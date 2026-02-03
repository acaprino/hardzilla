#!/usr/bin/env python3
"""
Setup View - Screen 1 (Intent & Setup)
First screen of the 3-screen wizard
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import Callable, Optional

from hardzilla.presentation.view_models import SetupViewModel
from hardzilla.presentation.widgets import PresetCard
from hardzilla.metadata.settings_metadata import PRESET_PROFILES


class SetupView(ctk.CTkScrollableFrame):
    """
    Screen 1: Intent & Setup View.

    SCROLLABLE frame to accommodate all content including:
    1A. Firefox profile selection
    1B. Quick preset cards (520px tall)
    1C. Intent questions (use cases, privacy level, breakage tolerance)
    1D. Smart recommendation display
    1E. Navigation buttons
    """

    USE_CASES = [
        ("Banking/Financial", "banking"),
        ("Shopping", "shopping"),
        ("Social Media", "social_media"),
        ("Work/Productivity", "work"),
        ("Streaming Media", "streaming"),
        ("Development/Testing", "development"),
        ("General Browsing", "general"),
        ("Anonymous Research", "anonymous")
    ]

    PRIVACY_LEVELS = [
        ("Just want better defaults", "basic"),
        ("Block ads and trackers", "moderate"),
        ("Strong privacy (some sites may break)", "strong"),
        ("Maximum privacy (will troubleshoot)", "maximum")
    ]

    def __init__(
        self,
        parent,
        view_model: SetupViewModel,
        on_generate_recommendation: Callable,
        on_next: Callable
    ):
        """
        Initialize Setup View.

        Args:
            parent: Parent widget
            view_model: SetupViewModel for state management
            on_generate_recommendation: Callback to generate recommendation
            on_next: Callback for Next button
        """
        super().__init__(parent)
        self.view_model = view_model
        self.on_generate_recommendation = on_generate_recommendation
        self.on_next = on_next

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Store selected preset card reference
        self.selected_card = None
        self.preset_cards = {}

        # Build UI
        self._build_header()
        self._build_firefox_selector()
        self._build_quick_presets()
        # Removed old manual customization (intent questions)
        self._build_recommendation_panel()
        self._build_navigation()

        # Subscribe to view model changes
        self.view_model.subscribe('can_proceed', self._on_can_proceed_changed)
        self.view_model.subscribe('generated_profile', self._on_profile_generated)

    def _build_header(self):
        """Build screen header"""
        header = ctk.CTkLabel(
            self,
            text="Setup & Presets",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, pady=(0, 20), sticky="w")

    def _build_firefox_selector(self):
        """Build Firefox profile path selector"""
        self.firefox_section = ctk.CTkFrame(self)
        self.firefox_section.grid(row=1, column=0, pady=10, sticky="ew")
        self.firefox_section.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(
            self.firefox_section,
            text="Firefox Profile:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.path_entry = ctk.CTkEntry(
            self.firefox_section,
            placeholder_text="Select Firefox profile directory...",
            font=ctk.CTkFont(size=13),
            height=36
        )
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        browse_btn = ctk.CTkButton(
            self.firefox_section,
            text="Browse",
            width=120,
            font=ctk.CTkFont(size=13),
            height=36,
            command=self._browse_firefox_path
        )
        browse_btn.grid(row=0, column=2, padx=10, pady=10)

    def _build_quick_presets(self):
        """Build quick preset selection cards"""
        section = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        section.grid(row=2, column=0, pady=10, sticky="ew", padx=10)

        # Header
        title = ctk.CTkLabel(
            section,
            text="Choose Your Privacy Profile",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(padx=20, pady=(15, 5))

        subtitle = ctk.CTkLabel(
            section,
            text="Select a preset that matches your needs - you can customize individual settings in the next step",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=800
        )
        subtitle.pack(padx=20, pady=(0, 10))

        # Scrollable frame for cards (horizontal)
        scrollable_frame = ctk.CTkScrollableFrame(
            section,
            orientation="horizontal",
            height=520,
            fg_color="transparent"
        )
        scrollable_frame.pack(padx=10, pady=(0, 15), fill="x")

        # Sort presets by privacy score (most aggressive first)
        presets_sorted = [
            ('anonymous', PRESET_PROFILES.get('anonymous')),
            ('privacy_enthusiast', PRESET_PROFILES.get('privacy_enthusiast')),
            ('privacy_pro', PRESET_PROFILES.get('privacy_pro')),
            ('banking', PRESET_PROFILES.get('banking')),
            ('office', PRESET_PROFILES.get('office')),
            ('developer', PRESET_PROFILES.get('developer')),
            ('laptop', PRESET_PROFILES.get('laptop')),
            ('gaming', PRESET_PROFILES.get('gaming')),
            ('casual', PRESET_PROFILES.get('casual'))
        ]

        # Create card for each preset
        for preset_key, preset_data in presets_sorted:
            if preset_data:  # Skip if None
                card = PresetCard(
                    scrollable_frame,
                    preset_data,
                    on_select=lambda key=preset_key: self._on_preset_selected(key)
                )
                card.pack(side="left", padx=10, pady=10)
                self.preset_cards[preset_key] = card

    def _build_divider(self):
        """Visual divider between quick presets and manual config"""
        divider_frame = ctk.CTkFrame(self, fg_color="transparent")
        divider_frame.grid(row=3, column=0, pady=15, sticky="ew", padx=10)
        divider_frame.grid_columnconfigure((0, 2), weight=1)

        # Left line
        left_line = ctk.CTkFrame(divider_frame, height=2, fg_color="gray")
        left_line.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # OR text
        or_label = ctk.CTkLabel(
            divider_frame,
            text="OR CUSTOMIZE MANUALLY",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        or_label.grid(row=0, column=1)

        # Right line
        right_line = ctk.CTkFrame(divider_frame, height=2, fg_color="gray")
        right_line.grid(row=0, column=2, sticky="ew", padx=(10, 0))

    def _build_intent_questions(self):
        """Build intent question cards"""
        section = ctk.CTkFrame(self)
        section.grid(row=4, column=0, pady=10, sticky="ew")
        section.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            section,
            text="Tell us how you use Firefox",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Use cases
        use_case_label = ctk.CTkLabel(
            section,
            text="What do you primarily use Firefox for? (Select all that apply)",
            font=ctk.CTkFont(size=13)
        )
        use_case_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        use_case_frame = ctk.CTkFrame(section)
        use_case_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.use_case_checkboxes = {}
        for idx, (label, value) in enumerate(self.USE_CASES):
            row = idx // 4
            col = idx % 4
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(
                use_case_frame,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=13),
                command=lambda v=value, var=var: self._on_use_case_toggle(v, var)
            )
            cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.use_case_checkboxes[value] = var

        # Privacy level
        privacy_label = ctk.CTkLabel(
            section,
            text="How important is privacy to you?",
            font=ctk.CTkFont(size=13)
        )
        privacy_label.grid(row=3, column=0, padx=10, pady=(15, 5), sticky="w")

        self.privacy_var = ctk.StringVar(value="moderate")
        for idx, (label, value) in enumerate(self.PRIVACY_LEVELS):
            rb = ctk.CTkRadioButton(
                section,
                text=label,
                variable=self.privacy_var,
                value=value,
                font=ctk.CTkFont(size=13),
                command=lambda: self._on_privacy_changed()
            )
            rb.grid(row=4+idx, column=0, padx=20, pady=2, sticky="w")

        # Breakage tolerance
        tolerance_label = ctk.CTkLabel(
            section,
            text="Are you comfortable troubleshooting issues?",
            font=ctk.CTkFont(size=13)
        )
        tolerance_label.grid(row=8, column=0, padx=10, pady=(15, 5), sticky="w")

        self.tolerance_slider = ctk.CTkSlider(
            section,
            from_=0,
            to=100,
            height=20,
            command=self._on_tolerance_changed
        )
        self.tolerance_slider.set(50)
        self.tolerance_slider.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        self.tolerance_value_label = ctk.CTkLabel(section, text="50%", font=ctk.CTkFont(size=13))
        self.tolerance_value_label.grid(row=10, column=0, padx=20, pady=2)

        # Generate button
        self.generate_btn = ctk.CTkButton(
            section,
            text="Generate Recommendation",
            command=self._on_generate_clicked,
            fg_color="#2FA572",
            hover_color="#238C5C",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.generate_btn.grid(row=11, column=0, padx=10, pady=15)

    def _build_recommendation_panel(self):
        """Build recommendation display panel"""
        self.recommendation_frame = ctk.CTkFrame(self)
        # Initially hidden
        # Will be shown after generation

    def _build_navigation(self):
        """Build navigation buttons"""
        nav_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        nav_frame.grid(row=4, column=0, pady=20, sticky="ew", padx=10)
        nav_frame.grid_columnconfigure(0, weight=1)

        # Status label (shows why Next is disabled)
        self.nav_status_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.nav_status_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        # Next button (prominent, centered)
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next: Customize Settings →",
            command=self.on_next,
            state="disabled",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#2FA572",
            hover_color="#238C5C"
        )
        self.next_btn.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")

    # Event handlers
    def _browse_firefox_path(self):
        """Open directory browser for Firefox profile"""
        path = filedialog.askdirectory(title="Select Firefox Profile Directory")
        if path:
            # Validate Firefox path
            is_valid, error_msg = self._validate_firefox_path(path)

            if is_valid:
                # Valid path - update and clear any errors
                self.path_entry.delete(0, "end")
                self.path_entry.insert(0, path)
                self.view_model.firefox_path = path
                self._clear_path_error()
            else:
                # Invalid path - show error
                self._show_path_error(error_msg)

    def _validate_firefox_path(self, path: str) -> tuple[bool, str]:
        """
        Validate Firefox profile path.

        Args:
            path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        firefox_path = Path(path)

        if not firefox_path.exists():
            return False, "Directory does not exist"

        if not firefox_path.is_dir():
            return False, "Path is not a directory"

        # Check for Firefox profile markers
        has_prefs = (firefox_path / "prefs.js").exists()
        has_times = (firefox_path / "times.json").exists()

        if not (has_prefs or has_times):
            return False, "Not a valid Firefox profile (missing prefs.js or times.json)"

        return True, ""

    def _show_path_error(self, message: str):
        """Show error message for invalid Firefox path"""
        if not hasattr(self, 'path_error_label'):
            self.path_error_label = ctk.CTkLabel(
                self.firefox_section,
                text="",
                font=ctk.CTkFont(size=11),
                text_color="#EF4444"  # Red
            )
            self.path_error_label.grid(row=2, column=0, columnspan=3,
                                      sticky="w", padx=10, pady=(5, 0))

        self.path_error_label.configure(text=f"⚠ {message}")

    def _clear_path_error(self):
        """Clear error message for Firefox path"""
        if hasattr(self, 'path_error_label'):
            self.path_error_label.configure(text="")

    def _on_use_case_toggle(self, value: str, var: ctk.BooleanVar):
        """Handle use case checkbox toggle"""
        self.view_model.toggle_use_case(value)

    def _on_privacy_changed(self):
        """Handle privacy level change"""
        self.view_model.privacy_level = self.privacy_var.get()

    def _on_tolerance_changed(self, value):
        """Handle tolerance slider change"""
        int_value = int(value)
        self.view_model.breakage_tolerance = int_value
        self.tolerance_value_label.configure(text=f"{int_value}%")

    def _on_generate_clicked(self):
        """Handle generate recommendation button click"""
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.view_model.is_loading = True
        self.on_generate_recommendation()

    def _on_profile_generated(self, profile):
        """Handle profile generation complete"""
        # Only update generate button if it exists (may not exist when loading presets)
        if hasattr(self, 'generate_btn'):
            self.generate_btn.configure(state="normal", text="Generate Recommendation")
        self.view_model.is_loading = False

        if profile:
            # Show recommendation
            self._show_recommendation(profile)

    def _show_recommendation(self, profile):
        """Display the generated recommendation"""
        self.recommendation_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Clear previous content
        for widget in self.recommendation_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.recommendation_frame,
            text="✨ Recommended Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=10, pady=10)

        profile_name = ctk.CTkLabel(
            self.recommendation_frame,
            text=f"Profile: {profile.name}",
            font=ctk.CTkFont(size=14)
        )
        profile_name.pack(padx=10, pady=5)

        stats = ctk.CTkLabel(
            self.recommendation_frame,
            text=f"BASE: {profile.get_base_settings_count()} settings | ADVANCED: {profile.get_advanced_settings_count()} settings"
        )
        stats.pack(padx=10, pady=5)

        use_btn = ctk.CTkButton(
            self.recommendation_frame,
            text="Use This Configuration",
            fg_color="#2FA572",
            command=lambda: self.view_model.set_property('selected_preset', profile.name)
        )
        use_btn.pack(padx=10, pady=10)

    def _on_can_proceed_changed(self, can_proceed: bool):
        """Update Next button state"""
        state = "normal" if can_proceed else "disabled"
        self.next_btn.configure(state=state)

        # Update status label
        if can_proceed:
            self.nav_status_label.configure(
                text="✓ Ready to proceed",
                text_color="#2FA572"
            )
        else:
            # Check what's missing
            has_firefox = bool(self.view_model.firefox_path)
            has_preset = self.view_model.selected_preset is not None

            if not has_firefox and not has_preset:
                self.nav_status_label.configure(
                    text="⚠ Please select Firefox profile and choose a preset above",
                    text_color="#FFA726"
                )
            elif not has_firefox:
                self.nav_status_label.configure(
                    text="⚠ Please select a Firefox profile above to continue",
                    text_color="#FFA726"
                )
            elif not has_preset:
                self.nav_status_label.configure(
                    text="⚠ Please choose a preset or generate a recommendation above",
                    text_color="#FFA726"
                )
            else:
                self.nav_status_label.configure(
                    text="",
                    text_color="#888888"
                )

    def _on_preset_selected(self, preset_key: str):
        """Handle preset card selection"""
        # Update card selection states
        for key, card in self.preset_cards.items():
            card.set_selected(key == preset_key)

        # Store selected preset
        self.selected_card = preset_key

        # Trigger generation immediately with preset
        self.view_model.selected_preset = preset_key

        # Show success message
        self._show_preset_selected_message(preset_key)

    def _show_preset_selected_message(self, preset_key: str):
        """Show confirmation message when preset is selected"""
        preset_data = PRESET_PROFILES.get(preset_key)
        if not preset_data:
            return

        # Show in recommendation panel
        self.recommendation_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Clear previous content
        for widget in self.recommendation_frame.winfo_children():
            widget.destroy()

        # Success icon and title
        title = ctk.CTkLabel(
            self.recommendation_frame,
            text=f"✓ Selected: {preset_data['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2FA572"
        )
        title.pack(padx=10, pady=(10, 5))

        # Description
        desc = ctk.CTkLabel(
            self.recommendation_frame,
            text=preset_data.get('description', ''),
            font=ctk.CTkFont(size=14),
            text_color="#B0B0B0",
            wraplength=600
        )
        desc.pack(padx=10, pady=5)

        # Stats summary
        stats = preset_data.get('stats', {})
        if stats:
            stats_text = f"Settings: {stats.get('settings_changed', 'N/A')} | Privacy: {stats.get('privacy_score', 'N/A')} | Risk: {stats.get('breakage_risk', 'N/A')}"
            stats_label = ctk.CTkLabel(
                self.recommendation_frame,
                text=stats_text,
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            )
            stats_label.pack(padx=10, pady=5)

        # Check if Firefox path is set
        if not self.view_model.firefox_path:
            # Firefox path not set - show warning
            firefox_warning = ctk.CTkLabel(
                self.recommendation_frame,
                text="⚠ Don't forget to select your Firefox profile above before clicking Next!",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FFA726"
            )
            firefox_warning.pack(padx=10, pady=(10, 15))
        else:
            # All set - show next instruction
            next_instruction = ctk.CTkLabel(
                self.recommendation_frame,
                text="✓ Click the big green 'Next' button below to customize settings →",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2FA572"
            )
            next_instruction.pack(padx=10, pady=(10, 15))
