#!/usr/bin/env python3
"""
JSON Profile Repository
Concrete implementation for saving/loading profiles as JSON files
"""

import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from hardzilla.domain.repositories import IProfileRepository, ISettingsRepository
from hardzilla.domain.entities import Profile

logger = logging.getLogger(__name__)


class JsonProfileRepository(IProfileRepository):
    """
    Repository for managing profiles as JSON files.

    Features:
    - Atomic writes (write to temp file, then move)
    - Timestamped profiles
    - Default profiles directory
    """

    def __init__(
        self,
        profiles_dir: Path,
        settings_repo: ISettingsRepository
    ):
        """
        Initialize repository.

        Args:
            profiles_dir: Directory to store profile JSON files
            settings_repo: Settings repository for metadata
        """
        self.profiles_dir = profiles_dir
        self.settings_repo = settings_repo

        # Create profiles directory if it doesn't exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def save(self, profile: Profile, path: Optional[Path] = None) -> None:
        """Save profile to JSON file"""
        if path is None:
            # Generate filename from profile name
            path = self._sanitize_profile_path(profile.name)

        # Serialize profile
        data = profile.to_dict()

        # Write atomically (temp file + move)
        temp_path = path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic move
            temp_path.replace(path)
            logger.info(f"Saved profile '{profile.name}' to {path.name}")
        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to save profile: {e}")

    def load(self, name_or_path: str) -> Profile:
        """Load profile from JSON file"""
        # Try as direct path first
        path = Path(name_or_path)
        if not path.exists():
            # Try in profiles directory
            path = self._sanitize_profile_path(name_or_path)

        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {name_or_path}")

        # Load JSON
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct profile with metadata
        settings_metadata = self.settings_repo.get_all()
        profile = Profile.from_dict(data, settings_metadata)

        logger.info(f"Loaded profile '{profile.name}' from {path.name}")
        return profile

    def list_all(self) -> List[str]:
        """List all available profile names"""
        profiles = []
        for json_file in self.profiles_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profiles.append(data.get("name", json_file.stem))
            except Exception as e:
                logger.warning(f"Failed to read profile {json_file.name}: {e}")

        return sorted(profiles)

    def delete(self, name: str) -> bool:
        """Delete a profile file"""
        path = self._sanitize_profile_path(name)

        if path.exists():
            path.unlink()
            logger.info(f"Deleted profile '{name}'")
            return True

        return False

    def exists(self, name: str) -> bool:
        """Check if profile exists"""
        try:
            path = self._sanitize_profile_path(name)
            return path.exists()
        except ValueError:
            return False

    def _sanitize_profile_path(self, name: str) -> Path:
        """
        Sanitize profile name and ensure path stays within profiles directory.

        Args:
            name: Profile name to sanitize

        Returns:
            Safe path within profiles_dir

        Raises:
            ValueError: If name would escape profiles directory
        """
        # FIX [HIGH-003]: Prevent path traversal attacks
        # Remove dangerous characters and patterns
        if '..' in name:
            raise ValueError(f"Profile name cannot contain '..': {name}")

        # Sanitize: remove/replace special characters
        safe_name = (name.lower()
                     .replace(' ', '_')
                     .replace('/', '_')
                     .replace('\\', '_')
                     .replace(':', '_')
                     .replace('*', '_')
                     .replace('?', '_')
                     .replace('"', '_')
                     .replace('<', '_')
                     .replace('>', '_')
                     .replace('|', '_'))

        # Build path
        path = self.profiles_dir / f"{safe_name}.json"

        # Verify path is actually inside profiles_dir
        resolved_path = path.resolve()
        resolved_dir = self.profiles_dir.resolve()

        if not resolved_path.is_relative_to(resolved_dir):
            raise ValueError(
                f"Profile path would escape profiles directory: {name} -> {resolved_path}"
            )

        return path
