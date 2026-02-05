#!/usr/bin/env python3
"""
Utilities View - Dedicated tab for utility tools (Convert to Portable, Update Portable, etc.)
"""

import logging
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

from hardfox.presentation.view_models.utilities_view_model import UtilitiesViewModel
from hardfox.presentation.theme import Theme
from hardfox.application.use_cases.create_portable_from_download_use_case import CHANNEL_DISPLAY_NAMES

logger = logging.getLogger(__name__)


class UtilitiesView(ctk.CTkFrame):
    """
    Utilities tab providing tools like Convert to Portable Firefox
    and Update Portable Firefox.
    """

    def __init__(
        self,
        parent,
        view_model: UtilitiesViewModel,
        on_convert: Callable,
        on_cancel_convert: Callable,
        on_estimate_requested: Callable,
        on_check_update: Optional[Callable] = None,
        on_update: Optional[Callable] = None,
        on_cancel_update: Optional[Callable] = None,
        on_create_portable: Optional[Callable] = None,
        on_cancel_create: Optional[Callable] = None
    ):
        super().__init__(parent)
        self.view_model = view_model
        self.on_convert = on_convert
        self.on_cancel_convert = on_cancel_convert
        self.on_estimate_requested = on_estimate_requested
        self.on_check_update = on_check_update
        self.on_update = on_update
        self.on_cancel_update = on_cancel_update
        self.on_create_portable = on_create_portable
        self.on_cancel_create = on_cancel_create

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Build UI
        self._build_header()
        self._build_content()

        # Subscribe to ViewModel changes (Convert)
        self.view_model.subscribe('firefox_install_dir', self._on_firefox_dir_changed)
        self.view_model.subscribe('destination_dir', self._on_destination_changed)
        self.view_model.subscribe('estimated_size_mb', self._on_size_estimate_changed)
        self.view_model.subscribe('is_converting', self._on_converting_changed)
        self.view_model.subscribe('conversion_progress', self._on_progress_changed)
        self.view_model.subscribe('conversion_status', self._on_status_changed)
        self.view_model.subscribe('conversion_result', self._on_result_changed)

        # Subscribe to ViewModel changes (Update)
        self.view_model.subscribe('portable_path', self._on_portable_path_changed)
        self.view_model.subscribe('current_version', self._on_version_changed)
        self.view_model.subscribe('latest_version', self._on_version_changed)
        self.view_model.subscribe('update_available', self._on_update_available_changed)
        self.view_model.subscribe('is_checking_update', self._on_checking_update_changed)
        self.view_model.subscribe('is_updating', self._on_updating_changed)
        self.view_model.subscribe('update_progress', self._on_update_progress_changed)
        self.view_model.subscribe('update_status', self._on_update_status_changed)
        self.view_model.subscribe('update_result', self._on_update_result_changed)

        # Subscribe to ViewModel changes (Create Portable)
        self.view_model.subscribe('is_creating', self._on_creating_changed)
        self.view_model.subscribe('create_progress', self._on_create_progress_changed)
        self.view_model.subscribe('create_status', self._on_create_status_changed)
        self.view_model.subscribe('create_result', self._on_create_result_changed)

    def destroy(self):
        """Clean up ViewModel subscriptions."""
        self.view_model.unsubscribe('firefox_install_dir', self._on_firefox_dir_changed)
        self.view_model.unsubscribe('destination_dir', self._on_destination_changed)
        self.view_model.unsubscribe('estimated_size_mb', self._on_size_estimate_changed)
        self.view_model.unsubscribe('is_converting', self._on_converting_changed)
        self.view_model.unsubscribe('conversion_progress', self._on_progress_changed)
        self.view_model.unsubscribe('conversion_status', self._on_status_changed)
        self.view_model.unsubscribe('conversion_result', self._on_result_changed)

        self.view_model.unsubscribe('portable_path', self._on_portable_path_changed)
        self.view_model.unsubscribe('current_version', self._on_version_changed)
        self.view_model.unsubscribe('latest_version', self._on_version_changed)
        self.view_model.unsubscribe('update_available', self._on_update_available_changed)
        self.view_model.unsubscribe('is_checking_update', self._on_checking_update_changed)
        self.view_model.unsubscribe('is_updating', self._on_updating_changed)
        self.view_model.unsubscribe('update_progress', self._on_update_progress_changed)
        self.view_model.unsubscribe('update_status', self._on_update_status_changed)
        self.view_model.unsubscribe('update_result', self._on_update_result_changed)

        self.view_model.unsubscribe('is_creating', self._on_creating_changed)
        self.view_model.unsubscribe('create_progress', self._on_create_progress_changed)
        self.view_model.unsubscribe('create_status', self._on_create_status_changed)
        self.view_model.unsubscribe('create_result', self._on_create_result_changed)
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
        """Build the main content area with utility cards."""
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, pady=10, sticky="nsew", padx=10)
        content.grid_columnconfigure(0, weight=1)

        # Card 1: Convert to Portable
        self._build_convert_card(content, row=0)

        # Card 2: Update Portable Firefox
        self._build_update_card(content, row=1)

        # Card 3: Create Portable Firefox from Download
        self._build_create_card(content, row=2)

    # ===================================================================
    # Card 1: Convert to Portable Firefox
    # ===================================================================

    def _build_convert_card(self, parent, row):
        """Build the Convert to Portable Firefox card."""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
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
        r = 2
        ctk.CTkLabel(
            card,
            text="Firefox Installation:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=r, column=0, sticky="w", padx=20, pady=(5, 2))

        self.firefox_dir_label = ctk.CTkLabel(
            card,
            text="Detecting...",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_secondary')
        )
        self.firefox_dir_label.grid(row=r, column=1, columnspan=2, sticky="w", padx=10, pady=(5, 2))

        # --- Destination Folder ---
        r = 3
        ctk.CTkLabel(
            card,
            text="Destination Folder:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=r, column=0, sticky="w", padx=20, pady=(10, 2))

        dest_frame = ctk.CTkFrame(card, fg_color="transparent")
        dest_frame.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
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
        r = 4
        self.copy_profile_var = ctk.BooleanVar(value=False)
        self.copy_profile_cb = ctk.CTkCheckBox(
            card,
            text="Copy existing Firefox profile",
            variable=self.copy_profile_var,
            command=self._on_copy_profile_toggled,
            font=ctk.CTkFont(size=13)
        )
        self.copy_profile_cb.grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 2))

        profile_hint = ctk.CTkLabel(
            card,
            text="Includes bookmarks, saved passwords, extensions, and browsing history",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('text_tertiary')
        )
        profile_hint.grid(row=r + 1, column=0, columnspan=3, sticky="w", padx=45, pady=(0, 5))

        # --- Estimated Size ---
        r = 6
        self.size_label = ctk.CTkLabel(
            card,
            text="Estimated size: --",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_secondary')
        )
        self.size_label.grid(row=r, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 5))

        # --- Button Frame (Convert + Cancel) ---
        r = 7
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=r, column=0, columnspan=3, padx=20, pady=(10, 5))

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
            hover_color="#CC3333",
            font=ctk.CTkFont(size=14),
            height=40,
            width=100
        )
        # Cancel button hidden initially, shown during conversion

        # --- Progress Section (hidden initially) ---
        r = 8
        self.progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.progress_frame.grid(row=r, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 5))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()

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
        r = 9
        self.result_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=700,
            justify="left"
        )
        self.result_label.grid(row=r, column=0, columnspan=3, sticky="w", padx=20, pady=(5, 15))
        self.result_label.grid_remove()

    # ===================================================================
    # Card 2: Update Portable Firefox
    # ===================================================================

    def _build_update_card(self, parent, row):
        """Build the Update Portable Firefox card."""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(1, weight=1)

        # Card title
        ctk.CTkLabel(
            card,
            text="Update Portable Firefox",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text="Check for and install Firefox updates for an existing portable installation. "
                 "Downloads the latest version from Mozilla and replaces binaries while preserving your profile.",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_tertiary'),
            wraplength=700,
            justify="left"
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 15))

        # --- Portable Path ---
        r = 2
        ctk.CTkLabel(
            card,
            text="Portable Firefox Folder:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=r, column=0, sticky="w", padx=20, pady=(5, 2))

        path_frame = ctk.CTkFrame(card, fg_color="transparent")
        path_frame.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10, pady=(5, 2))
        path_frame.grid_columnconfigure(0, weight=1)

        self.portable_path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Select your portable Firefox folder...",
            height=32
        )
        self.portable_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.portable_path_entry.bind('<KeyRelease>', self._on_portable_path_entry_changed)

        ctk.CTkButton(
            path_frame,
            text="Browse...",
            command=self._on_browse_portable_clicked,
            width=80,
            height=32,
            fg_color=Theme.get_color('primary'),
            hover_color=Theme.get_color('primary_hover')
        ).grid(row=0, column=1)

        # --- Version Info ---
        r = 3
        self.version_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_secondary')
        )
        self.version_label.grid(row=r, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 5))
        self.version_label.grid_remove()

        # --- Button Frame (Check + Update + Cancel) ---
        r = 4
        update_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        update_btn_frame.grid(row=r, column=0, columnspan=3, padx=20, pady=(10, 5))

        self.check_update_btn = ctk.CTkButton(
            update_btn_frame,
            text="Check for Updates",
            command=self._on_check_update_clicked,
            fg_color=Theme.get_color('primary'),
            hover_color=Theme.get_color('primary_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        self.check_update_btn.pack(side="left", padx=(0, 10))

        self.update_btn = ctk.CTkButton(
            update_btn_frame,
            text="Update Firefox",
            command=self._on_update_clicked,
            fg_color=Theme.get_color('secondary'),
            hover_color=Theme.get_color('secondary_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        # Hidden initially, shown when update is available
        # Don't pack yet

        self.cancel_update_btn = ctk.CTkButton(
            update_btn_frame,
            text="Cancel",
            command=self._on_cancel_update_clicked,
            fg_color=Theme.get_color('error'),
            hover_color="#CC3333",
            font=ctk.CTkFont(size=14),
            height=40,
            width=100
        )
        # Hidden initially, shown during update

        # --- Update Progress Section (hidden initially) ---
        r = 5
        self.update_progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.update_progress_frame.grid(row=r, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 5))
        self.update_progress_frame.grid_columnconfigure(0, weight=1)
        self.update_progress_frame.grid_remove()

        self.update_progress_bar = ctk.CTkProgressBar(self.update_progress_frame)
        self.update_progress_bar.grid(row=0, column=0, sticky="ew", pady=(5, 2))
        self.update_progress_bar.set(0)

        self.update_status_label = ctk.CTkLabel(
            self.update_progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('text_secondary')
        )
        self.update_status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # --- Update Result Section (hidden initially) ---
        r = 6
        self.update_result_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=700,
            justify="left"
        )
        self.update_result_label.grid(row=r, column=0, columnspan=3, sticky="w", padx=20, pady=(5, 15))
        self.update_result_label.grid_remove()

    # ===================================================================
    # Card 3: Create Portable Firefox from Download
    # ===================================================================

    def _build_create_card(self, parent, row):
        """Build the Create Portable Firefox from Download card."""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(1, weight=1)

        # Card title
        ctk.CTkLabel(
            card,
            text="Create Portable Firefox",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text="Download Firefox directly from Mozilla and create a fresh portable installation. "
                 "Choose a channel (Stable, Beta, or Developer Edition) and a destination folder.",
            font=ctk.CTkFont(size=12),
            text_color=Theme.get_color('text_tertiary'),
            wraplength=700,
            justify="left"
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 15))

        # --- Channel Selector ---
        r = 2
        ctk.CTkLabel(
            card,
            text="Channel:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=r, column=0, sticky="w", padx=20, pady=(5, 2))

        self.create_channel_var = ctk.StringVar(value="Stable")
        self.create_channel_dropdown = ctk.CTkOptionMenu(
            card,
            variable=self.create_channel_var,
            values=["Stable", "Beta", "Developer Edition"],
            command=self._on_create_channel_changed,
            width=200,
            height=32,
            fg_color=Theme.get_color('primary'),
            button_color=Theme.get_color('primary'),
            button_hover_color=Theme.get_color('primary_hover')
        )
        self.create_channel_dropdown.grid(row=r, column=1, sticky="w", padx=10, pady=(5, 2))

        # --- Destination Folder ---
        r = 3
        ctk.CTkLabel(
            card,
            text="Destination Folder:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=r, column=0, sticky="w", padx=20, pady=(10, 2))

        create_dest_frame = ctk.CTkFrame(card, fg_color="transparent")
        create_dest_frame.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        create_dest_frame.grid_columnconfigure(0, weight=1)

        self.create_dest_entry = ctk.CTkEntry(
            create_dest_frame,
            placeholder_text="Select a folder for the new portable installation...",
            height=32
        )
        self.create_dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.create_dest_entry.bind('<KeyRelease>', self._on_create_dest_entry_changed)

        ctk.CTkButton(
            create_dest_frame,
            text="Browse...",
            command=self._on_browse_create_dest_clicked,
            width=80,
            height=32,
            fg_color=Theme.get_color('primary'),
            hover_color=Theme.get_color('primary_hover')
        ).grid(row=0, column=1)

        # --- Button Frame (Create + Cancel) ---
        r = 4
        create_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        create_btn_frame.grid(row=r, column=0, columnspan=3, padx=20, pady=(10, 5))

        self.create_btn = ctk.CTkButton(
            create_btn_frame,
            text="Create Portable Firefox",
            command=self._on_create_clicked,
            fg_color=Theme.get_color('secondary'),
            hover_color=Theme.get_color('secondary_hover'),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            state="disabled"
        )
        self.create_btn.pack(side="left", padx=(0, 10))

        self.cancel_create_btn = ctk.CTkButton(
            create_btn_frame,
            text="Cancel",
            command=self._on_cancel_create_clicked,
            fg_color=Theme.get_color('error'),
            hover_color="#CC3333",
            font=ctk.CTkFont(size=14),
            height=40,
            width=100
        )
        # Cancel button hidden initially

        # --- Progress Section (hidden initially) ---
        r = 5
        self.create_progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.create_progress_frame.grid(row=r, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 5))
        self.create_progress_frame.grid_columnconfigure(0, weight=1)
        self.create_progress_frame.grid_remove()

        self.create_progress_bar = ctk.CTkProgressBar(self.create_progress_frame)
        self.create_progress_bar.grid(row=0, column=0, sticky="ew", pady=(5, 2))
        self.create_progress_bar.set(0)

        self.create_status_label = ctk.CTkLabel(
            self.create_progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('text_secondary')
        )
        self.create_status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # --- Result Section (hidden initially) ---
        r = 6
        self.create_result_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=700,
            justify="left"
        )
        self.create_result_label.grid(row=r, column=0, columnspan=3, sticky="w", padx=20, pady=(5, 15))
        self.create_result_label.grid_remove()

    # ===================================================================
    # Convert to Portable - UI Event Handlers
    # ===================================================================

    def _on_browse_clicked(self):
        """Handle Browse button click for conversion destination."""
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
            logger.warning("_on_convert_clicked: Firefox installation not detected")
            return

        if not self.view_model.destination_dir:
            logger.warning("_on_convert_clicked: no destination folder selected")
            return

        self.on_convert()

    def _on_cancel_clicked(self):
        """Handle Cancel button click for conversion."""
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

    # ===================================================================
    # Convert to Portable - ViewModel Subscription Handlers
    # ===================================================================

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

    # ===================================================================
    # Update Portable Firefox - UI Event Handlers
    # ===================================================================

    def _on_browse_portable_clicked(self):
        """Handle Browse button click for portable path."""
        folder = filedialog.askdirectory(
            title="Select Portable Firefox Folder"
        )
        if folder:
            self.portable_path_entry.delete(0, "end")
            self.portable_path_entry.insert(0, folder)
            self.view_model.portable_path = folder
            self._update_check_button_state()

    def _on_portable_path_entry_changed(self, event=None):
        """Handle manual entry in portable path field."""
        self.view_model.portable_path = self.portable_path_entry.get()
        self._update_check_button_state()

    def _on_check_update_clicked(self):
        """Handle Check for Updates button click."""
        if not self.view_model.portable_path:
            logger.warning("_on_check_update_clicked: no portable path selected")
            return

        portable = Path(self.view_model.portable_path)
        if not portable.exists():
            logger.warning("_on_check_update_clicked: folder does not exist: %s", portable)
            return

        # Validate it looks like a portable Firefox installation
        has_app = (portable / "App").exists()
        if not has_app:
            logger.warning("_on_check_update_clicked: not a valid portable installation (no App dir)")
            return

        if self.on_check_update:
            self.on_check_update()

    def _on_update_clicked(self):
        """Handle Update Firefox button click."""
        if not self.view_model.update_available:
            return

        if self.on_update:
            self.on_update()

    def _on_cancel_update_clicked(self):
        """Handle Cancel button click during update."""
        if self.on_cancel_update:
            self.on_cancel_update()

    def _update_check_button_state(self):
        """Enable/disable check button based on portable path."""
        has_path = bool(self.view_model.portable_path)
        is_busy = self.view_model.is_checking_update or self.view_model.is_updating

        if has_path and not is_busy:
            self.check_update_btn.configure(state="normal")
        else:
            self.check_update_btn.configure(state="disabled")

    def _update_update_button_state(self):
        """Show/enable update button when update is available."""
        if self.view_model.update_available and not self.view_model.is_updating:
            self.update_btn.pack(side="left", padx=(0, 10))
            self.update_btn.configure(state="normal")
        else:
            self.update_btn.pack_forget()

    # ===================================================================
    # Update Portable Firefox - ViewModel Subscription Handlers
    # ===================================================================

    def _on_portable_path_changed(self, value: str):
        """Handle portable path changes."""
        self._update_check_button_state()
        # Reset version info when path changes
        self.version_label.grid_remove()
        self.update_result_label.grid_remove()
        self.update_btn.pack_forget()

    def _on_version_changed(self, value: str):
        """Update version info display."""
        current = self.view_model.current_version
        latest = self.view_model.latest_version

        if current and latest:
            if self.view_model.update_available:
                self.version_label.configure(
                    text=f"Current: {current}  \u2192  Latest: {latest}",
                    text_color=Theme.get_color('warning')
                )
            else:
                self.version_label.configure(
                    text=f"Current: {current} (up to date)",
                    text_color=Theme.get_color('success')
                )
            self.version_label.grid()
        elif current:
            self.version_label.configure(
                text=f"Current: {current}",
                text_color=Theme.get_color('text_secondary')
            )
            self.version_label.grid()

    def _on_update_available_changed(self, value: bool):
        """Handle update availability change."""
        self._update_update_button_state()

    def _on_checking_update_changed(self, is_checking: bool):
        """Handle checking state change."""
        if is_checking:
            self.check_update_btn.configure(state="disabled", text="Checking...")
            self.update_result_label.grid_remove()
        else:
            self.check_update_btn.configure(text="Check for Updates")
            self._update_check_button_state()

    def _on_updating_changed(self, is_updating: bool):
        """Handle updating state change."""
        if is_updating:
            self.check_update_btn.configure(state="disabled")
            self.update_btn.pack_forget()
            self.cancel_update_btn.pack(side="left")
            self.update_progress_frame.grid()
            self.update_result_label.grid_remove()
            self.update_progress_bar.set(0)
        else:
            self.cancel_update_btn.pack_forget()
            self._update_check_button_state()
            self._update_update_button_state()

    def _on_update_progress_changed(self, value: float):
        """Update the update progress bar."""
        self.update_progress_bar.set(value)

    def _on_update_status_changed(self, value: str):
        """Update the update status text."""
        self.update_status_label.configure(text=value)

    def _on_update_result_changed(self, result: dict):
        """Handle update result."""
        if result is None:
            return

        self.update_result_label.grid()

        if result.get('success'):
            if result.get('already_up_to_date'):
                self.update_result_label.configure(
                    text=f"\u2713 Firefox is already up to date ({result.get('old_version', '')}).",
                    text_color=Theme.get_color('success')
                )
            else:
                self.update_result_label.configure(
                    text=(
                        f"\u2713 Firefox updated successfully!\n"
                        f"{result.get('old_version', '')} \u2192 {result.get('new_version', '')}\n"
                        f"Please restart Firefox to use the new version."
                    ),
                    text_color=Theme.get_color('success')
                )
            self.update_progress_frame.grid_remove()
        else:
            error_msg = result.get('error', 'Unknown error')
            self.update_result_label.configure(
                text=f"\u2717 Update failed: {error_msg}",
                text_color=Theme.get_color('error')
            )

    # ===================================================================
    # Create Portable from Download - UI Event Handlers
    # ===================================================================

    # Reverse of CHANNEL_DISPLAY_NAMES: display name -> internal key
    _CHANNEL_MAP = {v: k for k, v in CHANNEL_DISPLAY_NAMES.items()}

    def _on_create_channel_changed(self, choice: str):
        """Handle channel dropdown selection."""
        channel_key = self._CHANNEL_MAP.get(choice, "stable")
        self.view_model.create_channel = channel_key

    def _on_browse_create_dest_clicked(self):
        """Handle Browse button click for create destination."""
        folder = filedialog.askdirectory(
            title="Select Destination for New Portable Firefox"
        )
        if folder:
            self.create_dest_entry.delete(0, "end")
            self.create_dest_entry.insert(0, folder)
            self.view_model.create_destination_dir = folder
            self._update_create_button_state()

    def _on_create_dest_entry_changed(self, event=None):
        """Handle manual entry in create destination field."""
        self.view_model.create_destination_dir = self.create_dest_entry.get()
        self._update_create_button_state()

    def _on_create_clicked(self):
        """Handle Create Portable Firefox button click."""
        if not self.view_model.create_destination_dir:
            logger.warning("_on_create_clicked: no destination folder selected")
            return

        if self.on_create_portable:
            self.on_create_portable()

    def _on_cancel_create_clicked(self):
        """Handle Cancel button click during creation."""
        if self.on_cancel_create:
            self.on_cancel_create()

    def _update_create_button_state(self):
        """Enable/disable create button based on state."""
        has_dest = bool(self.view_model.create_destination_dir)
        is_creating = self.view_model.is_creating

        if has_dest and not is_creating:
            self.create_btn.configure(state="normal")
        else:
            self.create_btn.configure(state="disabled")

    # ===================================================================
    # Create Portable from Download - ViewModel Subscription Handlers
    # ===================================================================

    def _on_creating_changed(self, is_creating: bool):
        """Handle creation state change."""
        if is_creating:
            self.create_btn.configure(state="disabled", text="Creating...")
            self.cancel_create_btn.pack(side="left")
            self.create_progress_frame.grid()
            self.create_result_label.grid_remove()
            self.create_progress_bar.set(0)
        else:
            self.create_btn.configure(text="Create Portable Firefox")
            self.cancel_create_btn.pack_forget()
            self._update_create_button_state()

    def _on_create_progress_changed(self, value: float):
        """Update the create progress bar."""
        self.create_progress_bar.set(value)

    def _on_create_status_changed(self, value: str):
        """Update the create status text."""
        self.create_status_label.configure(text=value)

    def _on_create_result_changed(self, result: dict):
        """Handle create portable result."""
        if result is None:
            return

        self.create_result_label.grid()

        if result.get('success'):
            version = result.get('version', '')
            size_mb = result.get('size_mb', 0)
            channel = result.get('channel', '')
            channel_name = CHANNEL_DISPLAY_NAMES.get(channel, channel)

            self.create_result_label.configure(
                text=(
                    f"\u2713 Portable Firefox created successfully!\n"
                    f"Version: {version} ({channel_name}) | Size: {size_mb} MB\n"
                    f"Run MyFox.exe or FirefoxPortable.bat to launch."
                ),
                text_color=Theme.get_color('success')
            )
            self.create_progress_frame.grid_remove()
        else:
            error_msg = result.get('error', 'Unknown error')
            self.create_result_label.configure(
                text=f"\u2717 Creation failed: {error_msg}",
                text_color=Theme.get_color('error')
            )
