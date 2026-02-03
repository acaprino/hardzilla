#!/usr/bin/env python3
"""
Apply View - Screen 3 (Apply Settings to Firefox)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Callable
from pathlib import Path

from hardzilla.presentation.view_models import ApplyViewModel


class ApplyView(ctk.CTkScrollableFrame):
    """
    Apply to Firefox View.

    Final screen where user applies settings to Firefox profile.
    SCROLLABLE to accommodate all content including apply button.
    """

    def __init__(
        self,
        parent,
        view_model: ApplyViewModel,
        on_apply: Callable,
        on_back: Callable,
        on_install_extensions: Callable = None
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
        self.on_install_extensions = on_install_extensions

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Build UI
        self._build_header()
        self._build_summary()
        self._build_apply_options()
        self._build_extensions_section()
        self._build_navigation()

        # Subscribe to view model changes
        self.view_model.subscribe('apply_success', self._on_apply_complete)
        self.view_model.subscribe('error_message', self._on_error)
        # Subscribe to count changes for reactive summary updates
        self.view_model.subscribe('base_count', self._on_counts_updated)
        self.view_model.subscribe('advanced_count', self._on_counts_updated)
        # Subscribe to extension-related changes
        self.view_model.subscribe('extension_install_success', self._on_extension_install_complete)
        self.view_model.subscribe('is_installing_extensions', self._on_extension_installing_changed)

    def _build_header(self):
        """Build screen header"""
        header = ctk.CTkLabel(
            self,
            text="Apply to Firefox",
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

        # Profile name editor
        name_frame = ctk.CTkFrame(section, fg_color="transparent")
        name_frame.pack(padx=20, pady=(10, 5), fill="x")

        name_label = ctk.CTkLabel(
            name_frame,
            text="Profile Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.pack(side="left", padx=(0, 10))

        self.profile_name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter custom profile name...",
            font=ctk.CTkFont(size=13),
            height=32
        )
        self.profile_name_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Info label
        info_label = ctk.CTkLabel(
            section,
            text="💡 Tip: Rename to save a customized version without overwriting the original",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        info_label.pack(padx=20, pady=(0, 10))

        self.summary_label = ctk.CTkLabel(
            section,
            text="BASE: 0 settings | ADVANCED: 0 settings"
        )
        self.summary_label.pack(padx=20, pady=(5, 10))

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

    def _build_extensions_section(self):
        """Build extensions installation section"""
        from hardzilla.metadata.extensions_metadata import EXTENSIONS_METADATA
        from hardzilla.domain.entities.extension import Extension
        from hardzilla.presentation.widgets.extension_row import ExtensionRow

        section = ctk.CTkFrame(self)
        section.grid(row=3, column=0, pady=10, sticky="ew", padx=10)

        # Header
        title = ctk.CTkLabel(
            section,
            text="Install Privacy Extensions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=20, pady=(10, 5))

        # Description
        desc = ctk.CTkLabel(
            section,
            text="Recommended extensions to enhance Firefox privacy (auto-installed via Enterprise Policies)",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        desc.pack(padx=20, pady=(0, 10))

        # Extension list (scrollable)
        extensions_frame = ctk.CTkScrollableFrame(section, height=250)
        extensions_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Build extension rows
        for ext_id, ext_data in EXTENSIONS_METADATA.items():
            extension = Extension(
                extension_id=ext_id,
                name=ext_data['name'],
                description=ext_data['description'],
                install_url=ext_data['install_url'],
                breakage_risk=ext_data['breakage_risk'],
                size_mb=ext_data['size_mb'],
                icon=ext_data['icon']
            )
            row = ExtensionRow(
                extensions_frame,
                extension=extension,
                on_toggle=self._on_extension_toggled,
                initial_checked=True
            )
            row.pack(fill="x", pady=2)

        # Install button
        self.install_extensions_btn = ctk.CTkButton(
            section,
            text="Install Extensions",
            command=self._on_install_extensions_clicked,
            fg_color="#9B59B6",
            hover_color="#7D3C98",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.install_extensions_btn.pack(padx=20, pady=(10, 20))

        # Status label (hidden initially)
        self.extension_status_label = ctk.CTkLabel(
            section,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.extension_status_label.pack(padx=20, pady=(0, 10))

    def _build_navigation(self):
        """Build navigation buttons"""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=4, column=0, pady=20, sticky="ew")
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

            # Update profile name entry
            self.profile_name_entry.delete(0, 'end')
            self.profile_name_entry.insert(0, profile.name)

            # Update summary label
            text = f"BASE: {self.view_model.base_count} settings | "
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
        # Update profile name from entry field
        new_name = self.profile_name_entry.get().strip()
        if new_name and self.view_model.profile:
            # Update the profile name
            self.view_model.profile.name = new_name

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

    def _on_extension_toggled(self, extension_id: str, checked: bool):
        """Handle extension checkbox toggle"""
        # Create new list to trigger ViewModel reactivity
        current = list(self.view_model.selected_extensions)
        if checked:
            if extension_id not in current:
                current.append(extension_id)
        else:
            if extension_id in current:
                current.remove(extension_id)
        # Assign through property setter to notify subscribers
        self.view_model.selected_extensions = current

    def _on_install_extensions_clicked(self):
        """Handle install extensions button click"""
        if not self.on_install_extensions:
            messagebox.showerror("Error", "Extension installation not configured")
            return

        # Validate Firefox path is set
        if not self.view_model.firefox_path:
            messagebox.showerror(
                "Error",
                "Please select a Firefox profile first (in Step 1)"
            )
            return

        # Validate extensions selected
        if not self.view_model.selected_extensions:
            messagebox.showerror(
                "Error",
                "Please select at least one extension to install"
            )
            return

        # Confirm action
        if not messagebox.askyesno(
            "Confirm Installation",
            f"This will install {len(self.view_model.selected_extensions)} extension(s) "
            f"to your Firefox installation.\n\n"
            f"Extensions will be auto-installed on next Firefox start.\n\n"
            f"Continue?",
            icon='question'
        ):
            return

        # Call controller
        self.on_install_extensions()

    def _on_extension_installing_changed(self, is_installing: bool):
        """Handle extension installation state change"""
        if is_installing:
            self.install_extensions_btn.configure(state="disabled", text="Installing...")
            self.extension_status_label.configure(text="Installing extensions...", text_color="#3B8ED0")
        else:
            self.install_extensions_btn.configure(state="normal", text="Install Extensions")

    def _on_extension_install_complete(self, success: bool):
        """Handle extension installation completion"""
        if not success:
            # Show error feedback
            self.extension_status_label.configure(
                text="✗ Extension installation failed",
                text_color="#E74C3C"
            )
            error_msg = self.view_model.error_message or "Unknown error occurred"
            messagebox.showerror("Extension Installation Failed", error_msg)
            return

        results = self.view_model.extension_install_results
        installed = results.get('installed', [])
        failed = results.get('failed', {})
        total = results.get('total', 0)

        # Build message
        message = f"✓ Installed {len(installed)} of {total} extension(s)\n\n"

        if failed:
            message += "Failed:\n"
            for name, err in failed.items():
                message += f"  • {name}: {err}\n"
            message += "\n"

        message += "⚠ Restart Firefox to activate extensions."

        # Update status label
        self.extension_status_label.configure(
            text=f"✓ Installed {len(installed)}/{total} extensions",
            text_color="#2FA572"
        )

        # Show success dialog
        messagebox.showinfo("Extensions Installed", message)
