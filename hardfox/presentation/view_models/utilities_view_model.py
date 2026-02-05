#!/usr/bin/env python3
"""
Utilities ViewModel
State management for the Utilities tab (Convert to Portable, Update Portable, etc.)
"""

from typing import Optional, Dict
from .base_view_model import BaseViewModel


class UtilitiesViewModel(BaseViewModel):
    """
    ViewModel for the Utilities tab.

    Properties (Convert to Portable):
    - firefox_install_dir: Detected Firefox installation path
    - destination_dir: User-selected destination directory
    - copy_profile: Whether to copy Firefox profile data
    - profile_path: Firefox profile path (synced from setup_vm)
    - is_converting: Whether conversion is in progress
    - conversion_progress: Float 0.0-1.0
    - conversion_status: Current step description
    - conversion_result: Dict with success/files_copied/size_mb/error
    - estimated_size_mb: Pre-conversion size estimate

    Properties (Update Portable Firefox):
    - portable_path: Path to portable Firefox root directory
    - current_version: Currently installed Firefox version
    - latest_version: Latest available Firefox version
    - update_available: Whether an update is available
    - is_checking_update: Whether an update check is in progress
    - is_updating: Whether an update is in progress
    - update_progress: Float 0.0-1.0
    - update_status: Current update step description
    - update_result: Dict with success/old_version/new_version/error

    Properties (Create Portable from Download):
    - create_channel: Selected download channel (stable/beta/devedition)
    - create_destination_dir: Destination directory for new portable
    - is_creating: Whether creation is in progress
    - create_progress: Float 0.0-1.0
    - create_status: Current creation step description
    - create_result: Dict with success/version/channel/size_mb/error
    """

    def __init__(self):
        super().__init__()

        self._properties = {
            # Convert to Portable
            'firefox_install_dir': '',
            'destination_dir': '',
            'copy_profile': False,
            'profile_path': '',
            'is_converting': False,
            'conversion_progress': 0.0,
            'conversion_status': '',
            'conversion_result': None,
            'estimated_size_mb': 0.0,
            # Update Portable Firefox
            'portable_path': '',
            'current_version': '',
            'latest_version': '',
            'update_available': False,
            'is_checking_update': False,
            'is_updating': False,
            'update_progress': 0.0,
            'update_status': '',
            'update_result': None,
            # Create Portable from Download
            'create_channel': 'stable',
            'create_destination_dir': '',
            'is_creating': False,
            'create_progress': 0.0,
            'create_status': '',
            'create_result': None,
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

    # --- Update Portable Firefox properties ---

    @property
    def portable_path(self) -> str:
        return self.get_property('portable_path', '')

    @portable_path.setter
    def portable_path(self, value: str):
        self.set_property('portable_path', value)

    @property
    def current_version(self) -> str:
        return self.get_property('current_version', '')

    @current_version.setter
    def current_version(self, value: str):
        self.set_property('current_version', value)

    @property
    def latest_version(self) -> str:
        return self.get_property('latest_version', '')

    @latest_version.setter
    def latest_version(self, value: str):
        self.set_property('latest_version', value)

    @property
    def update_available(self) -> bool:
        return self.get_property('update_available', False)

    @update_available.setter
    def update_available(self, value: bool):
        self.set_property('update_available', value)

    @property
    def is_checking_update(self) -> bool:
        return self.get_property('is_checking_update', False)

    @is_checking_update.setter
    def is_checking_update(self, value: bool):
        self.set_property('is_checking_update', value)

    @property
    def is_updating(self) -> bool:
        return self.get_property('is_updating', False)

    @is_updating.setter
    def is_updating(self, value: bool):
        self.set_property('is_updating', value)

    @property
    def update_progress(self) -> float:
        return self.get_property('update_progress', 0.0)

    @update_progress.setter
    def update_progress(self, value: float):
        self.set_property('update_progress', value)

    @property
    def update_status(self) -> str:
        return self.get_property('update_status', '')

    @update_status.setter
    def update_status(self, value: str):
        self.set_property('update_status', value)

    @property
    def update_result(self) -> Optional[Dict]:
        return self.get_property('update_result', None)

    @update_result.setter
    def update_result(self, value: Optional[Dict]):
        # Always notify (same pattern as conversion_result)
        self._properties['update_result'] = value
        self._notify('update_result', value)

    # --- Create Portable from Download properties ---

    @property
    def create_channel(self) -> str:
        return self.get_property('create_channel', 'stable')

    @create_channel.setter
    def create_channel(self, value: str):
        self.set_property('create_channel', value)

    @property
    def create_destination_dir(self) -> str:
        return self.get_property('create_destination_dir', '')

    @create_destination_dir.setter
    def create_destination_dir(self, value: str):
        self.set_property('create_destination_dir', value)

    @property
    def is_creating(self) -> bool:
        return self.get_property('is_creating', False)

    @is_creating.setter
    def is_creating(self, value: bool):
        self.set_property('is_creating', value)

    @property
    def create_progress(self) -> float:
        return self.get_property('create_progress', 0.0)

    @create_progress.setter
    def create_progress(self, value: float):
        self.set_property('create_progress', value)

    @property
    def create_status(self) -> str:
        return self.get_property('create_status', '')

    @create_status.setter
    def create_status(self, value: str):
        self.set_property('create_status', value)

    @property
    def create_result(self) -> Optional[Dict]:
        return self.get_property('create_result', None)

    @create_result.setter
    def create_result(self, value: Optional[Dict]):
        # Always notify (same pattern as conversion_result)
        self._properties['create_result'] = value
        self._notify('create_result', value)
