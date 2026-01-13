"""
Hardzilla Profile Manager and Firefox Importer

This module provides functionality for managing custom Hardzilla profiles
and importing settings from existing Firefox installations.
"""

import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Module exports
__all__ = [
    'ProfileManager',
    'FirefoxImporter',
]

# Setup logging for this module
logger = logging.getLogger(__name__)


class ProfileManager:
    """Manages custom Hardzilla profiles stored as JSON files."""

    def __init__(self, profiles_dir: Path = None):
        """
        Initialize the ProfileManager.

        Args:
            profiles_dir: Directory for storing profiles. Defaults to ~/.hardzilla/profiles/
        """
        if profiles_dir is None:
            self.profiles_dir = Path.home() / ".hardzilla" / "profiles"
        else:
            self.profiles_dir = Path(profiles_dir)

        # Create directory if it doesn't exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> List[Dict]:
        """
        List all JSON profiles in the profiles directory.

        Returns:
            List of profile dicts with '_file' path added, sorted by modified date (newest first)
        """
        profiles = []

        for filepath in self.profiles_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                profile['_file'] = str(filepath)
                profiles.append(profile)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load profile {filepath}: {e}")
                continue

        # Sort by modified date (newest first)
        profiles.sort(
            key=lambda p: p.get('modified', p.get('created', '1970-01-01T00:00:00')),
            reverse=True
        )

        return profiles

    def save_profile(
        self,
        name: str,
        description: str,
        settings: Dict[str, Any],
        tags: List[str] = None,
        base: str = None
    ) -> Path:
        """
        Save a profile to a JSON file.

        Args:
            name: Profile name
            description: Profile description
            settings: Dictionary of Hardzilla settings
            tags: Optional list of tags for categorization
            base: Base preset name if applicable

        Returns:
            Path to the saved profile file
        """
        # Sanitize name for filename
        safe_name = self._sanitize_filename(name)
        filepath = self.profiles_dir / f"{safe_name}.json"

        # Check if profile already exists to preserve created date
        created = datetime.now().isoformat(timespec='seconds')
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                created = existing.get('created', created)
            except (json.JSONDecodeError, IOError) as e:
                logger.debug(f"Could not read existing profile for created date: {e}")

        # Create profile dict
        profile = {
            "name": name,
            "description": description,
            "tags": tags or [],
            "base": base,
            "created": created,
            "modified": datetime.now().isoformat(timespec='seconds'),
            "version": "3.0",
            "settings": settings
        }

        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        return filepath

    def load_profile(self, filepath: str) -> Dict[str, Any]:
        """
        Load a profile from a JSON file.

        Args:
            filepath: Path to the profile JSON file

        Returns:
            Profile dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete_profile(self, filepath: str) -> bool:
        """
        Delete a profile file.

        Args:
            filepath: Path to the profile JSON file

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            Path(filepath).unlink()
            return True
        except (IOError, OSError):
            return False

    def duplicate_profile(self, filepath: str, new_name: str) -> Path:
        """
        Duplicate a profile with a new name.

        Args:
            filepath: Path to the source profile
            new_name: Name for the duplicated profile

        Returns:
            Path to the new profile file
        """
        # Load the existing profile
        profile = self.load_profile(filepath)

        # Save with new name
        return self.save_profile(
            name=new_name,
            description=profile.get('description', ''),
            settings=profile.get('settings', {}),
            tags=profile.get('tags', []),
            base=profile.get('base')
        )

    def export_profile(self, filepath: str, export_path: str) -> bool:
        """
        Export a profile to an external location.

        Args:
            filepath: Path to the source profile
            export_path: Destination path for the export

        Returns:
            True if export was successful, False otherwise
        """
        try:
            shutil.copy2(filepath, export_path)
            return True
        except (IOError, OSError):
            return False

    def import_profile(self, import_path: str) -> Path:
        """
        Import a profile from an external file into the profiles directory.

        Args:
            import_path: Path to the profile file to import

        Returns:
            Path to the imported profile in the profiles directory
        """
        # Load the profile to validate and get the name
        with open(import_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        # Use the profile name for the filename
        name = profile.get('name', Path(import_path).stem)
        safe_name = self._sanitize_filename(name)
        dest_path = self.profiles_dir / f"{safe_name}.json"

        # Update modified date on import
        profile['modified'] = datetime.now().isoformat(timespec='seconds')

        # Save to profiles directory
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        return dest_path

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a profile name for use as a filename.

        Prevents path traversal attacks and ensures safe filenames.

        Args:
            name: Original profile name

        Returns:
            Sanitized filename (without extension)
        """
        # Remove null bytes and control characters first (security)
        safe = re.sub(r'[\x00-\x1f]', '', name)
        # Replace path separators and invalid characters with underscores
        safe = re.sub(r'[<>:"/\\|?*]', '_', safe)
        # Replace multiple spaces/underscores with single underscore
        safe = re.sub(r'[\s_]+', '_', safe)
        # Remove leading/trailing underscores, spaces, and dots (prevent hidden files)
        safe = safe.strip('_ .')
        # Limit length
        safe = safe[:100] if len(safe) > 100 else safe
        # Default name if empty
        safe = safe or "unnamed_profile"

        # Final security check - ensure no path traversal components remain
        # os.path.basename should return the same string if no path separators
        if os.path.basename(safe) != safe or safe in ('.', '..'):
            logger.warning(f"Path traversal attempt detected in profile name: {name}")
            safe = "unnamed_profile"

        return safe


class FirefoxImporter:
    """Imports settings from existing Firefox prefs.js/user.js files."""

    # Map Firefox pref names to Hardzilla setting keys
    PREF_MAP = {
        # Session/Startup
        'browser.startup.page': 'restore_session',
        'browser.startup.homepage': 'homepage',

        # Cache settings
        'browser.cache.disk.enable': 'disk_cache_enabled',
        'browser.cache.disk.capacity': 'disk_cache_size',
        'browser.cache.memory.enable': 'memory_cache_enabled',
        'browser.cache.memory.capacity': 'memory_cache_size',

        # Performance
        'dom.ipc.processCount': 'content_processes',
        'gfx.webrender.all': 'webrender_enabled',
        'layers.acceleration.force-enabled': 'hardware_acceleration',
        'browser.preferences.defaultPerformanceSettings.enabled': 'default_performance',

        # Privacy - Cookies
        'network.cookie.cookieBehavior': 'third_party_cookies',
        'network.cookie.lifetimePolicy': 'cookie_lifetime',

        # Privacy - DNS
        'network.trr.mode': 'dns_over_https',
        'network.trr.uri': 'doh_provider',

        # Privacy - Tracking Protection
        'privacy.trackingprotection.enabled': 'tracking_protection',
        'privacy.trackingprotection.fingerprinting.enabled': 'fingerprint_resist',
        'privacy.trackingprotection.cryptomining.enabled': 'cryptomining_protection',
        'privacy.trackingprotection.socialtracking.enabled': 'social_tracking_protection',

        # Privacy - Fingerprinting
        'privacy.resistFingerprinting': 'resist_fingerprinting',
        'privacy.resistFingerprinting.letterboxing': 'letterboxing',

        # Privacy - Other
        'privacy.donottrackheader.enabled': 'do_not_track',
        'privacy.globalprivacycontrol.enabled': 'global_privacy_control',
        'privacy.firstparty.isolate': 'first_party_isolate',

        # Security
        'security.ssl.require_safe_negotiation': 'safe_negotiation',
        'security.OCSP.enabled': 'ocsp_enabled',
        'security.cert_pinning.enforcement_level': 'cert_pinning',
        'security.mixed_content.block_active_content': 'block_mixed_content',
        'security.mixed_content.block_display_content': 'block_mixed_display',

        # Network
        'network.prefetch-next': 'link_prefetch',
        'network.dns.disablePrefetch': 'dns_prefetch_disabled',
        'network.predictor.enabled': 'predictor_enabled',
        'network.http.speculative-parallel-limit': 'speculative_connections',

        # Tabs
        'browser.tabs.groups.enabled': 'tab_groups',
        'sidebar.verticalTabs': 'vertical_tabs',
        'browser.tabs.loadInBackground': 'load_tabs_background',
        'browser.tabs.warnOnClose': 'warn_on_close_tabs',
        'browser.tabs.closeWindowWithLastTab': 'close_window_with_last_tab',

        # UI/Features
        'browser.ml.enable': 'ml_enabled',
        'browser.search.suggest.enabled': 'search_suggestions',
        'browser.urlbar.suggest.searches': 'urlbar_suggestions',
        'browser.formfill.enable': 'form_autofill',
        'signon.rememberSignons': 'remember_passwords',
        'signon.autofillForms': 'autofill_passwords',

        # Media
        'media.autoplay.default': 'autoplay_default',
        'media.autoplay.blocking_policy': 'autoplay_blocking',
        'media.peerconnection.enabled': 'webrtc_enabled',
        'media.peerconnection.ice.default_address_only': 'webrtc_ip_leak',

        # Telemetry
        'toolkit.telemetry.enabled': 'telemetry_enabled',
        'datareporting.healthreport.uploadEnabled': 'health_report',
        'app.shield.optoutstudies.enabled': 'shield_studies',

        # Downloads
        'browser.download.useDownloadDir': 'use_download_dir',
        'browser.download.folderList': 'download_folder_list',
        'browser.download.manager.addToRecentDocs': 'add_to_recent_docs',

        # Developer
        'devtools.chrome.enabled': 'devtools_chrome',
        'devtools.debugger.remote-enabled': 'remote_debugging',
    }

    # Value transformations for special cases
    VALUE_TRANSFORMS = {
        'restore_session': lambda v: v == 3,  # 3 = restore session
        'third_party_cookies': lambda v: {
            0: 'all',
            1: 'none',
            3: 'visited',
            4: 'cross-site-only',
            5: 'cross-site'
        }.get(v, 'cross-site'),
        'dns_over_https': lambda v: {
            0: 'off',
            2: 'default',
            3: 'max',
            5: 'max'
        }.get(v, 'default'),
        'cookie_lifetime': lambda v: {
            0: 'normal',
            2: 'session'
        }.get(v, 'normal'),
        'autoplay_default': lambda v: {
            0: 'allow',
            1: 'block-audio',
            5: 'block-all'
        }.get(v, 'block-audio'),
        'cert_pinning': lambda v: {
            0: 'disabled',
            1: 'allow-user-cas',
            2: 'strict'
        }.get(v, 'allow-user-cas'),
        # Invert disabled flags
        'dns_prefetch_disabled': lambda v: not v,  # Convert disabled to enabled
    }

    def __init__(self, profile_path: Path):
        """
        Initialize the FirefoxImporter.

        Args:
            profile_path: Path to the Firefox profile directory
        """
        self.profile_path = Path(profile_path)
        self.prefs_file = self.profile_path / "prefs.js"
        self.userjs_file = self.profile_path / "user.js"

    def scan_preferences(self) -> Dict[str, Any]:
        """
        Parse prefs.js and user.js files.

        user.js takes precedence over prefs.js for duplicate keys.

        Returns:
            Dictionary of all found Firefox preferences
        """
        prefs = {}

        # Parse prefs.js first
        if self.prefs_file.exists():
            prefs.update(self._parse_prefs_file(self.prefs_file))

        # Parse user.js (takes precedence)
        if self.userjs_file.exists():
            prefs.update(self._parse_prefs_file(self.userjs_file))

        return prefs

    def _parse_prefs_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Parse a Firefox prefs.js or user.js file.

        Args:
            filepath: Path to the prefs file

        Returns:
            Dictionary of preference key-value pairs
        """
        prefs = {}

        # Regex to match user_pref("key", value);
        pref_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.+?)\);')

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for match in pref_pattern.finditer(content):
                key = match.group(1)
                value_str = match.group(2).strip()

                # Parse the value
                value = self._parse_value(value_str)
                prefs[key] = value

        except IOError as e:
            logger.warning(f"Failed to read Firefox prefs file {filepath}: {e}")

        return prefs

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a JavaScript value string to a Python value.

        Args:
            value_str: String representation of the value

        Returns:
            Parsed Python value
        """
        value_str = value_str.strip()

        # Boolean
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False

        # String (quoted)
        if value_str.startswith('"') and value_str.endswith('"'):
            # Unescape basic escape sequences
            return value_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')

        # Number (integer or float)
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Return as-is if nothing else matches
        return value_str

    def import_to_hardzilla(self) -> Dict[str, Any]:
        """
        Import Firefox preferences and map to Hardzilla settings.

        Returns:
            Dictionary of Hardzilla setting keys and their values
        """
        # Scan Firefox preferences
        firefox_prefs = self.scan_preferences()

        hardzilla_settings = {}

        for firefox_key, hardzilla_key in self.PREF_MAP.items():
            if firefox_key in firefox_prefs:
                value = firefox_prefs[firefox_key]

                # Apply transformation if available
                if hardzilla_key in self.VALUE_TRANSFORMS:
                    try:
                        value = self.VALUE_TRANSFORMS[hardzilla_key](value)
                    except (KeyError, TypeError):
                        # Keep original value if transform fails
                        pass

                hardzilla_settings[hardzilla_key] = value

        return hardzilla_settings

    def get_import_summary(self) -> Dict[str, int]:
        """
        Get a summary of the import statistics.

        Returns:
            Dictionary with:
                - total_firefox_prefs: Total preferences found in Firefox
                - recognized_by_hardzilla: Firefox prefs that have Hardzilla mappings
                - hardzilla_settings: Number of Hardzilla settings that can be imported
        """
        firefox_prefs = self.scan_preferences()
        hardzilla_settings = self.import_to_hardzilla()

        # Count recognized preferences
        recognized = sum(1 for key in firefox_prefs if key in self.PREF_MAP)

        return {
            'total_firefox_prefs': len(firefox_prefs),
            'recognized_by_hardzilla': recognized,
            'hardzilla_settings': len(hardzilla_settings)
        }


if __name__ == "__main__":
    # Basic module test
    print("Hardzilla Profile Manager module loaded successfully")

    # Test ProfileManager
    pm = ProfileManager()
    print(f"Profiles directory: {pm.profiles_dir}")
    print(f"Existing profiles: {len(pm.list_profiles())}")
