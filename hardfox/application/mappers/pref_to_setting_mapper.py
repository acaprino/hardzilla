#!/usr/bin/env python3
"""
Pref to Setting Mapper
Converts Firefox preferences to Setting entities
"""

import logging
from typing import Dict, Any, Optional
from hardfox.domain.entities import Setting
from hardfox.domain.repositories import ISettingsRepository

logger = logging.getLogger(__name__)


class PrefToSettingMapper:
    """Maps Firefox preferences to Setting entities"""

    def __init__(self, settings_repo: ISettingsRepository):
        """
        Initialize mapper.

        Args:
            settings_repo: Repository providing setting metadata
        """
        self.settings_repo = settings_repo

    def map(self, pref_key: str, pref_value: Any) -> Optional[Setting]:
        """
        Convert Firefox preference to Setting entity.

        Args:
            pref_key: Firefox preference key
            pref_value: Firefox preference value

        Returns:
            Setting entity if pref is known, None otherwise
        """
        from hardfox.domain.enums import SettingType

        # Get metadata for this preference
        metadata_setting = self.settings_repo.get_by_key(pref_key)

        if metadata_setting is None:
            logger.debug(f"Unknown preference '{pref_key}', skipping")
            return None

        # For dropdown settings, convert Firefox value to label
        if metadata_setting.setting_type == SettingType.DROPDOWN:
            # First, try to convert Firefox value (e.g., URL) to label
            normalized_value = metadata_setting.firefox_value_to_label(pref_value)

            # If still not in options, try case-insensitive matching
            if normalized_value not in metadata_setting.options:
                normalized_value = self._normalize_dropdown_value(
                    normalized_value,
                    metadata_setting.options,
                    metadata_setting.firefox_values
                )

            pref_value = normalized_value

        # Create new setting with imported value
        return metadata_setting.clone_with_value(pref_value)

    def _normalize_dropdown_value(self, value: Any, options: list, firefox_values: list = None) -> Any:
        """
        Normalize dropdown value to match available options.

        Handles multiple formats:
        - Exact match
        - Case-insensitive match
        - Partial match (e.g., 'Quad9' → 'Quad9 (9.9.9.9)')
        - Firefox value to label (if firefox_values provided)

        Args:
            value: The value to normalize
            options: List of valid options (labels)
            firefox_values: Optional list of Firefox values (parallel to options)

        Returns:
            Normalized value that matches one of the options, or original value if no match
        """
        if not isinstance(value, str) or not options:
            return value

        # Try exact match first
        if value in options:
            return value

        # Try case-insensitive match
        value_lower = value.lower()
        for option in options:
            if isinstance(option, str) and option.lower() == value_lower:
                return option

        # Try partial match (e.g., 'Quad9' matches 'Quad9 (9.9.9.9)')
        # This handles legacy formats without version numbers
        for option in options:
            if isinstance(option, str) and option.lower().startswith(value_lower):
                logger.info(f"Normalized legacy value '{value}' to '{option}'")
                return option

        # If firefox_values provided, check if value is a Firefox value
        if firefox_values and value in firefox_values:
            idx = firefox_values.index(value)
            if idx < len(options):
                logger.info(f"Converted Firefox value '{value}' to label '{options[idx]}'")
                return options[idx]

        # No match found, return original (will fail validation)
        logger.warning(f"Could not normalize dropdown value '{value}' to options {options}")
        return value

    def map_many(self, prefs: Dict[str, Any]) -> Dict[str, Setting]:
        """
        Convert multiple Firefox preferences to Settings.

        Args:
            prefs: Dictionary of pref_key -> pref_value

        Returns:
            Dictionary of pref_key -> Setting entity (only known prefs)
        """
        settings = {}

        for pref_key, pref_value in prefs.items():
            setting = self.map(pref_key, pref_value)
            if setting is not None:
                settings[pref_key] = setting

        logger.info(
            f"Mapped {len(settings)} known preferences out of {len(prefs)} total"
        )

        return settings
