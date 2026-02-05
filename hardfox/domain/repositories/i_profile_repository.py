#!/usr/bin/env python3
"""
Profile Repository Interface
Abstract interface for saving/loading profiles
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from ..entities import Profile


class IProfileRepository(ABC):
    """Repository for managing Firefox hardening profiles"""

    @abstractmethod
    def save(self, profile: Profile, path: Optional[Path] = None) -> None:
        """
        Save a profile to storage.

        Args:
            profile: Profile to save
            path: Optional custom path (defaults to profile name)
        """
        pass

    @abstractmethod
    def load(self, name_or_path: str) -> Profile:
        """
        Load a profile from storage.

        Args:
            name_or_path: Profile name or file path

        Returns:
            Loaded Profile

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """
        List all available profiles.

        Returns:
            List of profile names
        """
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """
        Delete a profile.

        Args:
            name: Profile name to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """
        Check if a profile exists.

        Args:
            name: Profile name to check

        Returns:
            True if exists, False otherwise
        """
        pass
