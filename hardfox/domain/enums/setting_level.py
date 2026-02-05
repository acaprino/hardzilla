#!/usr/bin/env python3
"""
Setting Level Enumeration
Defines whether settings are applied to prefs.js (BASE) or user.js (ADVANCED)
"""

from enum import Enum, auto


class SettingLevel(Enum):
    """
    Controls where settings are applied in Firefox profile.

    BASE: Applied to prefs.js (user-configurable in Firefox UI)
    ADVANCED: Applied to user.js (locked, loaded on every startup)
    """
    BASE = "BASE"
    ADVANCED = "ADVANCED"

    def __str__(self) -> str:
        return self.value

    @property
    def filename(self) -> str:
        """Returns the Firefox filename for this level.

        Both BASE and ADVANCED settings are written to user.js because
        Firefox overwrites prefs.js on every shutdown, reverting changes.
        user.js is read-only from Firefox's perspective and applied on startup.
        """
        return "user.js"

    @property
    def prefix(self) -> str:
        """Returns the JavaScript function prefix for this level"""
        return "user_pref"
