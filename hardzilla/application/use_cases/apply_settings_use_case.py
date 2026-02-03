#!/usr/bin/env python3
"""
Apply Settings Use Case
Business logic for applying settings to a Firefox profile
"""

import logging
from typing import Dict
from pathlib import Path

from hardzilla.domain.entities import Setting
from hardzilla.domain.enums import SettingLevel
from hardzilla.domain.repositories import IFirefoxRepository
from hardzilla.application.mappers import SettingToPrefMapper

logger = logging.getLogger(__name__)


class ApplySettingsUseCase:
    """
    Use case for applying settings to a Firefox profile.

    Responsibilities:
    - Filter settings by level (BASE/ADVANCED/BOTH)
    - Create backups before modification
    - Write to appropriate files (prefs.js/user.js)
    - Handle merge vs replace logic
    """

    def __init__(
        self,
        firefox_repo: IFirefoxRepository,
        mapper: SettingToPrefMapper = None
    ):
        """
        Initialize use case.

        Args:
            firefox_repo: Repository for Firefox file operations
            mapper: Mapper for Setting -> Pref conversion
        """
        self.firefox_repo = firefox_repo
        self.mapper = mapper or SettingToPrefMapper()

    def execute(
        self,
        profile_path: Path,
        settings: Dict[str, Setting],
        level: SettingLevel = None
    ) -> Dict[str, int]:
        """
        Apply settings to Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            settings: Dictionary of setting_key -> Setting entity
            level: Which level to apply (BASE, ADVANCED, or None for BOTH)

        Returns:
            Dictionary with counts: {"base_applied": N, "advanced_applied": M}

        Raises:
            ValueError: If profile path is invalid
            PermissionError: If can't write to profile
        """
        # Validate profile path
        if not self.firefox_repo.validate_profile_path(profile_path):
            raise ValueError(f"Invalid Firefox profile path: {profile_path}")

        results = {
            "base_applied": 0,
            "advanced_applied": 0
        }

        # Apply BASE settings if requested
        if level is None or level == SettingLevel.BASE:
            base_settings = [s for s in settings.values() if s.level == SettingLevel.BASE]
            if base_settings:
                results["base_applied"] = self._apply_level(
                    profile_path,
                    base_settings,
                    SettingLevel.BASE
                )

        # Apply ADVANCED settings if requested
        if level is None or level == SettingLevel.ADVANCED:
            advanced_settings = [s for s in settings.values() if s.level == SettingLevel.ADVANCED]
            if advanced_settings:
                results["advanced_applied"] = self._apply_level(
                    profile_path,
                    advanced_settings,
                    SettingLevel.ADVANCED
                )

        logger.info(
            f"Applied {results['base_applied']} BASE and "
            f"{results['advanced_applied']} ADVANCED settings to {profile_path.name}"
        )

        return results

    def _apply_level(
        self,
        profile_path: Path,
        settings: list[Setting],
        level: SettingLevel
    ) -> int:
        """
        Apply settings for a specific level.

        Args:
            profile_path: Path to Firefox profile
            settings: List of settings to apply
            level: Level to apply (BASE or ADVANCED)

        Returns:
            Number of settings applied
        """
        # Convert settings to prefs
        prefs = self.mapper.map_many(settings)

        if not prefs:
            logger.info(f"No {level} settings to apply")
            return 0

        # Write prefs
        # BASE: Merge with existing prefs.js
        # ADVANCED: Replace user.js entirely
        merge = (level == SettingLevel.BASE)

        self.firefox_repo.write_prefs(
            profile_path=profile_path,
            prefs=prefs,
            level=level,
            merge=merge
        )

        return len(prefs)
