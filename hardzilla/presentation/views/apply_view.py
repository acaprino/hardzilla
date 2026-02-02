#!/usr/bin/env python3
"""
Apply View - Screen 3 (Apply Settings to Firefox)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Callable
from pathlib import Path

from hardzilla.presentation.view_models import ApplyViewModel


class ApplyView(ctk.CTkFrame):
    """
    Screen 3: Apply Settings View.

    Final screen where user applies settings to Firefox profile.
    """

    def __init__(
        self,
        parent,
        view_model: ApplyViewModel,
        on_apply: Callable,
        on_back: Callable
    ):
        """
        Initialize Apply View.

        Args:
            parent: Parent widget
            view_model: ApplyViewModel for state management
            on_apply: Callback for Apply button
            on_back: Callback for Back button
        """
        super().__init__(parent)
        self.view_model = view_model
        self.on_apply = on_apply
        self.on_back = on_back

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Build UI
        self._build_header()
        self._build_summary()
        self._build_apply_options()
        self._build_navigation()

        # Subscribe to view model changes
        self.view_model.subscribe('apply_success', self._on_apply_complete)
        self.view_model.subscribe('error_message', self._on_error)
        # Subscribe to count changes for reactive summary updates
        self.view_model.subscribe('base_count', self._on_counts_updated)
        self.view_model.subscribe('advanced_count', self._on_counts_updated)

    def _build_header(self):
        """Build screen header"""
        header = ctk.CTkLabel(
            self,
            text="Step 3: Apply Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, pady=(0, 20), sticky="w")

    def _build_summary(self):
        """Build summary section"""
        section = ctk.CTkFrame(self)
        section.grid(row=1, column=0, pady=10, sticky="ew", padx=10)

        title = ctk.CTkLabel(
            section,
            text="Ready to Apply",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=20, pady=(10, 5))

        self.summary_label = ctk.CTkLabel(
            section,
            text="Profile: None\nBASE: 0 settings | ADVANCED: 0 settings"
        )
        self.summary_label.pack(padx=20, pady=10)

        # Update from view model
        self._update_summary()

    def _build_apply_options(self):
        """Build apply options section"""
        section = ctk.CTkFrame(self)
        section.grid(row=2, column=0, pady=10, sticky="ew", padx=10)

        # Apply mode selection
        mode_label = ctk.CTkLabel(
            section,
            text="What to apply:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        mode_label.pack(padx=20, pady=(10, 5), anchor="w")

        self.mode_var = ctk.StringVar(value="BOTH")

        modes = [
            ("Apply BOTH (Recommended)", "BOTH", "#2FA572"),
            ("Apply BASE only (prefs.js)", "BASE", "#3B8ED0"),
            ("Apply ADVANCED only (user.js)", "ADVANCED", "#9B59B6")
        ]

        for label, value, color in modes:
            rb = ctk.CTkRadioButton(
                section,
                text=label,
                variable=self.mode_var,
                value=value,
                command=lambda v=value: self._on_mode_changed(v)
            )
            rb.pack(padx=40, pady=5, anchor="w")

        # Save to JSON option
        save_frame = ctk.CTkFrame(section)
        save_frame.pack(padx=20, pady=10, fill="x")

        self.save_json_var = ctk.BooleanVar(value=False)
        save_cb = ctk.CTkCheckBox(
            save_frame,
            text="Save profile as JSON for later reuse",
            variable=self.save_json_var,
            command=self._on_save_json_toggled
        )
        save_cb.pack(side="left", padx=10, pady=10)

        # Warning
        warning_label = ctk.CTkLabel(
            section,
            text="⚠️  Important: Close Firefox before applying!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFA500"
        )
        warning_label.pack(padx=20, pady=10)

    def _build_navigation(self):
        """Build navigation buttons"""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=3, column=0, pady=20, sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=self.on_back
        )
        back_btn.grid(row=0, column=0, padx=10, pady=10)

        self.apply_btn = ctk.CTkButton(
            nav_frame,
            text="Apply Settings",
            command=self._on_apply_clicked,
            fg_color="#2FA572",
            hover_color="#238C5C",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.apply_btn.grid(row=0, column=2, padx=10, pady=10)

    def _update_summary(self):
        """Update summary display"""
        if self.view_model.profile:
            profile = self.view_model.profile
            text = f"Profile: {profile.name}\n"
            text += f"BASE: {self.view_model.base_count} settings | "
            text += f"ADVANCED: {self.view_model.advanced_count} settings\n"
            text += f"Firefox Profile: {self.view_model.firefox_path or 'Not set'}"
            self.summary_label.configure(text=text)

    def _on_counts_updated(self, value):
        """Handle count updates from view model"""
        self._update_summary()

    def _on_mode_changed(self, mode: str):
        """Handle apply mode change"""
        self.view_model.apply_mode = mode

    def _on_save_json_toggled(self):
        """Handle save to JSON checkbox"""
        self.view_model.save_to_json = self.save_json_var.get()

    def _on_apply_clicked(self):
        """Handle apply button click"""
        # Confirm action
        if not messagebox.askyesno(
            "Confirm Apply",
            "This will modify your Firefox profile.\n\n"
            "Make sure Firefox is closed!\n\n"
            "Continue?",
            icon='warning'
        ):
            return

        # Disable button
        self.apply_btn.configure(state="disabled", text="Applying...")

        try:
            # Call controller
            self.on_apply()
        except Exception as e:
            self.apply_btn.configure(state="normal", text="Apply Settings")
            messagebox.showerror("Error", f"Failed to apply settings:\n{str(e)}")

    def _on_apply_complete(self, success: bool):
        """Handle apply completion"""
        self.apply_btn.configure(state="normal", text="Apply Settings")

        if success:
            base = self.view_model.applied_base_count
            adv = self.view_model.applied_advanced_count

            messagebox.showinfo(
                "Success!",
                f"Settings applied successfully!\n\n"
                f"BASE settings: {base}\n"
                f"ADVANCED settings: {adv}\n\n"
                f"Restart Firefox to activate the new settings.",
                icon='info'
            )

    def _on_error(self, error_msg: str):
        """Handle error"""
        if error_msg:
            messagebox.showerror("Error", error_msg)
