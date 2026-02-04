#!/usr/bin/env python3
"""
Utilities ViewModel
State management for the Utilities tab (Convert to Portable, etc.)
"""

from typing import Optional, Dict
from .base_view_model import BaseViewModel


class UtilitiesViewModel(BaseViewModel):
    """
    ViewModel for the Utilities tab.

    Properties:
    - firefox_install_dir: Detected Firefox installation path
    - destination_dir: User-selected destination directory
    - copy_profile: Whether to copy Firefox profile data
    - profile_path: Firefox profile path (synced from setup_vm)
    - is_converting: Whether conversion is in progress
    - conversion_progress: Float 0.0-1.0
    - conversion_status: Current step description
    - conversion_result: Dict with success/files_copied/size_mb/error
    - estimated_size_mb: Pre-conversion size estimate
    """

    def __init__(self):
        super().__init__()

        self._properties = {
            'firefox_install_dir': '',
            'destination_dir': '',
            'copy_profile': False,
            'profile_path': '',
            'is_converting': False,
            'conversion_progress': 0.0,
            'conversion_status': '',
            'conversion_result': None,
            'estimated_size_mb': 0.0,
        }

    # Firefox install directory
    @property
    def firefox_install_dir(self) -> str:
        return self.get_property('firefox_install_dir', '')

    @firefox_install_dir.setter
    def firefox_install_dir(self, value: str):
        self.set_property('firefox_install_dir', value)

    # Destination directory
    @property
    def destination_dir(self) -> str:
        return self.get_property('destination_dir', '')

    @destination_dir.setter
    def destination_dir(self, value: str):
        self.set_property('destination_dir', value)

    # Copy profile checkbox
    @property
    def copy_profile(self) -> bool:
        return self.get_property('copy_profile', False)

    @copy_profile.setter
    def copy_profile(self, value: bool):
        self.set_property('copy_profile', value)

    # Firefox profile path
    @property
    def profile_path(self) -> str:
        return self.get_property('profile_path', '')

    @profile_path.setter
    def profile_path(self, value: str):
        self.set_property('profile_path', value)

    # Converting state
    @property
    def is_converting(self) -> bool:
        return self.get_property('is_converting', False)

    @is_converting.setter
    def is_converting(self, value: bool):
        self.set_property('is_converting', value)

    # Progress (0.0 - 1.0)
    @property
    def conversion_progress(self) -> float:
        return self.get_property('conversion_progress', 0.0)

    @conversion_progress.setter
    def conversion_progress(self, value: float):
        self.set_property('conversion_progress', value)

    # Status text
    @property
    def conversion_status(self) -> str:
        return self.get_property('conversion_status', '')

    @conversion_status.setter
    def conversion_status(self, value: str):
        self.set_property('conversion_status', value)

    # Result dict
    @property
    def conversion_result(self) -> Optional[Dict]:
        return self.get_property('conversion_result', None)

    @conversion_result.setter
    def conversion_result(self, value: Optional[Dict]):
        # Always notify for result changes (even if values are identical)
        # to ensure the UI reacts to repeated conversions with same outcome.
        self._properties['conversion_result'] = value
        self._notify('conversion_result', value)

    # Estimated size
    @property
    def estimated_size_mb(self) -> float:
        return self.get_property('estimated_size_mb', 0.0)

    @estimated_size_mb.setter
    def estimated_size_mb(self, value: float):
        self.set_property('estimated_size_mb', value)
