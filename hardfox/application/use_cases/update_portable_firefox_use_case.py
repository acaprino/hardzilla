#!/usr/bin/env python3
"""
Update Portable Firefox Use Case

Orchestrates checking for updates and applying them to a portable
Firefox installation with atomic directory swap and rollback support.
"""

import logging
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class UpdatePortableFirefoxUseCase:
    """
    Use case for updating a portable Firefox installation.

    Flow:
    1. Validate portable structure
    2. Read current version from application.ini
    3. Query Mozilla API for latest version
    4. Compare versions
    5. Download installer to temp dir (with SHA-512 verification)
    6. Extract to App/Firefox64.new/
    7. Atomic swap: Firefox64 -> Firefox64.old, Firefox64.new -> Firefox64
    8. Remove Firefox64.old
    9. Update portable_metadata.json
    """

    def __init__(self, metadata_repo, download_repo):
        """
        Args:
            metadata_repo: PortableMetadataRepository instance
            download_repo: MozillaDownloadRepository instance
        """
        self.metadata_repo = metadata_repo
        self.download_repo = download_repo

    def check_for_update(self, portable_root: Path) -> Dict:
        """
        Check if an update is available for the portable Firefox installation.

        Args:
            portable_root: Root directory of portable Firefox

        Returns:
            Dict with keys: update_available, current_version, latest_version, error
        """
        result = {
            "update_available": False,
            "current_version": "",
            "latest_version": "",
            "error": None
        }

        try:
            # Validate portable structure
            error = self._validate_portable_root(portable_root)
            if error:
                result["error"] = error
                return result

            # Find Firefox directory
            firefox_dir = self.metadata_repo.find_firefox_dir(portable_root)
            if not firefox_dir:
                result["error"] = "Firefox directory not found in portable installation"
                return result

            # Read current version
            version_info = self.metadata_repo.read_version(firefox_dir)
            current = version_info.get("version", "")
            if not current:
                result["error"] = "Could not determine current Firefox version"
                return result
            result["current_version"] = current

            # Query latest version
            latest_info = self.download_repo.get_latest_version()
            latest = latest_info.get("version", "")
            if not latest:
                result["error"] = "Could not determine latest Firefox version"
                return result
            result["latest_version"] = latest

            # Compare
            result["update_available"] = self.metadata_repo.compare_versions(current, latest)

            if result["update_available"]:
                logger.info(f"Update available: {current} -> {latest}")
            else:
                logger.info(f"Firefox is up to date ({current})")

        except ConnectionError as e:
            result["error"] = str(e)
            logger.error(f"Update check failed: {e}")
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
            logger.error(f"Update check failed: {e}", exc_info=True)

        return result

    def execute(
        self,
        portable_root: Path,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Dict:
        """
        Execute the update process.

        Args:
            portable_root: Root directory of portable Firefox
            progress_cb: Progress callback(status, progress_0_to_1)
            cancel_event: Threading event for cancellation

        Returns:
            Dict with keys: success, old_version, new_version, already_up_to_date, error
        """
        result = {
            "success": False,
            "old_version": "",
            "new_version": "",
            "already_up_to_date": False,
            "error": None
        }

        temp_dir = None

        try:
            # Step 0: Validate portable structure
            error = self._validate_portable_root(portable_root)
            if error:
                result["error"] = error
                return result

            # Step 1: Find Firefox directory and read current version
            if progress_cb:
                progress_cb("Reading current version...", 0.0)

            firefox_dir = self.metadata_repo.find_firefox_dir(portable_root)
            if not firefox_dir:
                result["error"] = "Firefox directory not found in portable installation"
                return result

            # Determine the parent and folder name (e.g., App/Firefox64)
            firefox_parent = firefox_dir.parent
            firefox_name = firefox_dir.name

            version_info = self.metadata_repo.read_version(firefox_dir)
            old_version = version_info.get("version", "")
            if not old_version:
                result["error"] = "Could not determine current Firefox version"
                return result
            result["old_version"] = old_version

            # Step 2: Get latest version
            if progress_cb:
                progress_cb("Checking latest version...", 0.02)

            if cancel_event and cancel_event.is_set():
                result["error"] = "Update cancelled by user"
                return result

            latest_info = self.download_repo.get_latest_version()
            new_version = latest_info.get("version", "")
            if not new_version:
                result["error"] = "Could not determine latest Firefox version"
                return result
            result["new_version"] = new_version

            # Step 3: Compare versions
            if not self.metadata_repo.compare_versions(old_version, new_version):
                result["success"] = True
                result["already_up_to_date"] = True
                return result

            # Step 4: Download installer (with SHA-512 verification)
            if cancel_event and cancel_event.is_set():
                result["error"] = "Update cancelled by user"
                return result

            temp_dir = Path(tempfile.mkdtemp(prefix="hardfox_update_"))
            installer_path = self.download_repo.download_installer(
                version=new_version,
                dest_path=temp_dir,
                progress_cb=progress_cb,
                cancel_event=cancel_event
            )

            if cancel_event and cancel_event.is_set():
                result["error"] = "Update cancelled by user"
                return result

            # Step 5: Extract to Firefox64.new
            # Extraction handles nested dirs and post-extraction cancellation internally
            new_dir = firefox_parent / f"{firefox_name}.new"
            if new_dir.exists():
                shutil.rmtree(str(new_dir))

            self.download_repo.extract_installer(
                installer_path=installer_path,
                extract_dir=new_dir,
                progress_cb=progress_cb,
                cancel_event=cancel_event
            )

            # Step 6: Atomic swap
            if progress_cb:
                progress_cb("Replacing Firefox files...", 0.80)

            old_dir = firefox_parent / f"{firefox_name}.old"

            # Clean up any leftover from a previous failed update
            if old_dir.exists():
                shutil.rmtree(str(old_dir))

            try:
                # Rename current -> old
                firefox_dir.rename(old_dir)
            except OSError as e:
                # Restore new_dir cleanup
                shutil.rmtree(str(new_dir), ignore_errors=True)
                result["error"] = (
                    f"Failed to move current Firefox directory: {e}\n"
                    "Make sure Firefox is not running."
                )
                return result

            try:
                # Rename new -> current
                new_dir.rename(firefox_dir)
            except OSError as e:
                # Rollback: restore old -> current
                logger.error(f"Failed to place new Firefox, rolling back: {e}")
                try:
                    old_dir.rename(firefox_dir)
                except OSError as rollback_err:
                    logger.critical(f"Rollback also failed: {rollback_err}")
                    result["error"] = (
                        f"Critical: Update failed and rollback failed.\n"
                        f"Original files are at: {old_dir}\n"
                        f"Error: {e}"
                    )
                    return result
                result["error"] = f"Failed to place new Firefox files: {e}"
                return result

            # Step 7: Remove old directory
            if progress_cb:
                progress_cb("Cleaning up old version...", 0.90)

            try:
                shutil.rmtree(str(old_dir))
            except OSError as e:
                # Non-critical: old files remain but update succeeded
                logger.warning(f"Could not remove old Firefox directory: {e}")

            # Step 8: Update metadata
            if progress_cb:
                progress_cb("Updating metadata...", 0.95)

            new_version_info = self.metadata_repo.read_version(firefox_dir)
            metadata = self.metadata_repo.read_metadata(portable_root)
            metadata["firefox_version"] = new_version_info.get("version", new_version)
            metadata["firefox_build_id"] = new_version_info.get("build_id", "")
            metadata["last_updated"] = datetime.now(timezone.utc).isoformat()
            self.metadata_repo.write_metadata(portable_root, metadata)

            if progress_cb:
                progress_cb(f"Updated to Firefox {new_version}!", 1.0)

            result["success"] = True
            logger.info(f"Successfully updated Firefox {old_version} -> {new_version}")

        except RuntimeError as e:
            result["error"] = str(e)
            logger.error(f"Update failed: {e}")
        except ConnectionError as e:
            result["error"] = str(e)
            logger.error(f"Update failed (network): {e}")
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
            logger.error(f"Update failed: {e}", exc_info=True)
        finally:
            # Clean up temp directory
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(str(temp_dir))
                except OSError:
                    pass

        return result

    @staticmethod
    def _validate_portable_root(portable_root: Path) -> Optional[str]:
        """
        Validate that the path is a legitimate portable Firefox installation
        and not a system directory.

        Args:
            portable_root: Path to validate

        Returns:
            Error message string, or None if valid
        """
        if not portable_root.exists():
            return f"Directory does not exist: {portable_root}"

        if not (portable_root / "App").exists():
            return (
                "This does not appear to be a portable Firefox installation. "
                "Expected an 'App' directory inside the portable root."
            )

        # Prevent accidental operation on system Firefox installations
        resolved = portable_root.resolve()
        system_dirs = []
        try:
            import os
            prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
            system_dirs = [
                Path(prog_files) / "Mozilla Firefox",
                Path(prog_files_x86) / "Mozilla Firefox",
            ]
        except Exception:
            pass

        for sys_dir in system_dirs:
            try:
                if resolved == sys_dir.resolve() or sys_dir.resolve() in resolved.parents:
                    return (
                        "This appears to be a system Firefox installation, "
                        "not a portable one. The updater only works with "
                        "portable Firefox installations."
                    )
            except (ValueError, OSError):
                pass

        return None
