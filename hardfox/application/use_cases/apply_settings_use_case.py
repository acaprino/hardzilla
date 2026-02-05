#!/usr/bin/env python3
"""
Apply Settings Use Case
Business logic for applying settings to a Firefox profile
"""

import logging
from typing import Dict
from pathlib import Path

from hardfox.domain.entities import Setting
from hardfox.domain.enums import SettingLevel
from hardfox.domain.repositories import IFirefoxRepository
from hardfox.application.mappers import SettingToPrefMapper

logger = logging.getLogger(__name__)


class ApplySettingsUseCase:
    """
    Use case for applying settings to a Firefox profile.

    All settings (BASE and ADVANCED) are written to user.js because
    Firefox overwrites prefs.js on every shutdown. user.js is read-only
    from Firefox's perspective and applied on every startup.
    """

    def __init__(
        self,
        firefox_repo: IFirefoxRepository,
        mapper: SettingToPrefMapper = None
    ):
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

        All settings are consolidated into a single user.js write to prevent
        overwrites between BASE and ADVANCED levels.

        Args:
            profile_path: Path to Firefox profile directory
            settings: Dictionary of setting_key -> Setting entity
            level: Which level to apply (BASE, ADVANCED, or None for BOTH)

        Returns:
            Dictionary with counts: {"base_applied": N, "advanced_applied": M}
        """
        if not self.firefox_repo.validate_profile_path(profile_path):
            raise ValueError(f"Invalid Firefox profile path: {profile_path}")

        # Collect all settings to apply, filtered by requested level
        base_settings = []
        advanced_settings = []

        for s in settings.values():
            if s.level == SettingLevel.BASE and (level is None or level == SettingLevel.BASE):
                base_settings.append(s)
            elif s.level == SettingLevel.ADVANCED and (level is None or level == SettingLevel.ADVANCED):
                advanced_settings.append(s)

        # Convert all settings to Firefox prefs
        all_prefs = {}
        if base_settings:
            all_prefs.update(self.mapper.map_many(base_settings))
        if advanced_settings:
            all_prefs.update(self.mapper.map_many(advanced_settings))

        if not all_prefs:
            logger.info("No settings to apply")
            return {"base_applied": 0, "advanced_applied": 0}

        # Single consolidated write to user.js (merge with existing)
        self.firefox_repo.write_prefs(
            profile_path=profile_path,
            prefs=all_prefs,
            level=SettingLevel.ADVANCED,  # Always user.js
            merge=True  # Merge with existing user.js prefs
        )

        results = {
            "base_applied": len(base_settings),
            "advanced_applied": len(advanced_settings)
        }

        logger.info(
            f"Applied {results['base_applied']} BASE and "
            f"{results['advanced_applied']} ADVANCED settings to user.js in {profile_path.name}"
        )

        return results
