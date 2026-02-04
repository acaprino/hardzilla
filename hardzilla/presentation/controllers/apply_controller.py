#!/usr/bin/env python3
"""
Apply Controller
Handles logic for Screen 4 (Apply Settings) and Screen 3 (Extensions)
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardzilla.presentation.view_models import ApplyViewModel
from hardzilla.application.use_cases import ApplySettingsUseCase, SaveProfileUseCase
from hardzilla.application.use_cases.install_extensions_use_case import InstallExtensionsUseCase

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
        install_extensions: InstallExtensionsUseCase,
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
        self.install_extensions = install_extensions
        self.ui_callback = ui_callback
        self._apply_thread: Optional[threading.Thread] = None
        self._extension_thread: Optional[threading.Thread] = None

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
                self.view_model.apply_error_message = error
            else:
                self.view_model.apply_error_message = ""

        # Schedule on main thread if callback provided, otherwise run directly
        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()

    def handle_install_extensions(self) -> None:
        """
        Handle install extensions button click.

        Installs extensions to Firefox in background thread.
        """
        # Prevent double-clicks
        if self._extension_thread and self._extension_thread.is_alive():
            logger.warning("Extension installation already in progress")
            return

        # Validate inputs
        if not self.view_model.selected_extensions:
            self._update_extension_ui_state(error="No extensions selected")
            return

        if not self.view_model.firefox_path:
            self._update_extension_ui_state(error="No Firefox path selected")
            return

        # Snapshot extension IDs and firefox path to avoid race conditions
        extension_ids = list(self.view_model.selected_extensions)
        firefox_path = self.view_model.firefox_path

        # Set installing state
        self.view_model.is_installing_extensions = True

        # Run in background thread with snapshotted values
        self._extension_thread = threading.Thread(
            target=self._install_extensions_worker,
            args=(extension_ids, firefox_path),
            daemon=True,
            name="InstallExtensionsThread"
        )
        self._extension_thread.start()

    def _install_extensions_worker(self, extension_ids: list, firefox_path: str) -> None:
        """
        Worker thread for installing extensions.

        Runs installation operations without blocking UI.

        Args:
            extension_ids: Snapshot of extension IDs to install
            firefox_path: Snapshot of Firefox profile path
        """
        try:
            # Execute use case with snapshotted values
            results = self.install_extensions.execute(
                profile_path=Path(firefox_path),
                extension_ids=extension_ids
            )

            logger.info(
                f"Installed {len(results['installed'])} of {results['total']} extensions"
            )

            # Schedule UI update
            self._update_extension_ui_state(
                is_installing=False,
                success=True,
                results=results
            )

        except Exception as e:
            logger.error(f"Failed to install extensions: {e}", exc_info=True)
            self._update_extension_ui_state(
                is_installing=False,
                success=False,
                error=str(e)
            )

    def _update_extension_ui_state(
        self,
        is_installing: Optional[bool] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None,
        results: Optional[dict] = None
    ) -> None:
        """
        Update extension-related ViewModel state safely from any thread.

        Args:
            is_installing: Whether installation is in progress
            success: Whether installation succeeded
            error: Error message if failed
            results: Installation results dictionary
        """
        def update():
            if is_installing is not None:
                self.view_model.is_installing_extensions = is_installing
            # SET RESULTS FIRST - before triggering success subscription
            # The success subscriber reads extension_install_results immediately,
            # so results must be populated before extension_install_success fires.
            if results is not None:
                self.view_model.extension_install_results = results
            # NOW set success - subscription will see updated results
            if success is not None:
                self.view_model.extension_install_success = success
            if error is not None:
                self.view_model.extension_error_message = error
            else:
                self.view_model.extension_error_message = ""

        # Schedule on main thread if callback provided
        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()
