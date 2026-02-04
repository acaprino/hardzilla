#!/usr/bin/env python3
"""
Convert to Portable Use Case

Orchestrates converting a standard Firefox installation into a
PortableApps.com-format portable installation.
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ConvertToPortableUseCase:
    """
    Use case for converting Firefox to a portable installation.

    Validates inputs, estimates size, and delegates to the repository
    for the actual file copy operations.
    """

    def __init__(self, portable_repo):
        """
        Args:
            portable_repo: PortableConversionRepository instance
        """
        self.portable_repo = portable_repo

    def execute(
        self,
        firefox_install_dir: str,
        destination_dir: str,
        profile_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Dict:
        """
        Execute the conversion.

        Args:
            firefox_install_dir: Path to Firefox installation directory
            destination_dir: Path to destination directory
            profile_path: Optional path to Firefox profile to include
            progress_callback: Optional callback(status_text, progress_0_to_1)
            cancel_event: Optional threading event to signal cancellation

        Returns:
            Dict with keys: success, files_copied, files_failed, failed_files, size_mb, error
        """
        firefox_dir = Path(firefox_install_dir)
        dest_dir = Path(destination_dir)
        prof_path = Path(profile_path) if profile_path else None

        # Validate Firefox directory
        if not firefox_dir.exists():
            return self._error_result(f"Firefox directory not found: {firefox_dir}")

        firefox_exe = firefox_dir / "firefox.exe"
        if not firefox_exe.exists():
            # Try without .exe for Linux/macOS
            firefox_bin = firefox_dir / "firefox"
            if not firefox_bin.exists():
                return self._error_result(
                    f"Firefox binary not found in: {firefox_dir}"
                )

        # Validate destination (pass actual firefox_dir for overlap check)
        validation_error = self.portable_repo.validate_destination(
            str(dest_dir),
            required_mb=self.portable_repo.estimate_size(firefox_dir, prof_path),
            firefox_dir=firefox_dir
        )
        if validation_error:
            return self._error_result(validation_error)

        # Execute conversion
        logger.info(
            f"Starting portable conversion: {firefox_dir} -> {dest_dir}"
            f" (profile: {prof_path})"
        )

        result = self.portable_repo.convert(
            firefox_dir=firefox_dir,
            dest_dir=dest_dir,
            profile_path=prof_path,
            progress_cb=progress_callback,
            cancel_event=cancel_event
        )

        if result["success"]:
            logger.info(
                f"Conversion complete: {result['files_copied']} files, "
                f"{result['size_mb']} MB"
            )
            if result.get("files_failed", 0) > 0:
                logger.warning(
                    f"{result['files_failed']} files failed to copy: "
                    f"{result.get('failed_files', [])}"
                )
        else:
            logger.error(f"Conversion failed: {result['error']}")

        return result

    def _error_result(self, error: str) -> Dict:
        """Create a standard error result dict."""
        return {
            "success": False,
            "files_copied": 0,
            "files_failed": 0,
            "failed_files": [],
            "size_mb": 0,
            "error": error
        }
