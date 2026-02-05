#!/usr/bin/env python3
"""
Settings Controller
Unified controller for the Settings tab (merged Setup + Apply settings logic).
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardfox.presentation.view_models.settings_view_model import SettingsViewModel
from hardfox.application.use_cases import ApplySettingsUseCase, SaveProfileUseCase
from hardfox.infrastructure.persistence.firefox_detection import is_firefox_running

logger = logging.getLogger(__name__)


class SettingsController:
    """
    Controller for the unified Settings tab.

    Handles:
    - Firefox path change and settings import (from SetupController)
    - Preset selection
    - JSON profile import
    - Apply settings to Firefox (from ApplyController)
    """

    def __init__(
        self,
        view_model: SettingsViewModel,
        import_from_firefox=None,
        apply_settings: ApplySettingsUseCase = None,
        save_profile: SaveProfileUseCase = None,
        on_profile_imported: Callable = None,
        ui_callback: Optional[Callable[[Callable], None]] = None
    ):
        """
        Initialize controller.

        Args:
            view_model: SettingsViewModel instance
            import_from_firefox: Use case for importing from Firefox
            apply_settings: Use case for applying settings
            save_profile: Use case for saving profiles
            on_profile_imported: Callback when profile is imported from Firefox
            ui_callback: Callback for scheduling UI updates from background thread
        """
        self.view_model = view_model
        self.import_from_firefox = import_from_firefox
        self.apply_settings = apply_settings
        self.save_profile = save_profile
        self.on_profile_imported = on_profile_imported
        self.ui_callback = ui_callback
        self._import_thread: Optional[threading.Thread] = None
        self._apply_thread: Optional[threading.Thread] = None

    # =================================================================
    # Firefox path / import (from SetupController)
    # =================================================================

    def validate_firefox_path(self, path: str) -> bool:
        """Validate Firefox profile path."""
        firefox_path = Path(path)
        if not firefox_path.exists():
            return False

        has_prefs = (firefox_path / "prefs.js").exists()
        has_times = (firefox_path / "times.json").exists()
        return has_prefs or has_times

    def handle_firefox_path_changed(self, path: str) -> None:
        """
        Handle Firefox path selection - import current settings.

        Args:
            path: Firefox profile path
        """
        if not self.import_from_firefox:
            logger.warning("Import use case not available")
            return

        if self._import_thread and self._import_thread.is_alive():
            logger.warning("Import already in progress")
            return

        self._import_thread = threading.Thread(
            target=self._import_worker,
            args=(path,),
            daemon=True,
            name="ImportFromFirefoxThread"
        )
        self._import_thread.start()

    def _import_worker(self, path: str) -> None:
        """Worker thread for importing Firefox settings."""
        try:
            firefox_path = Path(path)

            profile = self.import_from_firefox.execute(
                profile_path=firefox_path,
                profile_name=f"Current - {firefox_path.name}"
            )

            logger.info(f"Imported profile from {firefox_path.name}: {len(profile.settings)} settings")

            if self.on_profile_imported:
                def update():
                    self.on_profile_imported(profile)

                if self.ui_callback:
                    self.ui_callback(update)
                else:
                    update()

        except Exception as e:
            logger.error(f"Failed to import from Firefox: {e}", exc_info=True)

            def show_error():
                if self.on_profile_imported:
                    self.on_profile_imported(None)

            if self.ui_callback:
                self.ui_callback(show_error)
            else:
                show_error()

    # =================================================================
    # Apply settings (from ApplyController)
    # =================================================================

    def handle_apply(self) -> None:
        """
        Handle apply button click.

        Applies settings to Firefox profile in background thread.
        """
        if self._apply_thread and self._apply_thread.is_alive():
            logger.warning("Apply operation already in progress")
            return

        profile = self.view_model.build_profile()
        if not profile:
            self._update_apply_state(error="No settings to apply")
            return

        if not self.view_model.firefox_path:
            self._update_apply_state(error="No Firefox path specified")
            return

        if is_firefox_running():
            logger.warning("Cannot apply settings: Firefox is running")
            self._update_apply_state(
                error="Firefox is currently running.\n\n"
                      "Please close Firefox completely before applying settings.\n"
                      "Changes to user.js are only loaded when Firefox starts."
            )
            return

        self.view_model.is_applying = True

        self._apply_thread = threading.Thread(
            target=self._apply_worker,
            args=(profile,),
            daemon=True,
            name="ApplySettingsThread"
        )
        self._apply_thread.start()

    def _apply_worker(self, profile) -> None:
        """Worker thread for applying settings."""
        try:
            if self.view_model.save_to_json:
                save_path = None
                if self.view_model.json_save_path:
                    save_path = Path(self.view_model.json_save_path)
                self.save_profile.execute(profile, save_path)
                logger.info("Profile saved to JSON")

            results = self.apply_settings.execute(
                profile_path=Path(self.view_model.firefox_path),
                settings=profile.settings,
                level=self.view_model.get_apply_level()
            )

            logger.info(
                f"Applied {results['base_applied']} BASE and "
                f"{results['advanced_applied']} ADVANCED settings"
            )

            self._update_apply_state(
                is_applying=False,
                success=True,
                results=results
            )

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}", exc_info=True)
            self._update_apply_state(
                is_applying=False,
                success=False,
                error=str(e)
            )

    def _update_apply_state(
        self,
        is_applying: Optional[bool] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None,
        results: Optional[dict] = None
    ) -> None:
        """Update ViewModel state safely from any thread."""
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
                self.view_model.apply_error_message = error
            else:
                self.view_model.apply_error_message = ""

        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()
