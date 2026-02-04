#!/usr/bin/env python3
"""
Utilities Controller
Handles logic for the Utilities tab (Convert to Portable, etc.)
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardzilla.presentation.view_models.utilities_view_model import UtilitiesViewModel
from hardzilla.application.use_cases.convert_to_portable_use_case import ConvertToPortableUseCase

logger = logging.getLogger(__name__)


class UtilitiesController:
    """
    Controller for the Utilities tab.

    Coordinates the Convert to Portable operation with background threading.
    """

    def __init__(
        self,
        view_model: UtilitiesViewModel,
        convert_to_portable: ConvertToPortableUseCase,
        portable_repo,
        ui_callback: Optional[Callable[[Callable], None]] = None
    ):
        """
        Args:
            view_model: UtilitiesViewModel instance
            convert_to_portable: Use case for portable conversion
            portable_repo: PortableConversionRepository for detection/estimation
            ui_callback: Callback for scheduling UI updates from background thread
        """
        self.view_model = view_model
        self.convert_to_portable = convert_to_portable
        self.portable_repo = portable_repo
        self.ui_callback = ui_callback
        self._convert_thread: Optional[threading.Thread] = None
        self._detect_thread: Optional[threading.Thread] = None
        self._estimate_thread: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()

    def detect_firefox_installation(self, profile_path: Optional[str] = None) -> None:
        """
        Detect Firefox installation in a background thread.

        Args:
            profile_path: Optional Firefox profile path for Portable detection
        """
        # Prevent overlapping detection threads
        if self._detect_thread and self._detect_thread.is_alive():
            return

        self._detect_thread = threading.Thread(
            target=self._detect_worker,
            args=(profile_path,),
            daemon=True,
            name="DetectFirefoxThread"
        )
        self._detect_thread.start()

    def _detect_worker(self, profile_path: Optional[str]) -> None:
        """Background worker for Firefox detection and size estimation."""
        try:
            firefox_dir = self.portable_repo.detect_firefox_dir(profile_path)

            def update_detection():
                if firefox_dir:
                    self.view_model.firefox_install_dir = str(firefox_dir)
                    logger.info(f"Detected Firefox at: {firefox_dir}")
                else:
                    self.view_model.firefox_install_dir = ''
                    logger.warning("Could not detect Firefox installation")

            if self.ui_callback:
                self.ui_callback(update_detection)
            else:
                update_detection()

            # Also estimate size in the same background thread
            self._estimate_size_sync()

        except Exception as e:
            logger.error(f"Firefox detection failed: {e}", exc_info=True)

    def estimate_size(self) -> None:
        """Update ViewModel with estimated portable size in a background thread."""
        # Prevent overlapping estimation threads
        if hasattr(self, '_estimate_thread') and self._estimate_thread and self._estimate_thread.is_alive():
            return

        self._estimate_thread = threading.Thread(
            target=self._estimate_size_sync,
            daemon=True,
            name="EstimateSizeThread"
        )
        self._estimate_thread.start()

    def _estimate_size_sync(self) -> None:
        """Synchronous size estimation (runs on background thread)."""
        try:
            firefox_dir = self.view_model.firefox_install_dir
            profile_path = self.view_model.profile_path if self.view_model.copy_profile else None

            if not firefox_dir:
                def clear_size():
                    self.view_model.estimated_size_mb = 0.0
                if self.ui_callback:
                    self.ui_callback(clear_size)
                else:
                    clear_size()
                return

            size = self.portable_repo.estimate_size(
                Path(firefox_dir),
                Path(profile_path) if profile_path else None
            )

            def update_size():
                self.view_model.estimated_size_mb = size

            if self.ui_callback:
                self.ui_callback(update_size)
            else:
                update_size()

        except Exception as e:
            logger.error(f"Size estimation failed: {e}", exc_info=True)

    def handle_convert(self) -> None:
        """
        Handle Convert button click.

        Validates inputs and starts background conversion thread.
        """
        # Prevent double-clicks
        if self._convert_thread and self._convert_thread.is_alive():
            logger.warning("Conversion already in progress")
            return

        # Validate inputs
        if not self.view_model.firefox_install_dir:
            self._update_ui_state(error="Firefox installation not detected")
            return

        if not self.view_model.destination_dir:
            self._update_ui_state(error="No destination folder selected")
            return

        # Snapshot values for thread safety
        firefox_dir = self.view_model.firefox_install_dir
        dest_dir = self.view_model.destination_dir
        profile_path = self.view_model.profile_path if self.view_model.copy_profile else None

        # Reset cancellation and set converting state on main thread
        self._cancel_event.clear()
        self.view_model.is_converting = True
        self.view_model.conversion_progress = 0.0
        self.view_model.conversion_status = "Starting conversion..."
        self.view_model.conversion_result = None

        # Run in background thread
        self._convert_thread = threading.Thread(
            target=self._convert_worker,
            args=(firefox_dir, dest_dir, profile_path),
            daemon=True,
            name="ConvertToPortableThread"
        )
        self._convert_thread.start()

    def cancel_conversion(self) -> None:
        """Signal the background conversion thread to stop."""
        self._cancel_event.set()
        logger.info("Cancellation requested for portable conversion")

    def _convert_worker(self, firefox_dir: str, dest_dir: str, profile_path: Optional[str]) -> None:
        """
        Worker thread for portable conversion.

        Args:
            firefox_dir: Firefox installation directory
            dest_dir: Destination directory
            profile_path: Optional profile path to include
        """
        try:
            result = self.convert_to_portable.execute(
                firefox_install_dir=firefox_dir,
                destination_dir=dest_dir,
                profile_path=profile_path,
                progress_callback=self._progress_callback,
                cancel_event=self._cancel_event
            )

            self._update_ui_state(
                is_converting=False,
                result=result
            )

        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            self._update_ui_state(
                is_converting=False,
                result={
                    "success": False,
                    "files_copied": 0,
                    "files_failed": 0,
                    "failed_files": [],
                    "size_mb": 0,
                    "error": str(e)
                }
            )

    def _progress_callback(self, status: str, progress: float) -> None:
        """
        Thread-safe progress callback from background thread.

        Args:
            status: Current operation description
            progress: Progress value 0.0-1.0
        """
        def update():
            self.view_model.conversion_progress = progress
            self.view_model.conversion_status = status

        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()

    def _update_ui_state(
        self,
        is_converting: Optional[bool] = None,
        result: Optional[dict] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Update ViewModel state safely from any thread.

        Args:
            is_converting: Whether conversion is in progress
            result: Conversion result dictionary
            error: Error message (creates error result)
        """
        def update():
            if is_converting is not None:
                self.view_model.is_converting = is_converting

            if error is not None:
                self.view_model.conversion_result = {
                    "success": False,
                    "files_copied": 0,
                    "files_failed": 0,
                    "failed_files": [],
                    "size_mb": 0,
                    "error": error
                }
            elif result is not None:
                # Set result last so subscribers see final state
                self.view_model.conversion_result = result

        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()
