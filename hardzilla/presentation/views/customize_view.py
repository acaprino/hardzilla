#!/usr/bin/env python3
"""
Customize View - Screen 2 (Review & Customize Settings)
Enhanced with visual polish and category organization
"""

import customtkinter as ctk
from typing import Callable, Dict, List

from hardzilla.presentation.view_models import CustomizeViewModel
from hardzilla.presentation.widgets.setting_row import SettingRow
from hardzilla.presentation.utils import bind_search_focus, bind_escape_clear
from hardzilla.domain.entities import Setting


class CustomizeView(ctk.CTkFrame):
    """
    Screen 2: Customize Settings View with Visual Polish.

    Features:
    - Color-coded setting badges ([B] green, [A] purple)
    - Category-organized collapsible sections
    - Search filter across all settings
    - Hover tooltips with descriptions
    - Progressive disclosure (show/hide advanced)
    """

    def __init__(
        self,
        parent,
        view_model: CustomizeViewModel,
        on_next: Callable,
        on_back: Callable
    ):
        """
        Initialize Customize View.

        Args:
            parent: Parent widget
            view_model: CustomizeViewModel for state management
            on_next: Callback for Next button
            on_back: Callback for Back button
        """
        super().__init__(parent)
        self.view_model = view_model
        self.on_next = on_next
        self.on_back = on_back

        # State
        self.setting_rows: List[SettingRow] = []
        # Expand core categories by default
        self.expanded_categories: set = {'privacy', 'security', 'tracking', 'cookies'}
        self.show_advanced = False
        self.show_descriptions = True  # Show full descriptions by default

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Build UI
        self._build_header()
        self._build_profile_summary()
        self._build_search_and_filters()
        self._build_settings_list()
        self._build_navigation()

        # Subscribe to view model changes
        self.view_model.subscribe('profile', self._on_profile_changed)

    def _build_header(self):
        """Build screen header with legend"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            header_frame,
            text="Review & Customize Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w")

        # Legend
        legend_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        legend_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            legend_frame,
            text="B",
            width=25,
            height=25,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#2FA572",
            text_color="#FFFFFF",
            corner_radius=5
        ).pack(side="left", padx=2)

        ctk.CTkLabel(
            legend_frame,
            text="BASE (editable)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="left", padx=(2, 10))

        ctk.CTkLabel(
            legend_frame,
            text="A",
            width=25,
            height=25,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#7B68EE",
            text_color="#FFFFFF",
            corner_radius=5
        ).pack(side="left", padx=2)

        ctk.CTkLabel(
            legend_frame,
            text="ADVANCED (locked)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="left", padx=2)

    def _build_profile_summary(self):
        """Build profile summary section"""
        section = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        section.grid(row=1, column=0, pady=5, sticky="ew", padx=10)

        self.profile_name_label = ctk.CTkLabel(
            section,
            text="Profile: None",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.profile_name_label.pack(padx=15, pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            section,
            text="0 BASE | 0 ADVANCED | 0 total settings",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.stats_label.pack(padx=15, pady=(0, 10))

    def _build_search_and_filters(self):
        """Build search bar and filter options"""
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=2, column=0, pady=5, sticky="ew", padx=10)
        filter_frame.grid_columnconfigure(0, weight=1)

        # Search entry
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search settings... (press / to focus)",
            height=32
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)

        # Bind keyboard shortcuts for search
        bind_search_focus(self.search_entry, self)
        bind_escape_clear(self.search_entry)

        # Show descriptions checkbox
        self.show_descriptions_var = ctk.BooleanVar(value=True)
        self.show_descriptions_check = ctk.CTkCheckBox(
            filter_frame,
            text="Show descriptions",
            variable=self.show_descriptions_var,
            command=self._on_show_descriptions_changed
        )
        self.show_descriptions_check.grid(row=0, column=1, padx=5)

        # Show advanced checkbox
        self.show_advanced_var = ctk.BooleanVar(value=False)
        self.show_advanced_check = ctk.CTkCheckBox(
            filter_frame,
            text="Show experimental",
            variable=self.show_advanced_var,
            command=self._on_show_advanced_changed
        )
        self.show_advanced_check.grid(row=0, column=2, padx=5)

        # Reset button
        reset_btn = ctk.CTkButton(
            filter_frame,
            text="Reset to Recommended",
            width=150,
            command=self._on_reset_clicked,
            fg_color="gray",
            hover_color="#555555"
        )
        reset_btn.grid(row=0, column=3, padx=5)

    def _build_settings_list(self):
        """Build scrollable settings list"""
        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=400
        )
        self.scrollable_frame.grid(row=3, column=0, pady=5, sticky="nsew", padx=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Placeholder message
        self.placeholder_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Generate a profile in Step 1 to see settings here",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.placeholder_label.grid(row=0, column=0, pady=50)

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

        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next: Apply Settings →",
            command=self.on_next,
            fg_color="#2FA572"
        )
        next_btn.grid(row=0, column=2, padx=10, pady=10)

    def _on_profile_changed(self, profile):
        """Update display when profile changes"""
        if profile:
            # Update summary
            self.profile_name_label.configure(text=f"{profile.name}")
            base_count = profile.get_base_settings_count()
            adv_count = profile.get_advanced_settings_count()
            total_count = len(profile.settings)
            self.stats_label.configure(
                text=f"{base_count} BASE | {adv_count} ADVANCED | {total_count} total settings"
            )

            # Render settings list
            self._render_settings()

    def _render_settings(self):
        """Render settings list organized by category"""
        profile = self.view_model.profile
        if not profile:
            return

        # Clear existing widgets
        self.placeholder_label.grid_forget()
        for row in self.setting_rows:
            row.destroy()
        self.setting_rows.clear()

        # Group settings by category
        categories = self._group_by_category(profile.settings)

        # Filter by search and visibility
        search_text = self.search_entry.get().lower()
        filtered_categories = self._filter_categories(categories, search_text)

        # Render each category
        row_index = 0
        for category, settings in filtered_categories.items():
            # Category header
            header = self._create_category_header(category, len(settings))
            header.grid(row=row_index, column=0, pady=(10, 5), sticky="ew")
            row_index += 1

            # Settings (collapsible)
            if category in self.expanded_categories:
                for setting in settings:
                    row = SettingRow(
                        self.scrollable_frame,
                        setting,
                        on_change=self._on_setting_changed,
                        show_description=self.show_descriptions
                    )
                    row.grid(row=row_index, column=0, pady=2, sticky="ew")
                    self.setting_rows.append(row)
                    row_index += 1

        # Show message if no results
        if row_index == 0:
            self.placeholder_label.configure(
                text="No settings match your search"
            )
            self.placeholder_label.grid(row=0, column=0, pady=50)

    def _group_by_category(self, settings: Dict[str, Setting]) -> Dict[str, List[Setting]]:
        """Group settings by category"""
        categories = {}

        for setting in settings.values():
            # Skip experimental unless enabled
            if setting.visibility == "advanced" and not self.show_advanced:
                continue

            category = setting.category or "other"

            if category not in categories:
                categories[category] = []

            categories[category].append(setting)

        # Sort settings within each category
        for category in categories:
            categories[category].sort(key=lambda s: s.key)

        # Sort categories alphabetically
        return dict(sorted(categories.items()))

    def _filter_categories(
        self,
        categories: Dict[str, List[Setting]],
        search_text: str
    ) -> Dict[str, List[Setting]]:
        """Filter categories and settings by search text"""
        if not search_text:
            return categories

        filtered = {}

        for category, settings in categories.items():
            matching_settings = [
                s for s in settings
                if search_text in s.key.lower() or
                   search_text in (s.description or "").lower() or
                   search_text in category.lower()
            ]

            if matching_settings:
                filtered[category] = matching_settings

        return filtered

    def _create_category_header(self, category: str, count: int) -> ctk.CTkFrame:
        """Create collapsible category header"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2B2B2B", corner_radius=5)
        frame.grid_columnconfigure(1, weight=1)

        # Expand/collapse button
        is_expanded = category in self.expanded_categories
        arrow = "▼" if is_expanded else "▶"

        btn = ctk.CTkButton(
            frame,
            text=f"{arrow}  {category.upper()}  ({count})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color="#3B3B3B",
            anchor="w",
            command=lambda: self._toggle_category(category)
        )
        btn.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        return frame

    def _toggle_category(self, category: str):
        """Toggle category expansion"""
        if category in self.expanded_categories:
            self.expanded_categories.remove(category)
        else:
            self.expanded_categories.add(category)

        self._render_settings()

    def _on_search_changed(self, event):
        """Handle search text change"""
        self._render_settings()

    def _on_show_descriptions_changed(self):
        """Handle show descriptions checkbox change"""
        self.show_descriptions = self.show_descriptions_var.get()
        self._render_settings()

    def _on_show_advanced_changed(self):
        """Handle show advanced checkbox change"""
        self.show_advanced = self.show_advanced_var.get()
        self._render_settings()

    def _on_reset_clicked(self):
        """Handle reset to recommended button"""
        # Reset all settings to original recommended values
        self.view_model.reset_all()
        # Re-render to show original values
        self._render_settings()

    def _on_setting_changed(self, key: str, new_value):
        """Handle setting value change"""
        # Update value via ViewModel (proper MVVM)
        self.view_model.update_setting_value(key, new_value)
