#!/usr/bin/env python3
"""
Firefox File Repository
Concrete implementation for reading/writing Firefox preference files
"""

import logging
import shutil
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from hardzilla.domain.repositories import IFirefoxRepository
from hardzilla.domain.enums import SettingLevel
from hardzilla.infrastructure.parsers import PrefsParser

logger = logging.getLogger(__name__)


class FirefoxFileRepository(IFirefoxRepository):
    """
    Repository for interacting with Firefox profile files.

    Handles:
    - Reading prefs.js and user.js files
    - Writing with backup creation
    - Merging BASE settings into existing prefs.js
    - Replacing ADVANCED settings in user.js
    """

    def __init__(self, parser: PrefsParser = None):
        """
        Initialize repository.

        Args:
            parser: Optional PrefsParser instance (creates new if None)
        """
        self.parser = parser or PrefsParser()

    def read_prefs(self, profile_path: Path, level: SettingLevel) -> Dict[str, Any]:
        """Read preferences from Firefox profile"""
        pref_file = profile_path / level.filename

        if not pref_file.exists():
            logger.warning(f"{level.filename} not found in profile, returning empty dict")
            return {}

        return self.parser.parse_file(pref_file)

    def write_prefs(
        self,
        profile_path: Path,
        prefs: Dict[str, Any],
        level: SettingLevel,
        merge: bool = False
    ) -> None:
        """Write preferences to Firefox profile"""
        pref_file = profile_path / level.filename

        # Validate profile path
        if not self.validate_profile_path(profile_path):
            raise ValueError(f"Invalid Firefox profile path: {profile_path}")

        # FIX [HIGH-001]: Read file first, then backup from that snapshot
        # This prevents race condition where file changes between backup and merge
        existing_prefs = {}
        if pref_file.exists():
            # Read existing content into memory first
            existing_prefs = self.parser.parse_file(pref_file)
            # Create backup from the snapshot we just read
            self.backup(profile_path, level)

        # Handle merge for BASE settings
        if merge and level == SettingLevel.BASE and existing_prefs:
            # Merge with the snapshot we read earlier (not re-reading file)
            merged_prefs = self.parser.merge_prefs(existing_prefs, prefs)
            self.parser.write_prefs(
                merged_prefs,
                pref_file,
                use_user_pref=(level == SettingLevel.BASE)
            )
            logger.info(f"Merged {len(prefs)} prefs into {pref_file.name}")
        else:
            # Replace file entirely (typical for ADVANCED/user.js)
            self.parser.write_prefs(
                prefs,
                pref_file,
                use_user_pref=(level == SettingLevel.BASE)
            )
            logger.info(f"Wrote {len(prefs)} prefs to {pref_file.name}")

    def backup(self, profile_path: Path, level: SettingLevel) -> Path:
        """Create a timestamped backup of preference file"""
        pref_file = profile_path / level.filename

        if not pref_file.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {pref_file}")

        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = profile_path / f"{level.filename}.backup_{timestamp}"

        shutil.copy2(pref_file, backup_file)
        logger.info(f"Created backup: {backup_file.name}")

        # Rotate old backups (keep last 5)
        self._rotate_backups(profile_path, level.filename, max_backups=5)

        return backup_file

    def _rotate_backups(self, directory: Path, filename: str, max_backups: int = 5) -> None:
        """
        Remove old backup files, keeping only the most recent ones.

        Args:
            directory: Directory containing backup files
            filename: Base filename (e.g. 'prefs.js' or 'user.js')
            max_backups: Maximum number of backups to keep
        """
        try:
            backup_files = sorted(
                directory.glob(f"{filename}.backup_*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_backup in backup_files[max_backups:]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup.name}")
        except Exception as e:
            logger.error(f"Failed to rotate backups: {e}")

    def validate_profile_path(self, profile_path: Path) -> bool:
        """
        Validate that path is a Firefox profile directory.

        Checks for existence of profile markers:
        - prefs.js (Firefox profile marker)
        - Or times.json (alternative marker)
        """
        if not profile_path.exists() or not profile_path.is_dir():
            return False

        # Check for Firefox profile markers
        has_prefs = (profile_path / "prefs.js").exists()
        has_times = (profile_path / "times.json").exists()

        return has_prefs or has_times
