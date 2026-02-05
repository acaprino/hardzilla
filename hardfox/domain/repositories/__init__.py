#!/usr/bin/env python3
"""Repository interfaces for Hardfox domain layer"""

from .i_settings_repository import ISettingsRepository
from .i_profile_repository import IProfileRepository
from .i_firefox_repository import IFirefoxRepository

__all__ = ['ISettingsRepository', 'IProfileRepository', 'IFirefoxRepository']
