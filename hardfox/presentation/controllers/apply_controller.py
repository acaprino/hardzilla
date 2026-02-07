#!/usr/bin/env python3
"""
Apply Controller
Handles extension installation and uninstallation.
Settings application logic has moved to SettingsController.
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardfox.presentation.view_models import ApplyViewModel
from hardfox.application.use_cases.install_extensions_use_case import InstallExtensionsUseCase
from hardfox.application.use_cases.uninstall_extensions_use_case import UninstallExtensionsUseCase
from hardfox.infrastructure.persistence.firefox_detection import is_firefox_running

logger = logging.getLogger(__name__)


class ApplyController:
    """
    Controller for Extensions tab.

    Coordinates extension installation and uninstallation.
    """

    def __init__(
        self,
        view_model: ApplyViewModel,
        install_extensions: InstallExtensionsUseCase,
        uninstall_extensions: UninstallExtensionsUseCase,
        ui_callback: Optional[Callable[[Callable], None]] = None,
        # Keep these params for backward compat but they're unused
        apply_settings=None,
        save_profile=None
    ):
        self.view_model = view_model
        self.install_extensions = install_extensions
        self.uninstall_extensions = uninstall_extensions
        self.ui_callback = ui_callback
        self._extension_thread: Optional[threading.Thread] = None
        self._uninstall_thread: Optional[threading.Thread] = None

    def handle_install_extensions(self) -> None:
        """Handle install extensions button click."""
        if self._extension_thread and self._extension_thread.is_alive():
            logger.warning("Extension installation already in progress")
            return

        if not self.view_model.selected_extensions:
            self._update_extension_ui_state(success=False, error="No extensions selected")
            return

        if not self.view_model.firefox_path:
            self._update_extension_ui_state(success=False, error="No Firefox path selected")
            return

        if is_firefox_running():
            logger.warning("Cannot install extensions: Firefox is running")
            self._update_extension_ui_state(
                success=False,
                error="Firefox is currently running.\n\n"
                      "Please close Firefox completely before installing extensions.\n"
                      "Extension policies are loaded when Firefox starts."
            )
            return

        extension_ids = list(self.view_model.selected_extensions)
        firefox_path = self.view_model.firefox_path

        self.view_model.is_installing_extensions = True

        self._extension_thread = threading.Thread(
            target=self._install_extensions_worker,
            args=(extension_ids, firefox_path),
            daemon=True,
            name="InstallExtensionsThread"
        )
        self._extension_thread.start()

    def _install_extensions_worker(self, extension_ids: list, firefox_path: str) -> None:
        """Worker thread for installing extensions."""
        try:
            results = self.install_extensions.execute(
                profile_path=Path(firefox_path),
                extension_ids=extension_ids
            )

            logger.info(
                f"Installed {len(results['installed'])} of {results['total']} extensions"
            )

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
        """Update extension-related ViewModel state safely from any thread."""
        def update():
            if is_installing is not None:
                self.view_model.is_installing_extensions = is_installing
            if results is not None:
                self.view_model.extension_install_results = results
            if success is not None:
                self.view_model.extension_install_success = success
            if error is not None:
                self.view_model.extension_error_message = error
            else:
                self.view_model.extension_error_message = ""

        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()

    def handle_uninstall_extensions(self) -> None:
        """Handle uninstall extensions button click."""
        if self._uninstall_thread and self._uninstall_thread.is_alive():
            logger.warning("Extension uninstallation already in progress")
            return

        if not self.view_model.selected_extensions:
            self._update_uninstall_ui_state(success=False, error="No extensions selected")
            return

        if not self.view_model.firefox_path:
            self._update_uninstall_ui_state(success=False, error="No Firefox path selected")
            return

        if is_firefox_running():
            logger.warning("Cannot uninstall extensions: Firefox is running")
            self._update_uninstall_ui_state(
                success=False,
                error="Firefox is currently running.\n\n"
                      "Please close Firefox completely before uninstalling extensions.\n"
                      "Extension policies are loaded when Firefox starts."
            )
            return

        extension_ids = list(self.view_model.selected_extensions)
        firefox_path = self.view_model.firefox_path

        self.view_model.is_uninstalling_extensions = True

        self._uninstall_thread = threading.Thread(
            target=self._uninstall_extensions_worker,
            args=(extension_ids, firefox_path),
            daemon=True,
            name="UninstallExtensionsThread"
        )
        self._uninstall_thread.start()

    def _uninstall_extensions_worker(self, extension_ids: list, firefox_path: str) -> None:
        """Worker thread for uninstalling extensions."""
        try:
            results = self.uninstall_extensions.execute(
                profile_path=Path(firefox_path),
                extension_ids=extension_ids
            )

            logger.info(
                f"Uninstalled {len(results['uninstalled'])} of {results['total']} extensions"
            )

            self._update_uninstall_ui_state(
                is_uninstalling=False,
                success=True,
                results=results
            )

        except Exception as e:
            logger.error(f"Failed to uninstall extensions: {e}", exc_info=True)
            self._update_uninstall_ui_state(
                is_uninstalling=False,
                success=False,
                error=str(e)
            )

    def _update_uninstall_ui_state(
        self,
        is_uninstalling: Optional[bool] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None,
        results: Optional[dict] = None
    ) -> None:
        """Update uninstall-related ViewModel state safely from any thread."""
        def update():
            if is_uninstalling is not None:
                self.view_model.is_uninstalling_extensions = is_uninstalling
            if results is not None:
                self.view_model.extension_uninstall_results = results
            if success is not None:
                self.view_model.extension_uninstall_success = success
            if error is not None:
                self.view_model.extension_uninstall_error_message = error
            else:
                self.view_model.extension_uninstall_error_message = ""

        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()

    def handle_refresh_installed_extensions(self) -> None:
        """Refresh the list of installed extensions from policies.json."""
        if not self.view_model.firefox_path:
            self.view_model.installed_extensions = []
            return

        try:
            installed = self.uninstall_extensions.get_installed(
                profile_path=Path(self.view_model.firefox_path)
            )
            self.view_model.installed_extensions = installed
            logger.info(f"Refreshed installed extensions: {len(installed)} found")
        except Exception as e:
            logger.error(f"Failed to refresh installed extensions: {e}")
            self.view_model.installed_extensions = []
