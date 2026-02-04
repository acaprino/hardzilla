#!/usr/bin/env python3
"""
Apply ViewModel
State management for Screen 4 (Apply Settings) and Screen 3 (Extensions)
"""

from pathlib import Path
from typing import Optional, Dict
from .base_view_model import BaseViewModel
from hardzilla.domain.entities import Profile
from hardzilla.domain.enums import SettingLevel


class ApplyViewModel(BaseViewModel):
    """
    ViewModel for Apply (Screen 4) and Extensions (Screen 3).

    Properties:
    - profile: Profile to apply
    - firefox_path: Path to Firefox profile directory
    - apply_mode: Which settings to apply (BASE, ADVANCED, or BOTH)
    - save_to_json: Whether to save profile as JSON
    - json_save_path: Path to save JSON file
    - is_applying: Boolean indicating apply in progress
    - apply_success: Boolean indicating successful application
    - apply_error_message: Error message if apply failed
    - extension_error_message: Error message if extension install failed
    """

    def __init__(self):
        """Initialize apply view model"""
        super().__init__()

        self._properties = {
            'profile': None,
            'firefox_path': '',
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
            # Extension-related properties
            'selected_extensions': [],
            'is_installing_extensions': False,
            'extension_install_success': False,
            'extension_install_results': {},
            'extension_error_message': ''
        }

    # Profile
    @property
    def profile(self) -> Optional[Profile]:
        return self.get_property('profile')

    @profile.setter
    def profile(self, value: Optional[Profile]):
        self.set_property('profile', value)
        if value:
            self.set_property('base_count', value.get_base_settings_count())
            self.set_property('advanced_count', value.get_advanced_settings_count())

    # Firefox Path
    @property
    def firefox_path(self) -> str:
        return self.get_property('firefox_path', '')

    @firefox_path.setter
    def firefox_path(self, value: str):
        self.set_property('firefox_path', value)

    # Apply Mode
    @property
    def apply_mode(self) -> str:
        return self.get_property('apply_mode', 'BOTH')

    @apply_mode.setter
    def apply_mode(self, value: str):
        """Set apply mode: 'BASE', 'ADVANCED', or 'BOTH'"""
        if value in ['BASE', 'ADVANCED', 'BOTH']:
            self.set_property('apply_mode', value)

    def get_apply_level(self) -> Optional[SettingLevel]:
        """Get SettingLevel enum from apply mode"""
        if self.apply_mode == 'BASE':
            return SettingLevel.BASE
        elif self.apply_mode == 'ADVANCED':
            return SettingLevel.ADVANCED
        else:  # BOTH
            return None

    # Save to JSON
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

    # Applying State
    @property
    def is_applying(self) -> bool:
        return self.get_property('is_applying', False)

    @is_applying.setter
    def is_applying(self, value: bool):
        self.set_property('is_applying', value)

    # Results
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
    def extension_error_message(self) -> str:
        return self.get_property('extension_error_message', '')

    @extension_error_message.setter
    def extension_error_message(self, value: str):
        self.set_property('extension_error_message', value)

    # Counts
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
        """Set results from apply use case"""
        self.applied_base_count = results.get('base_applied', 0)
        self.applied_advanced_count = results.get('advanced_applied', 0)

    # Extension properties
    @property
    def selected_extensions(self) -> list:
        return self.get_property('selected_extensions', [])

    @selected_extensions.setter
    def selected_extensions(self, value: list):
        self.set_property('selected_extensions', value)

    @property
    def is_installing_extensions(self) -> bool:
        return self.get_property('is_installing_extensions', False)

    @is_installing_extensions.setter
    def is_installing_extensions(self, value: bool):
        self.set_property('is_installing_extensions', value)

    @property
    def extension_install_success(self) -> bool:
        return self.get_property('extension_install_success', False)

    @extension_install_success.setter
    def extension_install_success(self, value: bool):
        self.set_property('extension_install_success', value)

    @property
    def extension_install_results(self) -> dict:
        return self.get_property('extension_install_results', {})

    @extension_install_results.setter
    def extension_install_results(self, value: dict):
        self.set_property('extension_install_results', value)
