#!/usr/bin/env python3
"""
Import From Firefox Use Case
Business logic for importing current Firefox settings
"""

import logging
from pathlib import Path
from datetime import datetime

from hardfox.domain.entities import Profile
from hardfox.domain.enums import SettingLevel
from hardfox.domain.repositories import IFirefoxRepository
from hardfox.application.mappers import PrefToSettingMapper

logger = logging.getLogger(__name__)


class ImportFromFirefoxUseCase:
    """Use case for importing settings from an existing Firefox profile"""

    def __init__(
        self,
        firefox_repo: IFirefoxRepository,
        mapper: PrefToSettingMapper
    ):
        """
        Initialize use case.

        Args:
            firefox_repo: Repository for Firefox file operations
            mapper: Mapper for Pref -> Setting conversion
        """
        self.firefox_repo = firefox_repo
        self.mapper = mapper

    def execute(self, profile_path: Path, profile_name: str = None) -> Profile:
        """
        Import settings from a Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            profile_name: Optional name for imported profile

        Returns:
            Profile entity with imported settings

        Raises:
            ValueError: If profile path is invalid
        """
        # Validate profile
        if not self.firefox_repo.validate_profile_path(profile_path):
            raise ValueError(f"Invalid Firefox profile path: {profile_path}")

        # Read BASE settings (prefs.js)
        base_prefs = self.firefox_repo.read_prefs(profile_path, SettingLevel.BASE)
        base_settings = self.mapper.map_many(base_prefs)

        # Read ADVANCED settings (user.js) if exists
        advanced_prefs = self.firefox_repo.read_prefs(profile_path, SettingLevel.ADVANCED)
        advanced_settings = self.mapper.map_many(advanced_prefs)

        # Combine all settings
        all_settings = {**base_settings, **advanced_settings}

        # Create profile
        if profile_name is None:
            profile_name = f"Imported from {profile_path.name}"

        profile = Profile(
            name=profile_name,
            settings=all_settings,
            metadata={
                "imported_from": str(profile_path),
                "imported_at": datetime.now().isoformat()
            },
            generated_by="import"
        )

        logger.info(
            f"Imported {len(base_settings)} BASE and {len(advanced_settings)} ADVANCED "
            f"settings from {profile_path.name}"
        )

        return profile
