#!/usr/bin/env python3
"""
Firefox Repository Interface
Abstract interface for reading/writing Firefox preference files
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
from ..enums import SettingLevel


class IFirefoxRepository(ABC):
    """Repository for interacting with Firefox profile files"""

    @abstractmethod
    def read_prefs(self, profile_path: Path, level: SettingLevel) -> Dict[str, Any]:
        """
        Read preferences from Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            level: Which file to read (BASE=prefs.js, ADVANCED=user.js)

        Returns:
            Dictionary of preference key -> value

        Raises:
            FileNotFoundError: If preference file doesn't exist
        """
        pass

    @abstractmethod
    def write_prefs(
        self,
        profile_path: Path,
        prefs: Dict[str, Any],
        level: SettingLevel,
        merge: bool = False
    ) -> None:
        """
        Write preferences to Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            prefs: Dictionary of preference key -> value
            level: Which file to write (BASE=prefs.js, ADVANCED=user.js)
            merge: If True, merge with existing prefs (BASE only)

        Raises:
            PermissionError: If can't write to profile
        """
        pass

    @abstractmethod
    def backup(self, profile_path: Path, level: SettingLevel) -> Path:
        """
        Create a backup of preference file.

        Args:
            profile_path: Path to Firefox profile directory
            level: Which file to backup

        Returns:
            Path to backup file

        Raises:
            FileNotFoundError: If preference file doesn't exist
        """
        pass

    @abstractmethod
    def validate_profile_path(self, profile_path: Path) -> bool:
        """
        Validate that path is a Firefox profile directory.

        Args:
            profile_path: Path to check

        Returns:
            True if valid Firefox profile, False otherwise
        """
        pass
