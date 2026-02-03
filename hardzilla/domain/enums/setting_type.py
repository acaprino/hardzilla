#!/usr/bin/env python3
"""
Setting Type Enumeration
Defines UI control types for different settings
"""

from enum import Enum


class SettingType(Enum):
    """
    UI control types for settings in the customize screen.
    """
    TOGGLE = "toggle"           # Boolean checkbox
    SLIDER = "slider"           # Integer/numeric slider
    DROPDOWN = "dropdown"       # Dropdown select
    INPUT = "input"             # Text input field

    def __str__(self) -> str:
        return self.value
