#!/usr/bin/env python3
"""
Utilities View - Dedicated tab for utility tools (Convert to Portable, etc.)
"""

import logging
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable

from hardzilla.presentation.view_models.utilities_view_model import UtilitiesViewModel
from hardzilla.presentation.theme import Theme

logger = logging.getLogger(__name__)


class UtilitiesView(ctk.CTkFrame):
    """
    Utilities tab providing tools like Convert to Portable Firefox.
    """

    def __init__(
        self,
        parent,
        view_model: UtilitiesViewModel,
        on_convert: Callable,
        on_cancel_convert: Callable,
        on_estimate_requested: Callable,
        on_back: Callable
    ):
        super().__init__(parent)
        self.view_model = view_model
        self.on_convert = on_convert
        self.on_cancel_convert = on_cancel_convert
        self.on_estimate_requested = on_estimate_requested
        self.on_back = on_back

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Build UI
        self._build_header()
        self._build_content()
        self._build_navigation()

        # Subscribe to ViewModel changes
        self.view_model.subscribe('firefox_install_dir', self._on_firefox_dir_changed)
        self.view_model.subscribe('destination_dir', self._on_destination_changed)
        self.view_model.subscribe('estimated_size_mb', self._on_size_estimate_changed)
        self.view_model.subscribe('is_converting', self._on_converting_changed)
        self.view_model.subscribe('conversion_progress', self._on_progress_changed)
        self.view_model.subscribe('conversion_status', self._on_status_changed)
        self.view_model.subscribe('conversion_result', self._on_result_changed)

    def destroy(self):
        """Clean up ViewModel subscriptions."""
        self.view_model.unsubscribe('firefox_install_dir', self._on_firefox_dir_changed)
        self.view_model.unsubscribe('destination_dir', self._on_destination_changed)
        self.view_model.unsubscribe('estimated_size_mb', self._on_size_estimate_changed)
        self.view_model.unsubscribe('is_converting', self._on_converting_changed)
        self.view_model.unsubscribe('conversion_progress', self._on_progress_changed)
        self.view_model.unsubscribe('conversion_status', self._on_status_changed)
        self.view_model.unsubscribe('conversion_result', self._on_result_changed)
        super().destroy()

    def _build_header(self):
        """Build screen header."""
        header = ctk.CTkLabel(
            self,
            text="Utilities",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

    def _build_content(self):
        """Build the main content area with Convert to Portable card."""
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, pady=10, sticky="nsew", padx=10)
        content.grid_columnconfigure(0, weight=1)

        # Convert to Portable card
        card = ctk.CTkFrame(content, corner_radius=12)
        card.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(1, weight=1)

        # Card title
        title = ctk.CTkLabel(
            card,
            text="Convert to Portable Firefox",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(15, 5))

        desc = ctk.CTkLabel(
            card,
            text="Create a portable Firefox installation that can run from a USB drive or any folder, "
                 "independent of the system Firefox installation.",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_tertiary'),
            wraplength=700,
            justify="left"
        )
        desc.grid(row=1, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 15))

        # --- Firefox Installation ---
        row = 2
        ctk.CTkLabel(
            card,
            text="Firefox Installation:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(5, 2))

        self.firefox_dir_label = ctk.CTkLabel(
            card,
            text="Detecting...",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_secondary')
        )
        self.firefox_dir_label.grid(row=row, column=1, columnspan=2, sticky="w", padx=10, pady=(5, 2))

        # --- Destination Folder ---
        row = 3
        ctk.CTkLabel(
            card,
            text="Destination Folder:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 2))

        dest_frame = ctk.CTkFrame(card, fg_color="transparent")
        dest_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        dest_frame.grid_columnconfigure(0, weight=1)

        self.dest_entry = ctk.CTkEntry(
            dest_frame,
            placeholder_text="Select a folder for the portable installation...",
            height=32
        )
        self.dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.dest_entry.bind('<KeyRelease>', self._on_dest_entry_changed)

        browse_btn = ctk.CTkButton(
            dest_frame,
            text="Browse...",
            command=self._on_browse_clicked,
            width=80,
            height=32,
            fg_color=Theme.get_color('primary'),
            hover_color=Theme.get_color('primary_hover')
        )
        browse_btn.grid(row=0, column=1)

        # --- Copy Profile Checkbox ---
        row = 4
        self.copy_profile_var = ctk.BooleanVar(value=False)
        self.copy_profile_cb = ctk.CTkCheckBox(
            card,
            text="Copy existing Firefox profile",
            variable=self.copy_profile_var,
            command=self._on_copy_profile_toggled,
            font=ctk.CTkFont(size=13)
        )
        self.copy_profile_cb.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 2))

        profile_hint = ctk.CTkLabel(
            card,
            text="Includes bookmarks, saved passwords, extensions, and browsing history",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('text_tertiary')
        )
        profile_hint.grid(row=row + 1, column=0, columnspan=3, sticky="w", padx=45, pady=(0, 5))

        # --- Estimated Size ---
        row = 6
        self.size_label = ctk.CTkLabel(
            card,
            text="Estimated size: --",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_secondary')
        )
        self.size_label.grid(row=row, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 5))

        # --- Button Frame (Convert + Cancel) ---
        row = 7
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=3, padx=20, pady=(10, 5))

        self.convert_btn = ctk.CTkButton(
            btn_frame,
            text="Convert to Portable",
            command=self._on_convert_clicked,
            fg_color=Theme.get_color('secondary'),
            hover_color=Theme.get_color('secondary_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        self.convert_btn.pack(side="left", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel_clicked,
            fg_color=Theme.get_color('error'),
            hover_color="#DC2626",
            font=ctk.CTkFont(size=14),
            height=40,
            width=100
        )
        # Cancel button hidden initially, shown during conversion
        # Don't pack yet

        # --- Progress Section (hidden initially) ---
        row = 8
        self.progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.progress_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 5))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()  # Hidden initially

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(5, 2))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('text_secondary')
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # --- Result Section (hidden initially) ---
        row = 9
        self.result_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=700,
            justify="left"
        )
        self.result_label.grid(row=row, column=0, columnspan=3, sticky="w", padx=20, pady=(5, 15))
        self.result_label.grid_remove()  # Hidden initially

    def _build_navigation(self):
        """Build navigation buttons (back only)."""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=2, column=0, pady=(10, 20), sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            nav_frame,
            text="\u2190 Back",
            command=self.on_back
        )
        back_btn.grid(row=0, column=0, padx=10, pady=10)

    # --- UI Event Handlers ---

    def _on_browse_clicked(self):
        """Handle Browse button click."""
        folder = filedialog.askdirectory(
            title="Select Destination for Portable Firefox"
        )
        if folder:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, folder)
            self.view_model.destination_dir = folder
            self.on_estimate_requested()

    def _on_dest_entry_changed(self, event=None):
        """Handle manual entry in destination field."""
        self.view_model.destination_dir = self.dest_entry.get()
        self._update_convert_button_state()

    def _on_copy_profile_toggled(self):
        """Handle copy profile checkbox toggle."""
        self.view_model.copy_profile = self.copy_profile_var.get()
        self.on_estimate_requested()

    def _on_convert_clicked(self):
        """Handle Convert button click."""
        if not self.view_model.firefox_install_dir:
            messagebox.showerror(
                "Error",
                "Firefox installation not detected.\n"
                "Please select a Firefox profile in the Setup tab."
            )
            return

        if not self.view_model.destination_dir:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        # Check if destination already has files
        dest = Path(self.view_model.destination_dir)
        if dest.exists() and any(dest.iterdir()):
            if not messagebox.askyesno(
                "Destination Not Empty",
                f"The folder '{dest}' already contains files.\n\n"
                "Existing files may be overwritten. Continue?",
                icon='warning'
            ):
                return

        self.on_convert()

    def _on_cancel_clicked(self):
        """Handle Cancel button click."""
        if messagebox.askyesno(
            "Cancel Conversion",
            "Are you sure you want to cancel the conversion?\n\n"
            "Partially copied files will remain in the destination folder.",
            icon='warning'
        ):
            self.on_cancel_convert()

    def _update_convert_button_state(self):
        """Enable/disable convert button based on state."""
        has_firefox = bool(self.view_model.firefox_install_dir)
        has_dest = bool(self.view_model.destination_dir)
        is_converting = self.view_model.is_converting

        if has_firefox and has_dest and not is_converting:
            self.convert_btn.configure(state="normal")
        else:
            self.convert_btn.configure(state="disabled")

    # --- ViewModel Subscription Handlers ---

    def _on_firefox_dir_changed(self, value: str):
        """Update Firefox installation label."""
        if value:
            self.firefox_dir_label.configure(
                text=value,
                text_color=Theme.get_color('success')
            )
        else:
            self.firefox_dir_label.configure(
                text="Not detected - select a Firefox profile in Setup tab",
                text_color=Theme.get_color('warning')
            )
        self._update_convert_button_state()

    def _on_destination_changed(self, value: str):
        """Update UI when destination changes."""
        self._update_convert_button_state()

    def _on_size_estimate_changed(self, value: float):
        """Update estimated size label."""
        if value > 0:
            if value >= 1024:
                self.size_label.configure(text=f"Estimated size: {value / 1024:.1f} GB")
            else:
                self.size_label.configure(text=f"Estimated size: {value:.0f} MB")
        else:
            self.size_label.configure(text="Estimated size: --")

    def _on_converting_changed(self, is_converting: bool):
        """Handle conversion state change."""
        if is_converting:
            self.convert_btn.configure(state="disabled", text="Converting...")
            self.cancel_btn.pack(side="left")  # Show cancel button
            self.progress_frame.grid()  # Show progress
            self.result_label.grid_remove()  # Hide previous result
            self.progress_bar.set(0)
        else:
            self.convert_btn.configure(text="Convert to Portable")
            self.cancel_btn.pack_forget()  # Hide cancel button
            self._update_convert_button_state()

    def _on_progress_changed(self, value: float):
        """Update progress bar."""
        self.progress_bar.set(value)

    def _on_status_changed(self, value: str):
        """Update status text."""
        self.status_label.configure(text=value)

    def _on_result_changed(self, result: dict):
        """Handle conversion result."""
        if result is None:
            return

        self.result_label.grid()  # Show result

        if result.get('success'):
            files_failed = result.get('files_failed', 0)
            msg = (
                f"\u2713 Portable Firefox created successfully!\n"
                f"Files copied: {result.get('files_copied', 0)} | "
                f"Size: {result.get('size_mb', 0)} MB\n"
                f"Run FirefoxPortable.bat to launch."
            )

            if files_failed > 0:
                failed_list = result.get('failed_files', [])
                msg += f"\n\n\u26a0 Warning: {files_failed} file(s) could not be copied."
                if failed_list:
                    msg += "\nFailed: " + ", ".join(failed_list[:5])
                    if files_failed > 5:
                        msg += f" (and {files_failed - 5} more)"

                self.result_label.configure(
                    text=msg,
                    text_color=Theme.get_color('warning')
                )
            else:
                self.result_label.configure(
                    text=msg,
                    text_color=Theme.get_color('success')
                )
            self.progress_frame.grid_remove()  # Hide progress bar on success
        else:
            error_msg = result.get('error', 'Unknown error')
            self.result_label.configure(
                text=f"\u2717 Conversion failed: {error_msg}",
                text_color=Theme.get_color('error')
            )
