#!/usr/bin/env python3
"""
Settings ViewModel
Unified state management for the Settings tab (merged Setup + Customize + Apply).
"""

from pathlib import Path
from typing import Dict, List, Optional
from .base_view_model import BaseViewModel
from hardfox.domain.entities import Setting, Profile
from hardfox.domain.enums import SettingLevel


class SettingsViewModel(BaseViewModel):
    """
    ViewModel for the unified Settings tab.

    Combines state from the former Setup, Customize, and Apply ViewModels:
    - Firefox path and import state (from Setup)
    - Settings editing, search, filters (from Customize)
    - Apply mode, save-to-JSON, apply status (from Apply)
    """

    def __init__(self, settings_repo=None):
        """
        Initialize settings view model.

        Args:
            settings_repo: Repository to load all available settings
        """
        super().__init__()

        # Load all settings from metadata
        all_settings = settings_repo.get_all() if settings_repo else {}

        self._properties = {
            # --- From SetupVM ---
            'firefox_path': '',
            'selected_preset': None,

            # --- From CustomizeVM ---
            'profile': None,
            'settings': all_settings.copy(),
            'base_settings': all_settings,
            'modified_settings': set(),
            'search_query': '',
            'selected_category': None,
            'show_advanced': False,
            'modification_count': 0,

            # --- From ApplyVM (settings-apply portion) ---
            'apply_mode': 'BOTH',
            'save_to_json': False,
            'json_save_path': '',
            'is_applying': False,
            'apply_success': False,
            'apply_error_message': '',
            'base_count': 0,
            'advanced_count': 0,
            'applied_base_count': 0,
            'applied_advanced_count': 0,
        }

    # =================================================================
    # Firefox Path
    # =================================================================

    @property
    def firefox_path(self) -> str:
        return self.get_property('firefox_path', '')

    @firefox_path.setter
    def firefox_path(self, value: str):
        self.set_property('firefox_path', value)

    # =================================================================
    # Selected Preset
    # =================================================================

    @property
    def selected_preset(self) -> Optional[str]:
        return self.get_property('selected_preset')

    @selected_preset.setter
    def selected_preset(self, value: Optional[str]):
        self.set_property('selected_preset', value)

    # =================================================================
    # Profile & Settings (from CustomizeVM)
    # =================================================================

    @property
    def profile(self) -> Optional[Profile]:
        return self.get_property('profile')

    @profile.setter
    def profile(self, value: Optional[Profile]):
        """
        Set profile and UPDATE setting values (not replace).

        When a preset is selected or Firefox profile is imported,
        this updates the values of the settings without replacing
        the entire settings dictionary.
        """
        self.set_property('profile', value)
        if value:
            current_settings = self._properties['settings']
            for key, profile_setting in value.settings.items():
                current_settings[key] = profile_setting

            # Update counts
            self.set_property('base_count', value.get_base_settings_count())
            self.set_property('advanced_count', value.get_advanced_settings_count())

            self._notify('settings', self._properties['settings'])

    @property
    def settings(self) -> Dict[str, Setting]:
        return self.get_property('settings', {})

    def get_setting(self, key: str) -> Optional[Setting]:
        return self.settings.get(key)

    def update_setting_value(self, key: str, new_value) -> None:
        """Update a setting value and mark as modified."""
        if key in self.settings:
            setting = self.settings[key]
            updated_setting = setting.clone_with_value(new_value)
            self._properties['settings'][key] = updated_setting

            modified = self.get_property('modified_settings', set())
            modified.add(key)
            self.set_property('modified_settings', modified)
            self.set_property('modification_count', len(modified))

            self._notify('settings', self._properties['settings'])

    def reset_setting(self, key: str) -> None:
        """Reset a setting to its original value."""
        if self.profile and key in self.profile.settings:
            original = self.profile.settings[key]
            self._properties['settings'][key] = original

            modified = self.get_property('modified_settings', set())
            modified.discard(key)
            self.set_property('modified_settings', modified)
            self.set_property('modification_count', len(modified))

            self._notify('settings', self._properties['settings'])

    def reset_all(self) -> None:
        """Reset all settings to current profile values (or defaults if no profile)."""
        if self.profile:
            current_settings = self._properties['settings']
            for key, profile_setting in self.profile.settings.items():
                if key in current_settings:
                    current_settings[key] = profile_setting
        else:
            self._properties['settings'] = self._properties['base_settings'].copy()

        self.set_property('modified_settings', set())
        self.set_property('modification_count', 0)
        self._notify('settings', self._properties['settings'])

    # Search & Filters

    @property
    def search_query(self) -> str:
        return self.get_property('search_query', '')

    @search_query.setter
    def search_query(self, value: str):
        self.set_property('search_query', value)

    def get_filtered_settings(self) -> Dict[str, Setting]:
        """Get settings filtered by search query."""
        query = self.search_query.lower()
        if not query:
            return self.settings

        return {
            key: setting
            for key, setting in self.settings.items()
            if (query in key.lower() or
                query in setting.description.lower() or
                query in setting.category.lower())
        }

    @property
    def selected_category(self) -> Optional[str]:
        return self.get_property('selected_category')

    @selected_category.setter
    def selected_category(self, value: Optional[str]):
        self.set_property('selected_category', value)

    def get_settings_by_category(self, category: str) -> List[Setting]:
        return [
            setting
            for setting in self.settings.values()
            if setting.category == category
        ]

    @property
    def show_advanced(self) -> bool:
        return self.get_property('show_advanced', False)

    @show_advanced.setter
    def show_advanced(self, value: bool):
        self.set_property('show_advanced', value)

    @property
    def modification_count(self) -> int:
        return self.get_property('modification_count', 0)

    @property
    def has_modifications(self) -> bool:
        return self.modification_count > 0

    # =================================================================
    # Apply Settings (from ApplyVM)
    # =================================================================

    @property
    def apply_mode(self) -> str:
        return self.get_property('apply_mode', 'BOTH')

    @apply_mode.setter
    def apply_mode(self, value: str):
        if value in ['BASE', 'ADVANCED', 'BOTH']:
            self.set_property('apply_mode', value)

    def get_apply_level(self) -> Optional[SettingLevel]:
        if self.apply_mode == 'BASE':
            return SettingLevel.BASE
        elif self.apply_mode == 'ADVANCED':
            return SettingLevel.ADVANCED
        else:
            return None

    @property
    def save_to_json(self) -> bool:
        return self.get_property('save_to_json', False)

    @save_to_json.setter
    def save_to_json(self, value: bool):
        self.set_property('save_to_json', value)

    @property
    def json_save_path(self) -> str:
        return self.get_property('json_save_path', '')

    @json_save_path.setter
    def json_save_path(self, value: str):
        self.set_property('json_save_path', value)

    @property
    def is_applying(self) -> bool:
        return self.get_property('is_applying', False)

    @is_applying.setter
    def is_applying(self, value: bool):
        self.set_property('is_applying', value)

    @property
    def apply_success(self) -> bool:
        return self.get_property('apply_success', False)

    @apply_success.setter
    def apply_success(self, value: bool):
        self.set_property('apply_success', value)

    @property
    def apply_error_message(self) -> str:
        return self.get_property('apply_error_message', '')

    @apply_error_message.setter
    def apply_error_message(self, value: str):
        self.set_property('apply_error_message', value)

    @property
    def base_count(self) -> int:
        return self.get_property('base_count', 0)

    @property
    def advanced_count(self) -> int:
        return self.get_property('advanced_count', 0)

    @property
    def applied_base_count(self) -> int:
        return self.get_property('applied_base_count', 0)

    @applied_base_count.setter
    def applied_base_count(self, value: int):
        self.set_property('applied_base_count', value)

    @property
    def applied_advanced_count(self) -> int:
        return self.get_property('applied_advanced_count', 0)

    @applied_advanced_count.setter
    def applied_advanced_count(self, value: int):
        self.set_property('applied_advanced_count', value)

    def set_apply_results(self, results: Dict[str, int]) -> None:
        """Set results from apply use case."""
        self.applied_base_count = results.get('base_applied', 0)
        self.applied_advanced_count = results.get('advanced_applied', 0)

    # =================================================================
    # Computed: generate Profile on-demand from current settings
    # =================================================================

    def build_profile(self) -> Optional[Profile]:
        """Build a Profile from the current settings state."""
        if not self.settings:
            return None

        profile_name = self.profile.name if self.profile else "Custom Configuration"
        return Profile(
            name=profile_name,
            settings=self.settings.copy(),
            metadata={},
            generated_by="user_customization"
        )
