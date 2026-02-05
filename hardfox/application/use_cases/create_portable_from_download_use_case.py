#!/usr/bin/env python3
"""
Create Portable Firefox from Download Use Case

Orchestrates downloading Firefox from Mozilla, extracting it, and creating
a complete portable installation in a user-specified directory.
"""

import logging
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Display names for channels
CHANNEL_DISPLAY_NAMES = {
    "stable": "Stable",
    "beta": "Beta",
    "devedition": "Developer Edition",
}


class CreatePortableFromDownloadUseCase:
    """
    Use case for creating a portable Firefox installation from a Mozilla download.

    Flow:
    1. Validate destination directory
    2. Fetch latest version for selected channel
    3. Download installer with SHA-512 verification
    4. Extract installer to temp dir
    5. Create portable structure in destination
    6. Cleanup temp files
    """

    def __init__(self, download_repo, portable_repo):
        """
        Args:
            download_repo: MozillaDownloadRepository instance
            portable_repo: PortableConversionRepository instance
        """
        self.download_repo = download_repo
        self.portable_repo = portable_repo

    def fetch_channel_version(self, channel: str) -> Dict[str, str]:
        """
        Fetch the latest Firefox version for a channel.

        Args:
            channel: One of "stable", "beta", "devedition"

        Returns:
            Dict with 'version' and 'channel' keys.

        Raises:
            ConnectionError: If the API is unreachable
        """
        return self.download_repo.get_latest_version_for_channel(channel)

    def execute(
        self,
        channel: str,
        destination_dir: str,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Dict:
        """
        Execute the full create-portable-from-download flow.

        Args:
            channel: One of "stable", "beta", "devedition"
            destination_dir: Path to create the portable installation
            progress_cb: Progress callback(status, progress_0_to_1)
            cancel_event: Threading event for cancellation

        Returns:
            Dict with keys: success, version, channel, size_mb, error
        """
        result = {
            "success": False,
            "version": "",
            "channel": channel,
            "size_mb": 0.0,
            "error": None
        }

        # Validate channel early for a clear error message
        if channel not in CHANNEL_DISPLAY_NAMES:
            result["error"] = f"Unknown channel: {channel}. Must be one of: {', '.join(CHANNEL_DISPLAY_NAMES.keys())}"
            return result

        temp_dir = None
        channel_name = CHANNEL_DISPLAY_NAMES[channel]

        try:
            dest_path = Path(destination_dir)

            # Step 1: Validate destination (0%)
            if progress_cb:
                progress_cb("Validating destination...", 0.0)

            # Firefox installer is ~60 MB, extracted is ~400 MB; require 500 MB free
            validation_error = self.portable_repo.validate_destination(
                destination_dir, required_mb=500
            )
            if validation_error:
                result["error"] = validation_error
                return result

            dest_path.mkdir(parents=True, exist_ok=True)

            # Step 2: Fetch latest version for channel (0-5%)
            if cancel_event and cancel_event.is_set():
                result["error"] = "Cancelled by user"
                return result

            if progress_cb:
                progress_cb(f"Fetching latest {channel_name} version...", 0.02)

            version_info = self.download_repo.get_latest_version_for_channel(channel)
            version = version_info.get("version", "")
            if not version:
                result["error"] = f"Could not determine latest {channel_name} version"
                return result
            result["version"] = version

            if progress_cb:
                progress_cb(f"Latest {channel_name}: Firefox {version}", 0.05)

            # Step 3: Download installer (5-55%)
            if cancel_event and cancel_event.is_set():
                result["error"] = "Cancelled by user"
                return result

            temp_dir = Path(tempfile.mkdtemp(prefix="hardfox_create_"))

            def download_progress(status, progress):
                """Remap raw download progress [0, 1] to [0.05, 0.55] overall."""
                if progress_cb:
                    overall = 0.05 + progress * 0.50
                    progress_cb(status, min(overall, 0.55))

            installer_path = self.download_repo.download_installer_for_channel(
                version=version,
                channel=channel,
                dest_path=temp_dir,
                progress_cb=download_progress,
                cancel_event=cancel_event
            )

            if cancel_event and cancel_event.is_set():
                result["error"] = "Cancelled by user"
                return result

            # Step 4: Extract installer (55-75%)
            def extract_progress(status, progress):
                """Remap extraction progress to 0.55-0.75 overall.

                extract_installer reports two fixed progress points:
                0.65 ("Extracting...") and 0.75 ("Extraction complete").
                Linear mapping: [0.65, 0.75] -> [0.55, 0.75].
                """
                if progress_cb:
                    overall = 0.55 + max(0, progress - 0.65) * 2.0
                    overall = max(0.55, min(overall, 0.75))
                    progress_cb(status, overall)

            extract_dir = temp_dir / "extracted"
            self.download_repo.extract_installer(
                installer_path=installer_path,
                extract_dir=extract_dir,
                progress_cb=extract_progress,
                cancel_event=cancel_event
            )

            if cancel_event and cancel_event.is_set():
                result["error"] = "Cancelled by user"
                return result

            # Step 5: Create portable structure (75-95%)
            def structure_progress(status, progress):
                """Remap portable structure progress to 0.75-0.95 overall."""
                if progress_cb:
                    overall = 0.75 + progress * 0.20
                    progress_cb(status, min(overall, 0.95))

            structure_result = self.portable_repo.create_portable_structure(
                dest_dir=dest_path,
                firefox_source_dir=extract_dir,
                progress_cb=structure_progress,
                cancel_event=cancel_event
            )

            if not structure_result.get("success"):
                result["error"] = structure_result.get("error", "Failed to create portable structure")
                return result

            result["size_mb"] = structure_result.get("size_mb", 0.0)

            # Step 6: Cleanup (95-100%)
            if progress_cb:
                progress_cb("Cleaning up temporary files...", 0.95)

            # temp_dir cleanup handled in finally block

            if progress_cb:
                progress_cb(f"Firefox {version} ({channel_name}) portable created!", 1.0)

            result["success"] = True
            logger.info(f"Successfully created portable Firefox {version} ({channel}) at {dest_path}")

        except RuntimeError as e:
            result["error"] = str(e)
            logger.error(f"Create portable failed: {e}")
        except ConnectionError as e:
            result["error"] = str(e)
            logger.error(f"Create portable failed (network): {e}")
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
            logger.error(f"Create portable failed: {e}", exc_info=True)
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(str(temp_dir))
                except OSError:
                    pass

        return result
