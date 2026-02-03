#!/usr/bin/env python3
"""
Setting to Pref Mapper
Converts Setting entities to Firefox preference format
"""

from typing import Dict, Any, List
from hardzilla.domain.entities import Setting


class SettingToPrefMapper:
    """Maps Setting entities to Firefox preference dictionaries"""

    def map(self, setting: Setting) -> tuple[str, Any]:
        """
        Convert a Setting to Firefox preference key-value pair.

        Args:
            setting: Setting entity to convert

        Returns:
            Tuple of (pref_key, pref_value)
        """
        return (setting.key, setting.value)

    def map_many(self, settings: List[Setting]) -> Dict[str, Any]:
        """
        Convert multiple Settings to Firefox preference dictionary.

        Args:
            settings: List of Setting entities

        Returns:
            Dictionary of pref_key -> pref_value
        """
        prefs = {}
        for setting in settings:
            key, value = self.map(setting)
            prefs[key] = value
        return prefs

    def map_profile_settings(self, settings: Dict[str, Setting]) -> Dict[str, Any]:
        """
        Convert profile settings dictionary to Firefox prefs.

        Args:
            settings: Dictionary of setting_key -> Setting entity

        Returns:
            Dictionary of pref_key -> pref_value
        """
        return {
            setting.key: setting.value
            for setting in settings.values()
        }
