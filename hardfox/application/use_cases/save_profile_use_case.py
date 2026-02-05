#!/usr/bin/env python3
"""
Save Profile Use Case
Business logic for saving a profile to storage
"""

import logging
from pathlib import Path
from typing import Optional

from hardfox.domain.entities import Profile
from hardfox.domain.repositories import IProfileRepository

logger = logging.getLogger(__name__)


class SaveProfileUseCase:
    """Use case for saving a profile to persistent storage"""

    def __init__(self, profile_repo: IProfileRepository):
        """
        Initialize use case.

        Args:
            profile_repo: Repository for profile persistence
        """
        self.profile_repo = profile_repo

    def execute(self, profile: Profile, path: Optional[Path] = None) -> None:
        """
        Save a profile.

        Args:
            profile: Profile to save
            path: Optional custom save path

        Raises:
            IOError: If save fails
        """
        self.profile_repo.save(profile, path)
        logger.info(f"Saved profile '{profile.name}' with {len(profile.settings)} settings")
