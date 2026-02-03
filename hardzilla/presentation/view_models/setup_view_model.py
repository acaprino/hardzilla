#!/usr/bin/env python3
"""
Setup ViewModel
State management for Screen 1 (Intent & Setup)
"""

from pathlib import Path
from typing import Optional, List
from .base_view_model import BaseViewModel
from hardzilla.domain.entities import Profile


class SetupViewModel(BaseViewModel):
    """
    ViewModel for the Setup screen (Screen 1).

    Properties:
    - firefox_path: Path to Firefox profile directory
    - use_cases: List of selected use cases
    - privacy_level: Selected privacy level
    - breakage_tolerance: Tolerance slider value (0-100)
    - generated_profile: AI-generated profile recommendation
    - selected_preset: Manually selected preset (alternative to AI)
    - is_loading: Boolean indicating generation in progress
    """

    def __init__(self):
        """Initialize setup view model with default values"""
        super().__init__()

        # Initialize properties
        self._properties = {
            'firefox_path': '',
            'use_cases': [],
            'privacy_level': 'moderate',
            'breakage_tolerance': 50,
            'generated_profile': None,
            'selected_preset': None,
            'is_loading': False,
            'can_proceed': False
        }

    # Firefox Path
    @property
    def firefox_path(self) -> str:
        return self.get_property('firefox_path', '')

    @firefox_path.setter
    def firefox_path(self, value: str):
        self.set_property('firefox_path', value)
        self._update_can_proceed()

    # Use Cases
    @property
    def use_cases(self) -> List[str]:
        return self.get_property('use_cases', [])

    @use_cases.setter
    def use_cases(self, value: List[str]):
        self.set_property('use_cases', value)

    def toggle_use_case(self, use_case: str) -> None:
        """Toggle a use case in the selection"""
        current = self.use_cases.copy()
        if use_case in current:
            current.remove(use_case)
        else:
            current.append(use_case)
        self.use_cases = current

    # Privacy Level
    @property
    def privacy_level(self) -> str:
        return self.get_property('privacy_level', 'moderate')

    @privacy_level.setter
    def privacy_level(self, value: str):
        self.set_property('privacy_level', value)

    # Breakage Tolerance
    @property
    def breakage_tolerance(self) -> int:
        return self.get_property('breakage_tolerance', 50)

    @breakage_tolerance.setter
    def breakage_tolerance(self, value: int):
        self.set_property('breakage_tolerance', value)

    # Generated Profile
    @property
    def generated_profile(self) -> Optional[Profile]:
        return self.get_property('generated_profile')

    @generated_profile.setter
    def generated_profile(self, value: Optional[Profile]):
        self.set_property('generated_profile', value)
        self._update_can_proceed()

    # Selected Preset
    @property
    def selected_preset(self) -> Optional[str]:
        return self.get_property('selected_preset')

    @selected_preset.setter
    def selected_preset(self, value: Optional[str]):
        self.set_property('selected_preset', value)
        self._update_can_proceed()

    # Loading State
    @property
    def is_loading(self) -> bool:
        return self.get_property('is_loading', False)

    @is_loading.setter
    def is_loading(self, value: bool):
        self.set_property('is_loading', value)

    # Can Proceed (computed property)
    @property
    def can_proceed(self) -> bool:
        return self.get_property('can_proceed', False)

    def _update_can_proceed(self):
        """Update whether user can proceed to next screen"""
        has_firefox = bool(self.firefox_path)
        has_profile = self.generated_profile is not None or self.selected_preset is not None
        can_proceed = has_firefox and has_profile

        self.set_property('can_proceed', can_proceed)

    def reset(self):
        """Reset all values to defaults"""
        self.use_cases = []
        self.privacy_level = 'moderate'
        self.breakage_tolerance = 50
        self.generated_profile = None
        self.selected_preset = None
        self.is_loading = False
