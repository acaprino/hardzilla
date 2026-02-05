"""
Extension installation status enumeration.
"""
from enum import Enum


class InstallationStatus(Enum):
    """Status of extension installation."""
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    UNINSTALLED = "uninstalled"
    FAILED = "failed"
