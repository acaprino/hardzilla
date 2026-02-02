#!/usr/bin/env python3
"""
Apply Controller
Handles logic for Screen 3 (Apply Settings)
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardzilla.presentation.view_models import ApplyViewModel
from hardzilla.application.use_cases import ApplySettingsUseCase, SaveProfileUseCase

logger = logging.getLogger(__name__)


class ApplyController:
    """
    Controller for Apply screen.

    Coordinates applying settings to Firefox and saving profiles.
    """

    def __init__(
        self,
        view_model: ApplyViewModel,
        apply_settings: ApplySettingsUseCase,
        save_profile: SaveProfileUseCase,
        ui_callback: Optional[Callable[[Callable], None]] = None
    ):
        """
        Initialize controller.

        Args:
            view_model: ApplyViewModel instance
            apply_settings: Use case for applying settings
            save_profile: Use case for saving profiles
            ui_callback: Callback for scheduling UI updates from background thread
        """
        self.view_model = view_model
        self.apply_settings = apply_settings
        self.save_profile = save_profile
        self.ui_callback = ui_callback
        self._apply_thread: Optional[threading.Thread] = None

    def handle_apply(self) -> None:
        """
        Handle apply button click.

        Applies settings to Firefox profile in background thread.
        """
        # Prevent double-clicks
        if self._apply_thread and self._apply_thread.is_alive():
            logger.warning("Apply operation already in progress")
            return

        # Validate inputs before starting thread
        if not self.view_model.profile:
            self._update_ui_state(error="No profile to apply")
            return

        if not self.view_model.firefox_path:
            self._update_ui_state(error="No Firefox path specified")
            return

        # Set applying state (we're on main thread, set directly)
        self.view_model.is_applying = True

        # Run in background thread
        self._apply_thread = threading.Thread(
            target=self._apply_worker,
            daemon=True,
            name="ApplySettingsThread"
        )
        self._apply_thread.start()

    def _apply_worker(self) -> None:
        """
        Worker thread for applying settings.

        Runs file I/O operations without blocking UI.
        """
        try:
            # Save to JSON if requested
            if self.view_model.save_to_json:
                save_path = None
                if self.view_model.json_save_path:
                    save_path = Path(self.view_model.json_save_path)

                self.save_profile.execute(self.view_model.profile, save_path)
                logger.info("Profile saved to JSON")

            # Apply settings to Firefox
            results = self.apply_settings.execute(
                profile_path=Path(self.view_model.firefox_path),
                settings=self.view_model.profile.settings,
                level=self.view_model.get_apply_level()
            )

            logger.info(
                f"Applied {results['base_applied']} BASE and "
                f"{results['advanced_applied']} ADVANCED settings"
            )

            # Schedule UI update on main thread
            self._update_ui_state(
                is_applying=False,
                success=True,
                results=results
            )

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}", exc_info=True)
            self._update_ui_state(
                is_applying=False,
                success=False,
                error=str(e)
            )

    def _update_ui_state(
        self,
        is_applying: Optional[bool] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None,
        results: Optional[dict] = None
    ) -> None:
        """
        Update ViewModel state safely from any thread.

        Args:
            is_applying: Whether apply operation is in progress
            success: Whether apply succeeded
            error: Error message if failed
            results: Apply results dictionary
        """
        def update():
            if is_applying is not None:
                self.view_model.is_applying = is_applying
            # SET RESULTS FIRST - before triggering success subscription
            if results is not None:
                self.view_model.set_apply_results(results)
            # NOW set success - subscription will see updated counts
            if success is not None:
                self.view_model.apply_success = success
            if error is not None:
                self.view_model.error_message = error
            else:
                self.view_model.error_message = ""

        # Schedule on main thread if callback provided, otherwise run directly
        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()
