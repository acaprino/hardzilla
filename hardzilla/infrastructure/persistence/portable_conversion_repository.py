#!/usr/bin/env python3
"""
Portable Conversion Repository

Handles file operations for converting a standard Firefox installation
into a PortableApps.com-format portable installation.
"""

import logging
import os
import shutil
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional

from hardzilla.infrastructure.persistence.firefox_detection import get_firefox_installation_dir

logger = logging.getLogger(__name__)


class PortableConversionRepository:
    """
    Repository for converting Firefox to a portable installation.

    Creates a PortableApps.com-compatible directory structure:
        <destination>/
            FirefoxPortable.bat    - Launcher script
            App/
                Firefox64/         - Copy of Firefox installation
            Data/
                profile/           - (Optional) copy of user profile
    """

    def convert(
        self,
        firefox_dir: Path,
        dest_dir: Path,
        profile_path: Optional[Path] = None,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Dict:
        """
        Convert Firefox installation to portable format.

        Args:
            firefox_dir: Path to Firefox installation directory
            dest_dir: Destination directory for portable installation
            profile_path: Optional path to Firefox profile to copy
            progress_cb: Progress callback(status_text, progress_float_0_to_1)
            cancel_event: Threading event to signal cancellation

        Returns:
            Dict with keys: success, files_copied, files_failed, failed_files, size_mb, error
        """
        files_copied = 0
        total_size = 0
        all_failed: List[str] = []

        try:
            # Phase 1: Setup (5%)
            if progress_cb:
                progress_cb("Creating directory structure...", 0.0)

            if cancel_event and cancel_event.is_set():
                return self._cancelled_result()

            self._create_directory_structure(dest_dir)

            if progress_cb:
                progress_cb("Directory structure created", 0.05)

            # Phase 2: Copy Firefox files (70%)
            if progress_cb:
                progress_cb("Copying Firefox installation...", 0.05)

            firefox_dest = dest_dir / "App" / "Firefox64"
            copied, size, failed = self._copy_with_progress(
                src=firefox_dir,
                dst=firefox_dest,
                progress_cb=progress_cb,
                phase_start=0.05,
                phase_weight=0.70,
                cancel_event=cancel_event
            )
            files_copied += copied
            total_size += size
            all_failed.extend(failed)

            if cancel_event and cancel_event.is_set():
                return self._cancelled_result()

            # Phase 3: Copy profile (20%) - optional
            if profile_path and profile_path.exists():
                if progress_cb:
                    progress_cb("Copying Firefox profile...", 0.75)

                profile_dest = dest_dir / "Data" / "profile"
                copied, size, failed = self._copy_with_progress(
                    src=profile_path,
                    dst=profile_dest,
                    progress_cb=progress_cb,
                    phase_start=0.75,
                    phase_weight=0.20,
                    cancel_event=cancel_event
                )
                files_copied += copied
                total_size += size
                all_failed.extend(failed)

            if cancel_event and cancel_event.is_set():
                return self._cancelled_result()

            # Phase 4: Finalize (5%)
            if progress_cb:
                progress_cb("Creating launcher...", 0.95)

            self._create_launcher_bat(dest_dir)

            # Ensure Data/profile directory exists even without copy
            profile_dir = dest_dir / "Data" / "profile"
            profile_dir.mkdir(parents=True, exist_ok=True)

            if progress_cb:
                progress_cb("Conversion complete!", 1.0)

            size_mb = round(total_size / (1024 * 1024), 1)

            # Check for critical missing files
            firefox_exe = firefox_dest / "firefox.exe"
            if not firefox_exe.exists():
                firefox_bin = firefox_dest / "firefox"
                if not firefox_bin.exists():
                    return {
                        "success": False,
                        "files_copied": files_copied,
                        "files_failed": len(all_failed),
                        "failed_files": all_failed[:10],
                        "size_mb": size_mb,
                        "error": "Critical failure: firefox.exe was not copied. "
                                 "The portable installation will not work."
                    }

            return {
                "success": True,
                "files_copied": files_copied,
                "files_failed": len(all_failed),
                "failed_files": all_failed[:10],
                "size_mb": size_mb,
                "error": None
            }

        except PermissionError as e:
            logger.error(f"Permission denied during conversion: {e}")
            return {
                "success": False,
                "files_copied": files_copied,
                "files_failed": len(all_failed),
                "failed_files": all_failed[:10],
                "size_mb": 0,
                "error": f"Permission denied: {e}\nTry running as Administrator or choosing a different destination."
            }

        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            return {
                "success": False,
                "files_copied": files_copied,
                "files_failed": len(all_failed),
                "failed_files": all_failed[:10],
                "size_mb": 0,
                "error": str(e)
            }

    def estimate_size(
        self,
        firefox_dir: Path,
        profile_path: Optional[Path] = None
    ) -> float:
        """
        Estimate total size in MB for the portable installation.

        Args:
            firefox_dir: Path to Firefox installation directory
            profile_path: Optional path to Firefox profile

        Returns:
            Estimated size in megabytes
        """
        total = 0

        if firefox_dir and firefox_dir.exists():
            total += self._get_dir_size(firefox_dir)

        if profile_path and profile_path.exists():
            total += self._get_dir_size(profile_path)

        return round(total / (1024 * 1024), 1)

    def validate_destination(
        self,
        dest_dir: str,
        required_mb: float = 0,
        firefox_dir: Optional[Path] = None
    ) -> Optional[str]:
        """
        Validate the destination directory.

        Args:
            dest_dir: Destination directory path string
            required_mb: Required space in MB
            firefox_dir: Actual Firefox installation directory to check against

        Returns:
            Error message string, or None if valid
        """
        if not dest_dir:
            return "No destination selected"

        dest_path = Path(dest_dir)

        # Check parent exists and is writable
        parent = dest_path if dest_path.exists() else dest_path.parent
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent

        if not parent.exists():
            return "Destination path is invalid"

        # Check write permission
        try:
            test_file = parent / ".hardzilla_write_test"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            return "No write permission to destination. Try a different folder or run as Administrator."

        # Check disk space
        if required_mb > 0:
            error = self._check_disk_space(parent, required_mb)
            if error:
                return error

        # Check destination is not inside Firefox installation
        try:
            dest_resolved = dest_path.resolve()

            # Check against the actual detected Firefox directory
            if firefox_dir:
                try:
                    ff_resolved = firefox_dir.resolve()
                    if dest_resolved == ff_resolved or ff_resolved in dest_resolved.parents:
                        return "Destination cannot be inside the Firefox installation directory"
                    # Also check if destination is a parent of Firefox dir (would overwrite it)
                    if dest_resolved in ff_resolved.parents:
                        return "Destination cannot be a parent of the Firefox installation directory"
                except (ValueError, OSError):
                    pass
        except (ValueError, OSError):
            pass

        return None

    def detect_firefox_dir(self, profile_path: Optional[str] = None) -> Optional[Path]:
        """
        Detect Firefox installation directory.

        Args:
            profile_path: Optional Firefox profile path for Portable detection

        Returns:
            Path to Firefox installation, or None
        """
        pp = Path(profile_path) if profile_path else None
        return get_firefox_installation_dir(pp)

    def _create_directory_structure(self, dest_dir: Path) -> None:
        """Create the PortableApps directory structure."""
        (dest_dir / "App" / "Firefox64").mkdir(parents=True, exist_ok=True)
        (dest_dir / "Data" / "profile").mkdir(parents=True, exist_ok=True)
        logger.info(f"Created portable directory structure at: {dest_dir}")

    def _copy_with_progress(
        self,
        src: Path,
        dst: Path,
        progress_cb: Optional[Callable],
        phase_start: float,
        phase_weight: float,
        cancel_event: Optional[threading.Event] = None
    ) -> tuple:
        """
        Copy directory tree with per-file progress reporting.

        Uses a single-pass walk: counts files as they are copied and estimates
        progress based on discovered files so far.

        Args:
            src: Source directory
            dst: Destination directory
            progress_cb: Progress callback
            phase_start: Starting progress value for this phase
            phase_weight: Weight of this phase in total progress
            cancel_event: Threading event to signal cancellation

        Returns:
            Tuple of (files_copied, total_bytes, failed_files)
        """
        files_copied = 0
        total_bytes = 0
        failed_files: List[str] = []

        # Estimate total file count for progress (fast stat-based count)
        estimated_total = 0
        try:
            for _ in src.rglob('*'):
                estimated_total += 1
        except OSError:
            estimated_total = 100  # fallback estimate

        if estimated_total == 0:
            return 0, 0, []

        processed = 0

        for root, dirs, files in os.walk(src):
            # Check cancellation
            if cancel_event and cancel_event.is_set():
                logger.info("Conversion cancelled by user")
                return files_copied, total_bytes, failed_files

            # Create corresponding directory in destination
            rel_path = os.path.relpath(root, src)
            dest_root = dst / rel_path
            dest_root.mkdir(parents=True, exist_ok=True)

            for filename in files:
                # Check cancellation per-file
                if cancel_event and cancel_event.is_set():
                    logger.info("Conversion cancelled by user")
                    return files_copied, total_bytes, failed_files

                src_file = Path(root) / filename
                dst_file = dest_root / filename
                processed += 1

                try:
                    shutil.copy2(str(src_file), str(dst_file))
                    file_size = src_file.stat().st_size
                    total_bytes += file_size
                    files_copied += 1

                    if progress_cb and estimated_total > 0:
                        file_progress = min(processed / estimated_total, 1.0)
                        overall = phase_start + (file_progress * phase_weight)
                        display_name = filename
                        if len(display_name) > 40:
                            display_name = display_name[:37] + "..."
                        progress_cb(
                            f"Copying: {display_name} ({files_copied}/{estimated_total})",
                            overall
                        )
                except (PermissionError, OSError) as e:
                    rel_failed = str(src_file.relative_to(src))
                    failed_files.append(rel_failed)
                    logger.warning(f"Failed to copy {src_file}: {e}")

        return files_copied, total_bytes, failed_files

    def _create_launcher_bat(self, dest_dir: Path) -> None:
        """
        Generate FirefoxPortable.bat launcher script.

        Uses setlocal to prevent special characters in paths (%, &, ^, !)
        from being interpreted by the command processor.

        Args:
            dest_dir: Root of portable installation
        """
        bat_content = '@echo off\r\n'
        bat_content += 'setlocal enableextensions disabledelayedexpansion\r\n'
        bat_content += 'set "BASE=%~dp0"\r\n'
        bat_content += 'set "FFDIR=%BASE%App\\Firefox64"\r\n'
        bat_content += 'if not exist "%FFDIR%\\firefox.exe" set "FFDIR=%BASE%App\\Firefox"\r\n'
        bat_content += 'set "PROFILE=%BASE%Data\\profile"\r\n'
        bat_content += 'if not exist "%PROFILE%\\" mkdir "%PROFILE%"\r\n'
        bat_content += 'start "" "%FFDIR%\\firefox.exe" -profile "%PROFILE%" -no-remote\r\n'
        bat_content += 'endlocal\r\n'

        bat_path = dest_dir / "FirefoxPortable.bat"
        bat_path.write_text(bat_content, encoding='utf-8')
        logger.info(f"Created launcher: {bat_path}")

    def _check_disk_space(self, dest_path: Path, required_mb: float) -> Optional[str]:
        """
        Check if destination has enough disk space.

        Args:
            dest_path: Path to check
            required_mb: Required space in MB

        Returns:
            Error message if insufficient space, None otherwise
        """
        try:
            usage = shutil.disk_usage(str(dest_path))
            available_mb = usage.free / (1024 * 1024)
            if available_mb < required_mb:
                return (
                    f"Insufficient disk space. "
                    f"Need {required_mb:.0f} MB, only {available_mb:.0f} MB available."
                )
        except OSError as e:
            logger.warning(f"Could not check disk space: {e}")

        return None

    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except OSError:
                        pass
        except OSError as e:
            logger.warning(f"Error calculating size of {path}: {e}")
        return total

    def _cancelled_result(self) -> Dict:
        """Create a standard cancellation result dict."""
        return {
            "success": False,
            "files_copied": 0,
            "files_failed": 0,
            "failed_files": [],
            "size_mb": 0,
            "error": "Conversion cancelled by user."
        }
