#!/usr/bin/env python3
"""
Setting to Pref Mapper
Converts Setting entities to Firefox preference format
"""

import logging
from typing import Dict, Any, List
from hardfox.domain.entities import Setting
from hardfox.domain.enums import SettingType

logger = logging.getLogger(__name__)


class SettingToPrefMapper:
    """Maps Setting entities to Firefox preference dictionaries"""

    def map(self, setting: Setting) -> tuple[str, Any]:
        """
        Convert a Setting to Firefox preference key-value pair.

        For dropdown settings with separate labels and Firefox values,
        converts the label (UI value) to the actual Firefox preference value.
        E.g., 'Quad9 (9.9.9.9)' → 'https://dns.quad9.net/dns-query'

        Args:
            setting: Setting entity to convert

        Returns:
            Tuple of (pref_key, pref_value)
        """
        pref_value = setting.value

        # For toggles with non-boolean values, convert bool back to actual value
        # This catches edge cases like imported profiles with true/false
        if setting.setting_type == SettingType.TOGGLE and setting.toggle_values and isinstance(pref_value, bool):
            pref_value = setting.toggle_values[0] if pref_value else setting.toggle_values[1]
            logger.debug(f"Converted toggle bool {setting.value} to Firefox value {pref_value} for {setting.key}")

        # For dropdowns with firefox_values mapping, convert label to Firefox value
        if setting.setting_type == SettingType.DROPDOWN and setting.firefox_values:
            firefox_value = setting.label_to_firefox_value(setting.value)
            if firefox_value != setting.value:
                logger.debug(f"Converted label '{setting.value}' to Firefox value '{firefox_value}'")
                pref_value = firefox_value

        return (setting.key, pref_value)

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
        return self.map_many(list(settings.values()))
