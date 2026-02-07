#!/usr/bin/env python3
"""
Extensions View - Dedicated tab for privacy extension management.
"""

import logging
import tkinter.messagebox as messagebox
import customtkinter as ctk
from typing import Callable

from hardfox.presentation.view_models import ApplyViewModel, SettingsViewModel
from hardfox.presentation.theme import Theme
from hardfox.metadata.extensions_metadata import EXTENSIONS_METADATA
from hardfox.domain.entities.extension import Extension
from hardfox.presentation.widgets.extension_row import ExtensionRow

logger = logging.getLogger(__name__)


class ExtensionsView(ctk.CTkFrame):
    """
    Extensions tab for selecting and installing Firefox privacy extensions.
    Standalone tab - no Back/Next navigation.
    """

    def __init__(
        self,
        parent,
        view_model: ApplyViewModel,
        on_install_extensions: Callable,
        on_uninstall_extensions: Callable,
        settings_view_model: SettingsViewModel = None
    ):
        logger.debug("ExtensionsView.__init__: starting initialization")
        super().__init__(parent)
        self.view_model = view_model
        self.settings_vm = settings_view_model
        self.on_install_extensions = on_install_extensions
        self.on_uninstall_extensions = on_uninstall_extensions
        self.extension_rows = []

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Build UI
        self._build_header()
        self._build_extensions_section()

        # Subscribe to view model changes
        self.view_model.subscribe('extension_install_success', self._on_extension_install_complete)
        self.view_model.subscribe('is_installing_extensions', self._on_extension_installing_changed)
        self.view_model.subscribe('extension_uninstall_success', self._on_extension_uninstall_complete)
        self.view_model.subscribe('is_uninstalling_extensions', self._on_extension_uninstalling_changed)
        logger.debug("ExtensionsView.__init__: initialization complete, %d extension rows created", len(self.extension_rows))

    def destroy(self):
        """Clean up ViewModel subscriptions before destroying widget."""
        logger.debug("ExtensionsView.destroy: unsubscribing from ViewModel events")
        self.view_model.unsubscribe('extension_install_success', self._on_extension_install_complete)
        self.view_model.unsubscribe('is_installing_extensions', self._on_extension_installing_changed)
        self.view_model.unsubscribe('extension_uninstall_success', self._on_extension_uninstall_complete)
        self.view_model.unsubscribe('is_uninstalling_extensions', self._on_extension_uninstalling_changed)
        super().destroy()

    def _build_header(self):
        """Build screen header."""
        header = ctk.CTkLabel(
            self,
            text="Privacy Extensions",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

        desc = ctk.CTkLabel(
            self,
            text="Recommended extensions to enhance Firefox privacy (auto-installed via Enterprise Policies)",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_tertiary')
        )
        desc.grid(row=1, column=0, pady=(0, 15), padx=10, sticky="w")

    def _build_extensions_section(self):
        """Build extensions list with select all/deselect all controls."""
        logger.debug("_build_extensions_section: loading EXTENSIONS_METADATA (%d extensions)", len(EXTENSIONS_METADATA))
        section = ctk.CTkFrame(self)
        section.grid(row=2, column=0, pady=10, sticky="nsew", padx=10)
        section.grid_rowconfigure(1, weight=1)
        section.grid_columnconfigure(0, weight=1)

        # Select All / Deselect All buttons
        btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))

        select_all_btn = ctk.CTkButton(
            btn_frame,
            text="Select All",
            command=self._select_all,
            width=100,
            height=28,
            fg_color=Theme.get_color('info'),
            hover_color=Theme.get_color('primary_hover'),
            font=ctk.CTkFont(size=12)
        )
        select_all_btn.pack(side="left", padx=(0, 10))

        deselect_all_btn = ctk.CTkButton(
            btn_frame,
            text="Deselect All",
            command=self._deselect_all,
            width=100,
            height=28,
            fg_color=Theme.get_color('text_secondary'),
            hover_color=Theme.get_color('border_dark'),
            font=ctk.CTkFont(size=12)
        )
        deselect_all_btn.pack(side="left")

        # Extension list (scrollable)
        extensions_frame = ctk.CTkScrollableFrame(section)
        extensions_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Track which extensions exist for initial ViewModel seeding
        all_ext_ids = []

        existing_selections = self.view_model.selected_extensions
        logger.debug("_build_extensions_section: existing ViewModel selections: %s", existing_selections)

        for ext_id, ext_data in EXTENSIONS_METADATA.items():
            all_ext_ids.append(ext_id)
            extension = Extension(
                extension_id=ext_id,
                name=ext_data['name'],
                description=ext_data['description'],
                install_url=ext_data['install_url'],
                breakage_risk=ext_data['breakage_risk'],
                size_mb=ext_data['size_mb'],
                icon=ext_data['icon']
            )
            # Check if ViewModel already has selections; default to checked
            is_checked = ext_id in existing_selections if existing_selections else True

            # Warn if CanvasBlocker is redundant due to Resist Fingerprinting
            warning_text = None
            if ext_id == "CanvasBlocker@kkapsner.de" and self.settings_vm:
                rfp = self.settings_vm.get_setting('resist_fingerprinting')
                if rfp and rfp.value:
                    warning_text = "\u26a0 Resist Fingerprinting is enabled \u2014 CanvasBlocker is redundant"

            row = ExtensionRow(
                extensions_frame,
                extension=extension,
                on_toggle=self._on_extension_toggled,
                initial_checked=is_checked,
                warning_text=warning_text
            )
            row.pack(fill="x", pady=2)
            self.extension_rows.append(row)

        # Seed ViewModel if it has no selections yet (first construction)
        if not self.view_model.selected_extensions:
            self.view_model.selected_extensions = all_ext_ids

        # Action buttons frame
        action_frame = ctk.CTkFrame(section, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=20, pady=(10, 10))

        # Install button
        self.install_extensions_btn = ctk.CTkButton(
            action_frame,
            text="Install Selected",
            command=self._on_install_extensions_clicked,
            fg_color=Theme.get_color('accent'),
            hover_color=Theme.get_color('accent_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180
        )
        self.install_extensions_btn.pack(side="left", padx=(0, 10))

        # Uninstall button
        self.uninstall_extensions_btn = ctk.CTkButton(
            action_frame,
            text="Uninstall Selected",
            command=self._on_uninstall_extensions_clicked,
            fg_color=Theme.get_color('error'),
            hover_color=Theme.get_color('error_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180
        )
        self.uninstall_extensions_btn.pack(side="left")

        # Status label
        self.extension_status_label = ctk.CTkLabel(
            section,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.extension_status_label.grid(row=3, column=0, padx=20, pady=(0, 10))

    def _select_all(self):
        """Select all extensions."""
        all_ids = [row.extension.extension_id for row in self.extension_rows]
        for row in self.extension_rows:
            row.set_checked(True)
        self.view_model.selected_extensions = all_ids

    def _deselect_all(self):
        """Deselect all extensions."""
        for row in self.extension_rows:
            row.set_checked(False)
        self.view_model.selected_extensions = []

    def _on_extension_toggled(self, extension_id: str, checked: bool):
        """Handle extension checkbox toggle."""
        current = list(self.view_model.selected_extensions)
        if checked:
            if extension_id not in current:
                current.append(extension_id)
        else:
            if extension_id in current:
                current.remove(extension_id)
        self.view_model.selected_extensions = current

    def _on_install_extensions_clicked(self):
        """Handle install extensions button click."""
        if not self.on_install_extensions:
            return
        if not self.view_model.firefox_path:
            self.extension_status_label.configure(
                text="\u2717 No Firefox profile selected",
                text_color=Theme.get_color('error')
            )
            return
        if not self.view_model.selected_extensions:
            self.extension_status_label.configure(
                text="\u2717 No extensions selected",
                text_color=Theme.get_color('error')
            )
            return
        self.on_install_extensions()

    def _on_uninstall_extensions_clicked(self):
        """Handle uninstall extensions button click."""
        if not self.on_uninstall_extensions:
            return
        if not self.view_model.firefox_path:
            self.extension_status_label.configure(
                text="\u2717 No Firefox profile selected",
                text_color=Theme.get_color('error')
            )
            return
        if not self.view_model.selected_extensions:
            self.extension_status_label.configure(
                text="\u2717 No extensions selected",
                text_color=Theme.get_color('error')
            )
            return

        count = len(self.view_model.selected_extensions)
        confirmed = messagebox.askyesno(
            "Confirm Uninstall",
            f"Are you sure you want to uninstall {count} extension(s)?\n\n"
            "This will remove them from Firefox Enterprise Policies."
        )
        if not confirmed:
            return

        self.on_uninstall_extensions()

    def _on_extension_installing_changed(self, is_installing: bool):
        """Handle extension installation state change."""
        if is_installing:
            self.install_extensions_btn.configure(state="disabled", text="Installing...")
            self.uninstall_extensions_btn.configure(state="disabled")
            self.extension_status_label.configure(
                text="Installing extensions...",
                text_color=Theme.get_color('info')
            )
        else:
            self.install_extensions_btn.configure(state="normal", text="Install Selected")
            self.uninstall_extensions_btn.configure(state="normal")

    def _on_extension_uninstalling_changed(self, is_uninstalling: bool):
        """Handle extension uninstallation state change."""
        if is_uninstalling:
            self.uninstall_extensions_btn.configure(state="disabled", text="Uninstalling...")
            self.install_extensions_btn.configure(state="disabled")
            self.extension_status_label.configure(
                text="Uninstalling extensions...",
                text_color=Theme.get_color('info')
            )
        else:
            self.uninstall_extensions_btn.configure(state="normal", text="Uninstall Selected")
            self.install_extensions_btn.configure(state="normal")

    def _on_extension_install_complete(self, success: bool):
        """Handle extension installation completion."""
        if not success:
            error_msg = self.view_model.extension_error_message or "Unknown error occurred"
            self.extension_status_label.configure(
                text=f"\u2717 {error_msg}",
                text_color=Theme.get_color('error')
            )
            return

        results = self.view_model.extension_install_results
        installed = results.get('installed', [])
        failed = results.get('failed', {})
        total = results.get('total', 0)

        if failed:
            status_text = f"\u2713 Installed {len(installed)}/{total} extensions (some failed)"
        else:
            status_text = f"\u2713 Installed {len(installed)}/{total} extensions"

        self.extension_status_label.configure(
            text=status_text,
            text_color=Theme.get_color('success')
        )

    def _on_extension_uninstall_complete(self, success: bool):
        """Handle extension uninstallation completion."""
        if not success:
            error_msg = self.view_model.extension_uninstall_error_message or "Unknown error occurred"
            self.extension_status_label.configure(
                text=f"\u2717 {error_msg}",
                text_color=Theme.get_color('error')
            )
            return

        results = self.view_model.extension_uninstall_results
        uninstalled = results.get('uninstalled', [])
        failed = results.get('failed', {})
        total = results.get('total', 0)

        if failed:
            status_text = f"\u2713 Uninstalled {len(uninstalled)}/{total} extensions (some failed)"
        else:
            status_text = f"\u2713 Uninstalled {len(uninstalled)}/{total} extensions"

        self.extension_status_label.configure(
            text=status_text,
            text_color=Theme.get_color('success')
        )
