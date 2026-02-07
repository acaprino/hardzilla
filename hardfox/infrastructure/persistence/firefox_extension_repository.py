"""
Firefox extension repository implementation using policies.json.
"""
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from hardfox.domain.repositories.i_extension_repository import IExtensionRepository
from hardfox.domain.enums.extension_status import InstallationStatus
from hardfox.metadata.extensions_metadata import EXTENSIONS_METADATA
from hardfox.infrastructure.persistence.firefox_detection import get_firefox_installation_dir

logger = logging.getLogger(__name__)


class FirefoxExtensionRepository(IExtensionRepository):
    """Manages Firefox extensions using Enterprise Policies (policies.json)."""

    def install_extensions(
        self,
        profile_path: Path,
        extension_ids: List[str]
    ) -> Dict[str, InstallationStatus]:
        """
        Install extensions to Firefox using policies.json.

        Creates or updates {firefox_installation}/distribution/policies.json
        with ExtensionSettings for the specified extensions.

        Args:
            profile_path: Path to Firefox profile directory
            extension_ids: List of extension IDs to install

        Returns:
            Dictionary mapping extension IDs to installation status
        """
        results = {}

        try:
            # Validate profile path
            if not profile_path.exists():
                logger.error(f"Profile path does not exist: {profile_path}")
                return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

            # Find Firefox installation directory
            firefox_dir = self._get_firefox_installation_dir(profile_path)
            if not firefox_dir:
                logger.error("Could not locate Firefox installation directory")
                return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

            # Create distribution directory if needed
            dist_dir = firefox_dir / "distribution"
            self._create_distribution_dir(dist_dir)

            # Check write permissions
            if not self._check_write_permission(dist_dir):
                raise PermissionError(
                    "Administrator privileges required to install extensions via Enterprise Policies. "
                    "Please run Hardfox as Administrator."
                )

            # Read existing policies
            policies_file = dist_dir / "policies.json"
            existing_policies = self._read_existing_policies(policies_file)

            # Backup existing policies if file exists
            if policies_file.exists():
                self._backup_policies(policies_file)

            # Build extension settings
            extension_settings = {}
            for ext_id in extension_ids:
                if ext_id not in EXTENSIONS_METADATA:
                    logger.warning(f"Unknown extension ID: {ext_id}")
                    results[ext_id] = InstallationStatus.FAILED
                    continue

                ext_data = EXTENSIONS_METADATA[ext_id]
                install_url = ext_data["install_url"]

                # Validate URL is from official Mozilla add-ons
                if not install_url.startswith("https://addons.mozilla.org/"):
                    logger.error(f"Rejected non-AMO install URL for {ext_id}: {install_url}")
                    results[ext_id] = InstallationStatus.FAILED
                    continue

                extension_settings[ext_id] = {
                    "installation_mode": "normal_installed",
                    "install_url": install_url
                }
                results[ext_id] = InstallationStatus.PENDING

            # Merge with existing policies
            merged_policies = self._merge_extension_policies(
                existing_policies,
                extension_settings
            )

            # Write updated policies.json
            with open(policies_file, 'w', encoding='utf-8') as f:
                json.dump(merged_policies, f, indent=2)

            # Mark all as INSTALLED only after successful file write
            for ext_id in results:
                results[ext_id] = InstallationStatus.INSTALLED

            logger.info(f"Successfully wrote policies.json with {len(extension_settings)} extensions")
            return results

        except Exception as e:
            logger.error(f"Failed to install extensions: {e}")
            return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

    def _get_firefox_installation_dir(self, profile_path: Path) -> Path:
        """
        Find Firefox installation directory from profile path.

        Delegates to shared firefox_detection module.

        Args:
            profile_path: Path to Firefox profile

        Returns:
            Path to Firefox installation directory, or None if not found
        """
        return get_firefox_installation_dir(profile_path)

    def _create_distribution_dir(self, dist_dir: Path) -> None:
        """
        Create distribution directory if it doesn't exist.

        Args:
            dist_dir: Path to distribution directory
        """
        if not dist_dir.exists():
            dist_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created distribution directory: {dist_dir}")

    def _check_write_permission(self, directory: Path) -> bool:
        """
        Check if we have write permission to a directory.

        Args:
            directory: Path to check

        Returns:
            True if writable, False otherwise
        """
        test_file = directory / ".hardfox_write_test"
        try:
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False

    def _read_existing_policies(self, policies_file: Path) -> dict:
        """
        Read existing policies.json file.

        Args:
            policies_file: Path to policies.json

        Returns:
            Existing policies dictionary, or empty dict if file doesn't exist
        """
        if not policies_file.exists():
            return {"policies": {}}

        try:
            with open(policies_file, 'r', encoding='utf-8') as f:
                policies = json.load(f)
                logger.info("Read existing policies.json")
                return policies
        except json.JSONDecodeError:
            logger.warning("Failed to parse existing policies.json, starting fresh")
            return {"policies": {}}
        except Exception as e:
            logger.error(f"Error reading policies.json: {e}")
            return {"policies": {}}

    def _backup_policies(self, policies_file: Path) -> None:
        """
        Create timestamped backup of policies.json and rotate old backups.

        Keeps only the last 5 backups to prevent accumulation.

        Args:
            policies_file: Path to policies.json
        """
        if not policies_file.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = policies_file.with_name(f"policies.json.backup.{timestamp}")

        try:
            shutil.copy2(policies_file, backup_file)
            logger.info(f"Created backup: {backup_file}")

            # Rotate old backups (keep last 5)
            self._rotate_backups(policies_file.parent, max_backups=5)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")

    def _rotate_backups(self, directory: Path, max_backups: int = 5) -> None:
        """
        Remove old backup files, keeping only the most recent ones.

        Args:
            directory: Directory containing backup files
            max_backups: Maximum number of backups to keep
        """
        try:
            # Find all backup files
            backup_files = sorted(
                directory.glob("policies.json.backup.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Remove old backups beyond max_backups
            for old_backup in backup_files[max_backups:]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Failed to rotate backups: {e}")

    def _merge_extension_policies(
        self,
        existing_policies: dict,
        new_extension_settings: dict
    ) -> dict:
        """
        Reconcile extension settings with existing policies.

        Installs selected extensions and blocks any previously-installed
        known extensions that were deselected. Unknown extensions (not in
        EXTENSIONS_METADATA) are left untouched.

        Args:
            existing_policies: Existing policies dictionary
            new_extension_settings: Extension settings for selected extensions

        Returns:
            Updated policies dictionary
        """
        # Ensure structure exists
        if "policies" not in existing_policies:
            existing_policies["policies"] = {}

        if "ExtensionSettings" not in existing_policies["policies"]:
            existing_policies["policies"]["ExtensionSettings"] = {}

        ext_settings = existing_policies["policies"]["ExtensionSettings"]

        # Block known extensions that were deselected and clean up their 3rdparty config
        third_party_exts = (
            existing_policies.get("policies", {})
            .get("3rdparty", {})
            .get("Extensions", {})
        )
        for ext_id in EXTENSIONS_METADATA:
            if ext_id not in new_extension_settings and ext_id in ext_settings:
                ext_settings[ext_id] = {"installation_mode": "blocked"}
                if ext_id in third_party_exts:
                    del third_party_exts[ext_id]
                logger.info(f"Blocked deselected extension: {ext_id}")

        # Install selected extensions (overrides any previous blocked state)
        ext_settings.update(new_extension_settings)

        # Add 3rdparty extension configurations (e.g., uBlock Origin filter lists)
        third_party_config = self._build_third_party_config(new_extension_settings)
        if third_party_config:
            if "3rdparty" not in existing_policies["policies"]:
                existing_policies["policies"]["3rdparty"] = {"Extensions": {}}
            if "Extensions" not in existing_policies["policies"]["3rdparty"]:
                existing_policies["policies"]["3rdparty"]["Extensions"] = {}
            existing_policies["policies"]["3rdparty"]["Extensions"].update(third_party_config)
            logger.info(f"Added 3rdparty config for {len(third_party_config)} extensions")

        logger.info(f"Merged {len(new_extension_settings)} extension settings")
        return existing_policies

    def _build_third_party_config(self, extension_settings: dict) -> dict:
        """
        Build 3rdparty extension configuration for extensions that support it.

        Currently supports:
        - uBlock Origin: builtin + custom filter lists via adminSettings + toOverwrite

        Uses a dual approach for maximum Firefox compatibility:

        1. adminSettings (JSON string) — reliable on Firefox because uBlock
           explicitly JSON.parse()s it. Sets selectedFilterLists to builtin +
           custom lists AND userSettings.importedLists to register URL-based
           lists as downloadable assets.

        2. toOverwrite (JSON object) — takes priority in uBlock's code and
           properly handles URL-based lists. Works on Chromium and may work
           on Firefox if managed storage types are preserved from policies.json.

        selectedFilterLists replaces the entire list. We include:
        - user-filters (so users can add their own rules)
        - builtin_filter_lists (uBO defaults + extras like quick-fixes, AdGuard URL tracking)
        - custom_filter_lists (Hagezi: DNS-level domain blocking)

        Args:
            extension_settings: Dictionary of extension IDs being installed

        Returns:
            Dictionary of 3rdparty configurations keyed by extension ID
        """
        config = {}

        for ext_id in extension_settings:
            if ext_id not in EXTENSIONS_METADATA:
                continue

            ext_data = EXTENSIONS_METADATA[ext_id]

            # uBlock Origin filter lists (dual adminSettings + toOverwrite)
            if ext_id == "uBlock0@raymondhill.net":
                builtin_lists = ext_data.get("builtin_filter_lists", [])
                custom_lists = ext_data.get("custom_filter_lists", [])
                if builtin_lists or custom_lists:
                    # user-filters + uBO builtins + external Hagezi lists
                    selected_lists = ["user-filters"] + list(builtin_lists) + list(custom_lists)
                    url_lists = [u for u in custom_lists if u.startswith("http")]
                    config[ext_id] = {
                        # Primary: adminSettings (Firefox-reliable, JSON string)
                        "adminSettings": json.dumps({
                            "selectedFilterLists": selected_lists,
                            "userSettings": {
                                "importedLists": url_lists,
                                "externalLists": "\n".join(url_lists),
                            }
                        }),
                        # Secondary: toOverwrite (Chromium, newer Firefox)
                        "toOverwrite": {
                            "filterLists": selected_lists
                        }
                    }
                    logger.info(
                        f"Configured uBlock Origin with {len(selected_lists)} filter lists "
                        f"({len(builtin_lists)} builtin, {len(custom_lists)} custom)"
                    )

        return config

    def uninstall_extensions(
        self,
        profile_path: Path,
        extension_ids: List[str]
    ) -> Dict[str, InstallationStatus]:
        """
        Uninstall extensions from Firefox by blocking them in policies.json.

        Sets installation_mode to "blocked" so Firefox actively removes the
        extensions on next startup. Also removes any 3rdparty config.

        Args:
            profile_path: Path to Firefox profile directory
            extension_ids: List of extension IDs to uninstall

        Returns:
            Dictionary mapping extension IDs to uninstallation status
        """
        try:
            if not profile_path.exists():
                logger.error(f"Profile path does not exist: {profile_path}")
                return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

            firefox_dir = self._get_firefox_installation_dir(profile_path)
            if not firefox_dir:
                logger.error("Could not locate Firefox installation directory")
                return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

            dist_dir = firefox_dir / "distribution"
            self._create_distribution_dir(dist_dir)
            policies_file = dist_dir / "policies.json"

            if not self._check_write_permission(dist_dir):
                raise PermissionError(
                    "Administrator privileges required to modify extensions via Enterprise Policies. "
                    "Please run Hardfox as Administrator."
                )

            existing_policies = self._read_existing_policies(policies_file)

            if policies_file.exists():
                self._backup_policies(policies_file)

            # Ensure ExtensionSettings exists
            if "policies" not in existing_policies:
                existing_policies["policies"] = {}
            if "ExtensionSettings" not in existing_policies["policies"]:
                existing_policies["policies"]["ExtensionSettings"] = {}

            ext_settings = existing_policies["policies"]["ExtensionSettings"]
            third_party_exts = (
                existing_policies.get("policies", {})
                .get("3rdparty", {})
                .get("Extensions", {})
            )

            results = {}
            for ext_id in extension_ids:
                # Set to "blocked" so Firefox actively removes the extension
                ext_settings[ext_id] = {
                    "installation_mode": "blocked"
                }
                # Remove any 3rdparty config for this extension
                if ext_id in third_party_exts:
                    del third_party_exts[ext_id]

                results[ext_id] = InstallationStatus.UNINSTALLED
                logger.info(f"Blocked extension in policies: {ext_id}")

            # Clean up empty 3rdparty structures
            if not third_party_exts:
                if "3rdparty" in existing_policies.get("policies", {}):
                    existing_policies["policies"]["3rdparty"].pop("Extensions", None)
                    if not existing_policies["policies"]["3rdparty"]:
                        existing_policies["policies"].pop("3rdparty", None)

            with open(policies_file, 'w', encoding='utf-8') as f:
                json.dump(existing_policies, f, indent=2)

            logger.info(f"Successfully updated policies.json, blocked {len(results)} extensions")
            return results

        except Exception as e:
            logger.error(f"Failed to uninstall extensions: {e}")
            return {ext_id: InstallationStatus.FAILED for ext_id in extension_ids}

    def get_installed_extensions(
        self,
        profile_path: Path
    ) -> List[str]:
        """
        Get list of known extension IDs currently in policies.json.

        Only returns IDs that are also present in EXTENSIONS_METADATA.

        Args:
            profile_path: Path to Firefox profile directory

        Returns:
            List of extension IDs installed via policies.json
        """
        try:
            if not profile_path.exists():
                logger.error(f"Profile path does not exist: {profile_path}")
                return []

            firefox_dir = self._get_firefox_installation_dir(profile_path)
            if not firefox_dir:
                logger.warning("Could not locate Firefox installation directory")
                return []

            policies_file = firefox_dir / "distribution" / "policies.json"
            existing_policies = self._read_existing_policies(policies_file)

            ext_settings = existing_policies.get("policies", {}).get("ExtensionSettings", {})
            installed = [
                ext_id for ext_id, cfg in ext_settings.items()
                if ext_id in EXTENSIONS_METADATA
                and cfg.get("installation_mode") != "blocked"
            ]
            logger.info(f"Found {len(installed)} known extensions in policies.json")
            return installed

        except Exception as e:
            logger.error(f"Failed to read installed extensions: {e}")
            return []
