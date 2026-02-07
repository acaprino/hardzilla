#!/usr/bin/env python3
"""
Load Preset Use Case
Business logic for loading preset profiles into Profile entities
"""

import logging
from typing import Dict, Any

from hardfox.domain.entities import Profile
from hardfox.domain.enums import SettingType
from hardfox.infrastructure.persistence import MetadataSettingsRepository
from hardfox.metadata.settings_metadata import PRESET_PROFILES, SETTINGS_METADATA, get_profile_settings

logger = logging.getLogger(__name__)


class LoadPresetUseCase:
    """
    Use case for loading a preset profile into a Profile entity.

    Takes a preset key (e.g., "privacy_enthusiast") and creates a complete
    Profile object with all settings configured according to the preset.
    """

    def __init__(self, settings_repo: MetadataSettingsRepository):
        """
        Initialize use case.

        Args:
            settings_repo: Repository for accessing settings metadata
        """
        self.settings_repo = settings_repo

    def execute(self, preset_key: str) -> Profile:
        """
        Load preset profile and create Profile entity.

        Args:
            preset_key: Key of preset to load (e.g., "privacy_enthusiast")

        Returns:
            Complete Profile with all settings configured

        Raises:
            ValueError: If preset_key is invalid
        """
        # Validate preset exists
        if preset_key not in PRESET_PROFILES:
            raise ValueError(
                f"Invalid preset key: '{preset_key}'. "
                f"Available presets: {list(PRESET_PROFILES.keys())}"
            )

        # Get preset metadata
        preset_data = PRESET_PROFILES[preset_key]

        # Get preset settings (all settings with recommended values for this preset)
        # These are keyed by metadata keys (e.g., 'disk_cache_enabled')
        preset_settings = get_profile_settings(preset_key)

        # Load all available settings metadata from repository
        # These are keyed by Firefox pref names (e.g., 'browser.cache.disk.enable')
        all_settings_by_pref = self.settings_repo.get_all()

        # Create Setting objects for each preset value
        settings_dict = {}
        for meta_key, value in preset_settings.items():
            # Map metadata key to Firefox pref key
            if meta_key in SETTINGS_METADATA:
                pref_key = SETTINGS_METADATA[meta_key].get('pref', meta_key)
                meta_data = SETTINGS_METADATA[meta_key]

                # Look up setting in repository using pref key
                if pref_key in all_settings_by_pref:
                    base_setting = all_settings_by_pref[pref_key]

                    # Map preset values to the format each setting type expects
                    mapped_value = value

                    # For toggles with non-boolean values, ensure preset value is actual Firefox value
                    if base_setting.setting_type == SettingType.TOGGLE and base_setting.toggle_values:
                        if isinstance(value, bool):
                            mapped_value = base_setting.toggle_values[0] if value else base_setting.toggle_values[1]

                    elif base_setting.setting_type == SettingType.DROPDOWN:
                        # Get values and labels from metadata
                        values_list = meta_data.get('values', [])
                        labels_list = meta_data.get('labels', [])

                        # If value is in values list, map to corresponding label
                        if value in values_list and len(labels_list) == len(values_list):
                            idx = values_list.index(value)
                            mapped_value = labels_list[idx]
                        elif value not in labels_list:
                            # Value doesn't match any label, keep the original value
                            # (Setting validation will handle the error)
                            logger.warning(
                                f"Dropdown value {value} for '{meta_key}' not found in values or labels"
                            )

                    # Clone the setting with the mapped value
                    try:
                        setting = base_setting.clone_with_value(mapped_value)
                        settings_dict[pref_key] = setting
                    except ValueError as e:
                        logger.warning(f"Failed to set value for '{meta_key}': {e}")
                else:
                    logger.debug(f"Pref '{pref_key}' (from '{meta_key}') not found in repository")
            else:
                logger.debug(f"Metadata key '{meta_key}' not found in SETTINGS_METADATA")

        # Create Profile
        profile = Profile(
            name=preset_data['name'],
            settings=settings_dict,
            metadata={
                'preset_key': preset_key,
                'description': preset_data.get('description', ''),
                'priority_profile': preset_data.get('priority_profile', 'balanced')
            },
            generated_by='preset'
        )

        logger.info(f"Loaded preset '{preset_data['name']}' with {len(settings_dict)} settings")

        return profile
