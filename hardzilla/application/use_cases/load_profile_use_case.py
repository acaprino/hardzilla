#!/usr/bin/env python3
"""
Load Profile Use Case
Business logic for loading a saved profile
"""

import logging
from hardzilla.domain.entities import Profile
from hardzilla.domain.repositories import IProfileRepository

logger = logging.getLogger(__name__)


class LoadProfileUseCase:
    """Use case for loading a saved profile from storage"""

    def __init__(self, profile_repo: IProfileRepository):
        """
        Initialize use case.

        Args:
            profile_repo: Repository for profile persistence
        """
        self.profile_repo = profile_repo

    def execute(self, name_or_path: str) -> Profile:
        """
        Load a profile by name or path.

        Args:
            name_or_path: Profile name or file path

        Returns:
            Loaded Profile entity

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile = self.profile_repo.load(name_or_path)
        logger.info(f"Loaded profile '{profile.name}' with {len(profile.settings)} settings")
        return profile
