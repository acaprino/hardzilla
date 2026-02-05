#!/usr/bin/env python3
"""
Firefox Detection Utilities

Shared logic for detecting Firefox installation directories across platforms.
Used by FirefoxExtensionRepository and PortableConversionRepository.
"""

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def is_firefox_running() -> bool:
    """
    Check if Firefox is currently running.

    Returns:
        True if Firefox is running, False otherwise
    """
    system = platform.system()

    try:
        if system == "Windows":
            # Use tasklist to check for firefox.exe
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq firefox.exe", "/NH"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # tasklist returns "INFO: No tasks are running..." if not found
            # or the process info if found
            is_running = "firefox.exe" in result.stdout.lower()
            logger.debug(f"Firefox running check (Windows): {is_running}")
            return is_running

        elif system == "Linux":
            result = subprocess.run(
                ["pgrep", "-x", "firefox"],
                capture_output=True,
                timeout=5
            )
            is_running = result.returncode == 0
            logger.debug(f"Firefox running check (Linux): {is_running}")
            return is_running

        elif system == "Darwin":
            result = subprocess.run(
                ["pgrep", "-x", "firefox"],
                capture_output=True,
                timeout=5
            )
            is_running = result.returncode == 0
            logger.debug(f"Firefox running check (macOS): {is_running}")
            return is_running

        else:
            logger.warning(f"Cannot check Firefox process on platform: {system}")
            return False

    except subprocess.TimeoutExpired:
        logger.warning("Timeout checking if Firefox is running")
        return False
    except FileNotFoundError as e:
        logger.warning(f"Process check command not found: {e}")
        return False
    except Exception as e:
        logger.warning(f"Failed to check if Firefox is running: {e}")
        return False


def get_firefox_installation_dir(profile_path: Path = None) -> Optional[Path]:
    """
    Find Firefox installation directory.

    Checks common installation paths across platforms, detects Firefox Portable
    installations, and falls back to Windows registry lookup.

    Args:
        profile_path: Optional path to Firefox profile (used for Portable detection)

    Returns:
        Path to Firefox installation directory, or None if not found
    """
    system = platform.system()

    # Determine binary name by platform
    if system == "Windows":
        binary_name = "firefox.exe"
        portable_binary = "FirefoxPortable.exe"
    elif system == "Linux":
        binary_name = "firefox"
        portable_binary = None
    elif system == "Darwin":
        binary_name = "firefox"
        portable_binary = None
    else:
        logger.warning(f"Unsupported platform: {system}")
        return None

    # Check if profile is inside a Firefox Portable installation
    if system == "Windows" and profile_path and portable_binary:
        portable_dir = detect_firefox_portable(profile_path, portable_binary, binary_name)
        if portable_dir:
            logger.info(f"Found Firefox Portable installation at: {portable_dir}")
            return portable_dir

    # Common Firefox installation paths by platform
    if system == "Windows":
        common_paths = [
            Path("C:/Program Files/Mozilla Firefox"),
            Path("C:/Program Files (x86)/Mozilla Firefox"),
            Path(os.path.expandvars("%LOCALAPPDATA%/Mozilla Firefox")),
        ]
    elif system == "Linux":
        common_paths = [
            Path("/usr/lib/firefox"),
            Path("/usr/lib64/firefox"),
            Path("/opt/firefox"),
            Path("/snap/firefox/current/usr/lib/firefox"),
        ]
    elif system == "Darwin":
        common_paths = [
            Path("/Applications/Firefox.app/Contents/MacOS"),
        ]

    # Check common paths
    for path in common_paths:
        if path.exists() and (path / binary_name).exists():
            logger.info(f"Found Firefox installation at: {path}")
            return path

    # On Windows, try registry lookup as fallback
    if system == "Windows":
        registry_path = _lookup_firefox_registry()
        if registry_path:
            return registry_path

    logger.warning("Could not find Firefox installation directory")
    return None


def detect_firefox_portable(
    profile_path: Path,
    portable_binary: str,
    firefox_binary: str
) -> Optional[Path]:
    """
    Detect if the profile is inside a Firefox Portable installation.

    Firefox Portable structure:
    - FirefoxPortable/
      - FirefoxPortable.exe
      - App/Firefox64/firefox.exe (64-bit)
      - App/Firefox/firefox.exe (32-bit)
      - Data/profile/

    Args:
        profile_path: Path to Firefox profile
        portable_binary: Name of portable launcher (e.g., "FirefoxPortable.exe")
        firefox_binary: Name of Firefox binary (e.g., "firefox.exe")

    Returns:
        Path to Firefox installation directory, or None if not portable
    """
    current = profile_path.resolve()
    max_depth = 10

    for _ in range(max_depth):
        parent = current.parent
        if parent == current:
            break

        portable_exe = parent / portable_binary
        portable_bat = parent / "FirefoxPortable.bat"
        myfox_exe = parent / "MyFox.exe"
        if portable_exe.exists() or portable_bat.exists() or myfox_exe.exists():
            for firefox_dir_name in ["Firefox64", "Firefox"]:
                firefox_install = parent / "App" / firefox_dir_name
                if firefox_install.exists() and (firefox_install / firefox_binary).exists():
                    return firefox_install

        current = parent

    return None


def _lookup_firefox_registry() -> Optional[Path]:
    """Look up Firefox installation path from Windows registry."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Mozilla\Mozilla Firefox",
            0,
            winreg.KEY_READ
        ) as key:
            version_key_name = winreg.EnumKey(key, 0)
            with winreg.OpenKey(key, version_key_name + r"\Main") as version_key:
                install_dir = winreg.QueryValueEx(version_key, "Install Directory")[0]

        install_path = Path(install_dir)
        if install_path.exists() and (install_path / "firefox.exe").exists():
            logger.info(f"Found Firefox via registry at: {install_path}")
            return install_path
    except Exception as e:
        logger.debug(f"Registry lookup failed: {e}")

    return None
