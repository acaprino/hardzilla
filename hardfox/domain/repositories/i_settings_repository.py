#!/usr/bin/env python3
"""
Settings Repository Interface
Abstract interface for accessing setting metadata
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from ..entities import Setting


class ISettingsRepository(ABC):
    """Repository for accessing setting metadata"""

    @abstractmethod
    def get_all(self) -> Dict[str, Setting]:
        """
        Get all available settings.

        Returns:
            Dictionary of setting key -> Setting entity
        """
        pass

    @abstractmethod
    def get_by_key(self, key: str) -> Optional[Setting]:
        """
        Get a setting by its key.

        Args:
            key: Setting key (e.g., "privacy.trackingprotection.enabled")

        Returns:
            Setting if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Setting]:
        """
        Get all settings in a category.

        Args:
            category: Category name

        Returns:
            List of settings in the category
        """
        pass

    @abstractmethod
    def get_by_level(self, level: str) -> List[Setting]:
        """
        Get all settings at a specific level.

        Args:
            level: "BASE" or "ADVANCED"

        Returns:
            List of settings at the level
        """
        pass
