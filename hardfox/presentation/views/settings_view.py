#!/usr/bin/env python3
"""
Settings View - Unified tab combining Setup, Customize, and Apply.

Layout:
  Row 0: Collapsible Preset Selector
  Row 1: Search & Filters bar
  Row 2: Profile summary (compact)
  Row 3: Settings list (expandable, weight=1)
  Row 4: Apply bar (fixed bottom)
"""

import logging
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Dict, List, Optional

import customtkinter as ctk

from hardfox.domain.entities import Setting
from hardfox.metadata.settings_metadata import PRESET_PROFILES
from hardfox.presentation.reconciliation import VNode, Reconciler
from hardfox.presentation.theme import Theme
from hardfox.presentation.utils import bind_search_focus, bind_escape_clear
from hardfox.presentation.view_models.settings_view_model import SettingsViewModel
from hardfox.presentation.widgets import PresetTile

logger = logging.getLogger(__name__)


class SettingsView(ctk.CTkFrame):
    """
    Unified Settings tab combining preset selection, settings customization,
    and apply-to-Firefox functionality in a single view.
    """

    def __init__(
        self,
        parent,
        view_model: SettingsViewModel,
        on_preset_selected: Callable,
        on_json_imported: Callable,
        on_apply: Callable,
        profiles_dir: Optional[Path] = None,
        debug_reconciliation: bool = False
    ):
        super().__init__(parent)
        self.view_model = view_model
        self.on_preset_selected = on_preset_selected
        self.on_json_imported = on_json_imported
        self.on_apply = on_apply
        self.profiles_dir = profiles_dir or Path.cwd() / "profiles"
        self.debug_reconciliation = debug_reconciliation

        # State
        self._reconciler: Optional[Reconciler] = None
        self.expanded_categories: set = {'privacy', 'security', 'tracking', 'cookies'}
        self.show_advanced = False
        self.show_descriptions = False
        self.preset_cards: dict = {}
        self.selected_card = None
        self._preset_expanded = False
        self._restore_warning_id = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Settings list expands

        # Build UI sections
        self._build_preset_section()       # Row 0
        self._build_search_and_filters()   # Row 1
        self._build_profile_summary()      # Row 2
        self._build_settings_list()        # Row 3
        self._build_apply_bar()            # Row 4

        # Subscribe to ViewModel changes
        self.view_model.subscribe('profile', self._on_profile_changed)
        self.view_model.subscribe('apply_success', self._on_apply_complete)
        self.view_model.subscribe('apply_error_message', self._on_apply_error)
        self.view_model.subscribe('base_count', self._on_counts_updated)
        self.view_model.subscribe('advanced_count', self._on_counts_updated)

        # Initial render
        self._on_profile_changed(None)

    def destroy(self):
        """Clean up ViewModel subscriptions."""
        self.view_model.unsubscribe('profile', self._on_profile_changed)
        self.view_model.unsubscribe('apply_success', self._on_apply_complete)
        self.view_model.unsubscribe('apply_error_message', self._on_apply_error)
        self.view_model.unsubscribe('base_count', self._on_counts_updated)
        self.view_model.unsubscribe('advanced_count', self._on_counts_updated)
        super().destroy()

    # =================================================================
    # Row 0: Collapsible Preset Selector
    # =================================================================

    def _build_preset_section(self):
        """Build collapsible preset selector section."""
        self.preset_outer = ctk.CTkFrame(self, fg_color="transparent")
        self.preset_outer.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        self.preset_outer.grid_columnconfigure(0, weight=1)

        # Clickable header
        self.preset_header = ctk.CTkButton(
            self.preset_outer,
            text="  Choose Preset / Import JSON",
            anchor="w",
            fg_color="#2D2D2D",
            hover_color="#383838",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=36,
            command=self._toggle_preset_section
        )
        self.preset_header.grid(row=0, column=0, sticky="ew")

        # Collapsible content (hidden by default)
        self.preset_content = ctk.CTkFrame(
            self.preset_outer,
            fg_color=Theme.get_color('frame_bg'),
            corner_radius=8
        )
        # Don't grid yet - starts collapsed

        self._build_preset_content()

    def _build_preset_content(self):
        """Build the inner content of the preset section."""
        content = self.preset_content
        content.grid_columnconfigure(0, weight=1)

        # --- Preset tiles (3-column grid) ---
        grid_frame = ctk.CTkFrame(content, fg_color="transparent")
        grid_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

        # Ordered presets
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

        idx = 0
        for preset_key, preset_data in presets_sorted:
            if preset_data:
                tile = PresetTile(
                    grid_frame,
                    preset_data,
                    on_select=lambda key=preset_key: self._on_preset_card_selected(key)
                )
                tile.grid(row=idx // 3, column=idx % 3, padx=5, pady=5, sticky="ew")
                self.preset_cards[preset_key] = tile
                idx += 1

        # --- Import JSON row ---
        import_frame = ctk.CTkFrame(content, fg_color="transparent")
        import_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        import_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            import_frame,
            text="Or Import Saved Profile:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.json_entry = ctk.CTkEntry(
            import_frame,
            placeholder_text="No profile imported",
            font=ctk.CTkFont(size=13),
            height=32,
            state="disabled"
        )
        self.json_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            import_frame,
            text="Import JSON",
            width=110,
            height=32,
            command=self._import_json_profile
        ).grid(row=0, column=2, padx=(0, 10))

        self.json_status_label = ctk.CTkLabel(
            import_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('info')
        )
        self.json_status_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(2, 0), sticky="w")

    def _toggle_preset_section(self):
        """Toggle expand/collapse of preset section."""
        self._preset_expanded = not self._preset_expanded
        if self._preset_expanded:
            self.preset_header.configure(text="  Choose Preset / Import JSON")
            self.preset_content.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        else:
            self.preset_header.configure(text="  Choose Preset / Import JSON")
            self.preset_content.grid_forget()

    def _on_preset_card_selected(self, preset_key: str):
        """Handle preset card selection."""
        for key, card in self.preset_cards.items():
            card.set_selected(key == preset_key)

        self.selected_card = preset_key
        self.view_model.selected_preset = preset_key

        # Clear JSON import (mutually exclusive)
        self._clear_json_entry()
        self._clear_json_status()

        # Trigger preset loading callback
        if self.on_preset_selected:
            self.on_preset_selected(preset_key)

        # Auto-collapse preset section
        if self._preset_expanded:
            self._toggle_preset_section()

    def _import_json_profile(self):
        """Open file dialog and import JSON profile."""
        file_path = filedialog.askopenfilename(
            title="Select Profile JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=str(self.profiles_dir)
        )
        if file_path:
            self._show_json_status("Loading profile from JSON...", Theme.get_color('info'))

            self.json_entry.configure(state="normal")
            self.json_entry.delete(0, "end")
            self.json_entry.insert(0, Path(file_path).name)
            self.json_entry.configure(state="disabled")

            # Clear preset selection (mutually exclusive)
            self._clear_preset_selection()

            if self.on_json_imported:
                self.on_json_imported(file_path)

    def _clear_preset_selection(self):
        """Deselect all preset cards."""
        for card in self.preset_cards.values():
            card.set_selected(False)
        self.selected_card = None
        self.view_model.selected_preset = None

    def _clear_json_entry(self):
        """Clear JSON entry field."""
        self.json_entry.configure(state="normal")
        self.json_entry.delete(0, "end")
        self.json_entry.configure(placeholder_text="No profile imported")
        self.json_entry.configure(state="disabled")

    def _clear_json_status(self):
        self.json_status_label.configure(text="")

    def _show_json_status(self, text: str, color: str):
        self.json_status_label.configure(text=text, text_color=color)

    def show_json_import_success(self, profile_name: str, settings_count: int):
        """Show successful JSON import message."""
        self.json_status_label.configure(
            text=f"Loaded '{profile_name}' with {settings_count} settings",
            text_color=Theme.get_color('primary')
        )

    def show_json_import_error(self, error_msg: str):
        """Show JSON import error message."""
        self.json_status_label.configure(
            text=f"Import failed: {error_msg}",
            text_color=Theme.get_color('error')
        )
        self._clear_json_entry()

    # =================================================================
    # Row 1: Search & Filters
    # =================================================================

    def _build_search_and_filters(self):
        """Build search bar and filter options."""
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, pady=5, sticky="ew", padx=10)
        filter_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search settings... (press / to focus)",
            height=32
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)

        bind_search_focus(self.search_entry, self)
        bind_escape_clear(self.search_entry)

        self.show_descriptions_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filter_frame,
            text="Show descriptions",
            variable=self.show_descriptions_var,
            command=self._on_show_descriptions_changed
        ).grid(row=0, column=1, padx=5)

        self.show_advanced_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filter_frame,
            text="Show experimental",
            variable=self.show_advanced_var,
            command=self._on_show_advanced_changed
        ).grid(row=0, column=2, padx=5)

        ctk.CTkButton(
            filter_frame,
            text="Reset to Recommended",
            width=150,
            command=self._on_reset_clicked,
            fg_color="#2D2D2D",
            hover_color="#383838"
        ).grid(row=0, column=3, padx=5)

    # =================================================================
    # Row 2: Profile Summary (compact)
    # =================================================================

    def _build_profile_summary(self):
        """Build compact profile summary."""
        section = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=8)
        section.grid(row=2, column=0, pady=5, sticky="ew", padx=10)
        section.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=8)
        inner.grid_columnconfigure(1, weight=1)

        self.profile_name_label = ctk.CTkLabel(
            inner,
            text="All Settings (Default Values)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.profile_name_label.grid(row=0, column=0, sticky="w")

        self.stats_label = ctk.CTkLabel(
            inner,
            text="0 BASE | 0 ADVANCED | 0 total",
            font=ctk.CTkFont(size=11),
            text_color="#9E9E9E"
        )
        self.stats_label.grid(row=0, column=1, sticky="e")

        # Legend
        legend_label = ctk.CTkLabel(
            inner,
            text="BASE = editable  |  ADV = locked",
            font=ctk.CTkFont(size=10),
            text_color="#9E9E9E"
        )
        legend_label.grid(row=0, column=2, sticky="e", padx=(15, 0))

    # =================================================================
    # Row 3: Settings List (scrollable, with reconciliation)
    # =================================================================

    def _build_settings_list(self):
        """Build scrollable settings list."""
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=400
        )
        self.scrollable_frame.grid(row=3, column=0, pady=5, sticky="nsew", padx=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.placeholder_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Select a preset or import a profile to see settings here",
            font=ctk.CTkFont(size=12),
            text_color="#9E9E9E"
        )
        self.placeholder_label.grid(row=0, column=0, pady=50)

    # =================================================================
    # Row 4: Apply Bar (fixed bottom)
    # =================================================================

    def _build_apply_bar(self):
        """Build the fixed apply bar at the bottom."""
        # Separator line
        separator = ctk.CTkFrame(self, height=1, fg_color="#3D3D3D")
        separator.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 0))

        bar = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=8)
        bar.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 10))
        bar.grid_columnconfigure(2, weight=1)

        # Profile name entry
        ctk.CTkLabel(
            bar,
            text="Profile:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")

        self.profile_name_entry = ctk.CTkEntry(
            bar,
            placeholder_text="Profile name...",
            font=ctk.CTkFont(size=13),
            height=32,
            width=200
        )
        self.profile_name_entry.grid(row=0, column=1, padx=(0, 15), pady=10)

        # Apply mode radio buttons
        mode_frame = ctk.CTkFrame(bar, fg_color="transparent")
        mode_frame.grid(row=0, column=2, pady=10, sticky="w")

        self.mode_var = ctk.StringVar(value="BOTH")
        for label, value in [("Both", "BOTH"), ("BASE", "BASE"), ("ADV", "ADVANCED")]:
            ctk.CTkRadioButton(
                mode_frame,
                text=label,
                variable=self.mode_var,
                value=value,
                command=lambda v=value: self._on_mode_changed(v),
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=5)

        # Load JSON button
        ctk.CTkButton(
            bar,
            text="Load JSON",
            width=100,
            height=32,
            fg_color="#3D3D3D",
            hover_color="#4D4D4D",
            font=ctk.CTkFont(size=12),
            command=self._import_json_profile
        ).grid(row=0, column=3, padx=(10, 5), pady=10)

        # Save JSON checkbox
        self.save_json_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            bar,
            text="Save JSON",
            variable=self.save_json_var,
            command=self._on_save_json_toggled,
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=4, padx=10, pady=10)

        # Warning + Apply button
        right_frame = ctk.CTkFrame(bar, fg_color="transparent")
        right_frame.grid(row=0, column=5, padx=(10, 15), pady=10, sticky="e")

        self.firefox_warning_label = ctk.CTkLabel(
            right_frame,
            text="Close Firefox before applying!",
            font=ctk.CTkFont(size=11),
            text_color="#FFB900"
        )
        self.firefox_warning_label.pack(side="left", padx=(0, 10))

        self.apply_btn = ctk.CTkButton(
            right_frame,
            text="Apply Settings",
            command=self._on_apply_clicked,
            fg_color="#0078D4",
            hover_color="#106EBE",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=36,
            width=150
        )
        self.apply_btn.pack(side="left")

    # =================================================================
    # Settings rendering (from CustomizeView)
    # =================================================================

    def _render_settings(self):
        """Render settings list using virtual DOM reconciliation."""
        settings = self.view_model.settings
        if not settings:
            return

        virtual_tree = self._build_virtual_tree(settings)

        if not self._reconciler:
            self._reconciler = Reconciler(self.scrollable_frame, debug=self.debug_reconciliation)
            self._reconciler.set_category_toggle_callback(self._toggle_category)

        self._reconciler.reconcile(virtual_tree, self._on_setting_changed)

        if len(virtual_tree) == 0:
            self.placeholder_label.configure(text="No settings match your search")
            self.placeholder_label.grid(row=0, column=0, pady=50)
        else:
            self.placeholder_label.grid_forget()

    def _build_virtual_tree(self, settings: Dict[str, Setting]) -> List[VNode]:
        """Build virtual tree representing desired UI state."""
        virtual_tree = []

        categories = self._group_by_category(settings)
        search_text = self.search_entry.get().lower()
        filtered_categories = self._filter_categories(categories, search_text)

        for category, category_settings in filtered_categories.items():
            virtual_tree.append(VNode(
                node_type='category_header',
                key=f'header_{category}',
                props={
                    'category': category,
                    'count': len(category_settings),
                    'is_expanded': category in self.expanded_categories
                }
            ))

            if category in self.expanded_categories:
                for setting in category_settings:
                    virtual_tree.append(VNode(
                        node_type='setting_row',
                        key=setting.key,
                        props={
                            'setting': setting,
                            'show_description': self.show_descriptions
                        }
                    ))

        return virtual_tree

    def _group_by_category(self, settings: Dict[str, Setting]) -> Dict[str, List[Setting]]:
        """Group settings by category."""
        categories = {}

        for setting in settings.values():
            if setting.visibility == "advanced" and not self.show_advanced:
                continue

            category = setting.category or "other"
            if category not in categories:
                categories[category] = []
            categories[category].append(setting)

        for category in categories:
            categories[category].sort(key=lambda s: s.key)

        return dict(sorted(categories.items()))

    def _filter_categories(
        self,
        categories: Dict[str, List[Setting]],
        search_text: str
    ) -> Dict[str, List[Setting]]:
        """Filter categories and settings by search text."""
        if not search_text:
            return categories

        filtered = {}
        for category, settings in categories.items():
            matching = [
                s for s in settings
                if search_text in s.key.lower() or
                   search_text in (s.description or "").lower() or
                   search_text in category.lower()
            ]
            if matching:
                filtered[category] = matching
        return filtered

    def _toggle_category(self, category: str):
        """Toggle category expansion."""
        if category in self.expanded_categories:
            self.expanded_categories.remove(category)
        else:
            self.expanded_categories.add(category)
        self._render_settings()

    # =================================================================
    # Event handlers
    # =================================================================

    def _on_search_changed(self, event):
        self._render_settings()

    def _on_show_descriptions_changed(self):
        self.show_descriptions = self.show_descriptions_var.get()
        self._render_settings()

    def _on_show_advanced_changed(self):
        self.show_advanced = self.show_advanced_var.get()
        self._render_settings()

    def _on_reset_clicked(self):
        self.view_model.reset_all()
        self._render_settings()

    def _on_setting_changed(self, key: str, new_value):
        self.view_model.update_setting_value(key, new_value)

    def _on_mode_changed(self, mode: str):
        self.view_model.apply_mode = mode

    def _on_save_json_toggled(self):
        self.view_model.save_to_json = self.save_json_var.get()

    def _on_apply_clicked(self):
        """Handle apply button click."""
        logger.debug("_on_apply_clicked: button pressed")

        # Update profile name from entry field
        new_name = self.profile_name_entry.get().strip()
        if new_name and self.view_model.profile:
            self.view_model.profile.name = new_name

        self.apply_btn.configure(state="disabled", text="Applying...")

        try:
            self.on_apply()
        except Exception as e:
            logger.error("_on_apply_clicked: failed: %s", e)
            self.apply_btn.configure(state="normal", text="Apply Settings")

    # =================================================================
    # ViewModel subscription handlers
    # =================================================================

    def _on_profile_changed(self, profile):
        """Update display when profile changes."""
        settings = self.view_model.settings

        if profile:
            self.profile_name_label.configure(text=profile.name)
            self.profile_name_entry.delete(0, 'end')
            self.profile_name_entry.insert(0, profile.name)
            base_count = profile.get_base_settings_count()
            adv_count = profile.get_advanced_settings_count()
            total_count = len(profile.settings)
        else:
            self.profile_name_label.configure(text="All Settings (Default Values)")
            base_count = sum(1 for s in settings.values() if s.level.value == "BASE")
            adv_count = sum(1 for s in settings.values() if s.level.value == "ADVANCED")
            total_count = len(settings)

        self.stats_label.configure(
            text=f"{base_count} BASE | {adv_count} ADVANCED | {total_count} total"
        )

        self._render_settings()

    def _on_counts_updated(self, value):
        """Handle count updates."""
        self._update_apply_summary()

    def _update_apply_summary(self):
        """Update apply bar summary if needed."""
        pass  # Counts are shown in profile summary

    def _on_apply_complete(self, success: bool):
        """Handle apply completion."""
        logger.debug("_on_apply_complete: success=%s", success)
        self.apply_btn.configure(state="normal", text="Apply Settings")

        if success:
            base = self.view_model.applied_base_count
            adv = self.view_model.applied_advanced_count
            logger.info("_on_apply_complete: base=%s, advanced=%s", base, adv)
            self.firefox_warning_label.configure(
                text=f"Applied {base} BASE + {adv} ADVANCED settings",
                text_color="#4CAF50"
            )
            self._schedule_restore_warning()

    def _on_apply_error(self, error_msg: str):
        """Handle apply error."""
        self.apply_btn.configure(state="normal", text="Apply Settings")
        if error_msg:
            logger.error("_on_apply_error: %s", error_msg)
            short_msg = error_msg.split('\n')[0][:60]
            self.firefox_warning_label.configure(
                text=f"Error: {short_msg}",
                text_color="#F44336"
            )
            self._schedule_restore_warning()

    def _schedule_restore_warning(self):
        """Restore the default warning label after a delay."""
        if hasattr(self, '_restore_warning_id') and self._restore_warning_id:
            self.after_cancel(self._restore_warning_id)
        self._restore_warning_id = self.after(5000, self._restore_warning_label)

    def _restore_warning_label(self):
        """Reset warning label to default text."""
        self._restore_warning_id = None
        self.firefox_warning_label.configure(
            text="Close Firefox before applying!",
            text_color="#FFB900"
        )
