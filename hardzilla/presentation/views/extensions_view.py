#!/usr/bin/env python3
"""
Extensions View - Dedicated tab for privacy extension management.
"""

import logging
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable

from hardzilla.presentation.view_models import ApplyViewModel
from hardzilla.presentation.theme import Theme
from hardzilla.metadata.extensions_metadata import EXTENSIONS_METADATA
from hardzilla.domain.entities.extension import Extension
from hardzilla.presentation.widgets.extension_row import ExtensionRow

logger = logging.getLogger(__name__)


class ExtensionsView(ctk.CTkFrame):
    """
    Extensions tab for selecting and installing Firefox privacy extensions.
    """

    def __init__(
        self,
        parent,
        view_model: ApplyViewModel,
        on_install_extensions: Callable,
        on_next: Callable,
        on_back: Callable
    ):
        logger.debug("ExtensionsView.__init__: starting initialization")
        super().__init__(parent)
        self.view_model = view_model
        self.on_install_extensions = on_install_extensions
        self.on_next = on_next
        self.on_back = on_back
        self.extension_rows = []

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Build UI
        logger.debug("ExtensionsView.__init__: building header")
        self._build_header()
        logger.debug("ExtensionsView.__init__: building extensions section")
        self._build_extensions_section()
        logger.debug("ExtensionsView.__init__: building navigation")
        self._build_navigation()

        # Subscribe to view model changes
        logger.debug("ExtensionsView.__init__: subscribing to ViewModel events")
        self.view_model.subscribe('extension_install_success', self._on_extension_install_complete)
        self.view_model.subscribe('is_installing_extensions', self._on_extension_installing_changed)
        logger.debug("ExtensionsView.__init__: initialization complete, %d extension rows created", len(self.extension_rows))

    def destroy(self):
        """Clean up ViewModel subscriptions before destroying widget."""
        logger.debug("ExtensionsView.destroy: unsubscribing from ViewModel events")
        self.view_model.unsubscribe('extension_install_success', self._on_extension_install_complete)
        self.view_model.unsubscribe('is_installing_extensions', self._on_extension_installing_changed)
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
            logger.debug("_build_extensions_section: creating row for '%s' (id=%s, checked=%s)", ext_data['name'], ext_id, is_checked)
            row = ExtensionRow(
                extensions_frame,
                extension=extension,
                on_toggle=self._on_extension_toggled,
                initial_checked=is_checked
            )
            row.pack(fill="x", pady=2)
            self.extension_rows.append(row)

        # Seed ViewModel if it has no selections yet (first construction)
        if not self.view_model.selected_extensions:
            logger.debug("_build_extensions_section: seeding ViewModel with all %d extension IDs", len(all_ext_ids))
            self.view_model.selected_extensions = all_ext_ids
        else:
            logger.debug("_build_extensions_section: ViewModel already has %d selections, skipping seed", len(self.view_model.selected_extensions))

        # Install button
        self.install_extensions_btn = ctk.CTkButton(
            section,
            text="Install Extensions",
            command=self._on_install_extensions_clicked,
            fg_color=Theme.get_color('accent'),
            hover_color=Theme.get_color('accent_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.install_extensions_btn.grid(row=2, column=0, padx=20, pady=(10, 10))

        # Status label
        self.extension_status_label = ctk.CTkLabel(
            section,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.extension_status_label.grid(row=3, column=0, padx=20, pady=(0, 10))

    def _build_navigation(self):
        """Build navigation buttons."""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=3, column=0, pady=(10, 20), sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            nav_frame,
            text="\u2190 Back",
            command=self.on_back
        )
        back_btn.grid(row=0, column=0, padx=10, pady=10)

        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next \u2192",
            command=self.on_next
        )
        next_btn.grid(row=0, column=2, padx=10, pady=10)

    def _select_all(self):
        """Select all extensions."""
        all_ids = [row.extension.extension_id for row in self.extension_rows]
        logger.debug("_select_all: selecting all %d extensions", len(all_ids))
        for row in self.extension_rows:
            row.set_checked(True)
        self.view_model.selected_extensions = all_ids
        logger.debug("_select_all: ViewModel.selected_extensions updated to %d items", len(self.view_model.selected_extensions))

    def _deselect_all(self):
        """Deselect all extensions."""
        logger.debug("_deselect_all: clearing all extension selections")
        for row in self.extension_rows:
            row.set_checked(False)
        self.view_model.selected_extensions = []
        logger.debug("_deselect_all: ViewModel.selected_extensions cleared")

    def _on_extension_toggled(self, extension_id: str, checked: bool):
        """Handle extension checkbox toggle."""
        logger.debug("_on_extension_toggled: ext_id=%s, checked=%s", extension_id, checked)
        current = list(self.view_model.selected_extensions)
        if checked:
            if extension_id not in current:
                current.append(extension_id)
        else:
            if extension_id in current:
                current.remove(extension_id)
        self.view_model.selected_extensions = current
        logger.debug("_on_extension_toggled: ViewModel now has %d selected extensions", len(current))

    def _on_install_extensions_clicked(self):
        """Handle install extensions button click."""
        logger.debug("_on_install_extensions_clicked: button pressed")
        logger.debug("_on_install_extensions_clicked: on_install_extensions callback=%s", self.on_install_extensions)
        logger.debug("_on_install_extensions_clicked: firefox_path=%s", self.view_model.firefox_path)
        logger.debug("_on_install_extensions_clicked: selected_extensions=%s (%d)", self.view_model.selected_extensions, len(self.view_model.selected_extensions))

        if not self.on_install_extensions:
            logger.warning("_on_install_extensions_clicked: no callback configured, aborting")
            messagebox.showerror("Error", "Extension installation not configured")
            return

        if not self.view_model.firefox_path:
            logger.warning("_on_install_extensions_clicked: no firefox_path set, aborting")
            messagebox.showerror(
                "Error",
                "Please select a Firefox profile first (in Setup & Presets tab)"
            )
            return

        if not self.view_model.selected_extensions:
            logger.warning("_on_install_extensions_clicked: no extensions selected, aborting")
            messagebox.showerror(
                "Error",
                "Please select at least one extension to install"
            )
            return

        if not messagebox.askyesno(
            "Confirm Installation",
            f"This will install {len(self.view_model.selected_extensions)} extension(s) "
            f"to your Firefox installation.\n\n"
            f"Extensions will be auto-installed on next Firefox start.\n\n"
            f"Continue?",
            icon='question'
        ):
            logger.debug("_on_install_extensions_clicked: user cancelled installation")
            return

        logger.info("_on_install_extensions_clicked: user confirmed, calling on_install_extensions callback")
        self.on_install_extensions()

    def _on_extension_installing_changed(self, is_installing: bool):
        """Handle extension installation state change."""
        logger.debug("_on_extension_installing_changed: is_installing=%s", is_installing)
        if is_installing:
            self.install_extensions_btn.configure(state="disabled", text="Installing...")
            self.extension_status_label.configure(
                text="Installing extensions...",
                text_color=Theme.get_color('info')
            )
        else:
            logger.debug("_on_extension_installing_changed: re-enabling install button")
            self.install_extensions_btn.configure(state="normal", text="Install Extensions")

    def _on_extension_install_complete(self, success: bool):
        """Handle extension installation completion."""
        logger.debug("_on_extension_install_complete: success=%s", success)
        if not success:
            error_msg = self.view_model.extension_error_message or "Unknown error occurred"
            logger.error("_on_extension_install_complete: installation failed - %s", error_msg)
            self.extension_status_label.configure(
                text="\u2717 Extension installation failed",
                text_color=Theme.get_color('error')
            )
            messagebox.showerror("Extension Installation Failed", error_msg)
            return

        results = self.view_model.extension_install_results
        installed = results.get('installed', [])
        failed = results.get('failed', {})
        total = results.get('total', 0)

        logger.info("_on_extension_install_complete: installed %d/%d extensions", len(installed), total)
        if installed:
            logger.debug("_on_extension_install_complete: installed extensions: %s", installed)
        if failed:
            logger.warning("_on_extension_install_complete: failed extensions: %s", failed)

        message = f"\u2713 Installed {len(installed)} of {total} extension(s)\n\n"

        if failed:
            message += "Failed:\n"
            for name, err in failed.items():
                message += f"  \u2022 {name}: {err}\n"
            message += "\n"

        message += "\u26a0 Restart Firefox to activate extensions."

        self.extension_status_label.configure(
            text=f"\u2713 Installed {len(installed)}/{total} extensions",
            text_color=Theme.get_color('success')
        )

        messagebox.showinfo("Extensions Installed", message)
