#!/usr/bin/env python3
"""
Setting Row Widget with Visual Polish
Displays settings with badges, color coding, and tooltips
"""

import customtkinter as ctk
from typing import Callable, Optional
from hardfox.domain.entities import Setting
from hardfox.domain.enums import SettingLevel, SettingType


class SettingRow(ctk.CTkFrame):
    """
    Setting row with Windows 11 neutral styling.

    Features:
    - BASE/ADV text label indicating setting level
    - Neutral card surface with subtle border
    - Hover tooltips with full descriptions
    - Interactive controls based on setting type
    """

    # Color scheme - Windows 11 neutral style
    COLORS = {
        'BASE': {
            'badge_bg': 'transparent',
            'badge_fg': '#9E9E9E',
            'row_bg': '#2D2D2D',
            'hover_bg': '#383838',
            'border': '#3D3D3D',
            'text_primary': '#FFFFFF',
            'text_secondary': '#9E9E9E',
            'text_description': '#E0E0E0'
        },
        'ADVANCED': {
            'badge_bg': 'transparent',
            'badge_fg': '#9E9E9E',
            'row_bg': '#2D2D2D',
            'hover_bg': '#383838',
            'border': '#3D3D3D',
            'text_primary': '#FFFFFF',
            'text_secondary': '#9E9E9E',
            'text_description': '#E0E0E0'
        }
    }

    def __init__(
        self,
        parent,
        setting: Setting,
        on_change: Optional[Callable[[str, any], None]] = None,
        show_description: bool = True
    ):
        """
        Initialize setting row.

        Args:
            parent: Parent widget
            setting: Setting entity to display
            on_change: Callback when setting value changes (key, new_value)
            show_description: Whether to show full description below setting
        """
        super().__init__(parent)

        self.setting = setting
        self.on_change = on_change
        self.show_description = show_description

        # Configure colors with accent border
        self.colors = self.COLORS[setting.level.value]
        self.configure(
            fg_color=self.colors['row_bg'],
            border_color=self.colors['border'],
            border_width=1,
            corner_radius=4
        )

        # Build UI
        self._build_ui()

        # Bind hover events
        self.bind('<Enter>', self._on_hover_enter)
        self.bind('<Leave>', self._on_hover_leave)

    def _build_ui(self):
        """Build row UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Badge - small text label (Win11 style)
        badge_text = 'BASE' if self.setting.level == SettingLevel.BASE else 'ADV'
        badge = ctk.CTkLabel(
            self,
            text=badge_text,
            width=36,
            height=20,
            font=ctk.CTkFont(size=9),
            fg_color="transparent",
            text_color=self.colors['badge_fg'],
            corner_radius=0
        )
        badge.grid(row=0, column=0, padx=(8, 4), pady=(6, 4), sticky="nw")

        # Setting info frame
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=4, pady=(4, 4), sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)

        # Setting name
        name_label = ctk.CTkLabel(
            info_frame,
            text=self.setting.key,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")

        # Category and level info
        meta_text = f"[{self.setting.category}]" if self.setting.category else ""
        level_desc = "User-editable" if self.setting.level == SettingLevel.BASE else "Locked"
        meta_text += f"  {level_desc}"

        if self.setting.intent_tags:
            tags_display = ', '.join(self.setting.intent_tags[:3])
            if len(self.setting.intent_tags) > 3:
                tags_display += f" +{len(self.setting.intent_tags) - 3} more"
            meta_text += f"  |  Tags: {tags_display}"

        meta_label = ctk.CTkLabel(
            info_frame,
            text=meta_text,
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        meta_label.grid(row=1, column=0, sticky="w", pady=(1, 0))

        # Description (if enabled)
        if self.show_description and self.setting.description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=self.setting.description,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_description'],
                anchor="w",
                wraplength=600,
                justify="left"
            )
            desc_label.grid(row=2, column=0, sticky="w", pady=(2, 0))

        # Warning if high breakage
        if self.setting.breakage_score > 5:
            warning_label = ctk.CTkLabel(
                info_frame,
                text=f"⚠ Risk: {self.setting.breakage_score}/10 - may break sites",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#FFB900",
                anchor="w"
            )
            warning_label.grid(row=3, column=0, sticky="w", pady=(1, 0))

        # Additional warning text
        if self.setting.warning:
            extra_warning = ctk.CTkLabel(
                info_frame,
                text=f"Note: {self.setting.warning}",
                font=ctk.CTkFont(size=11),
                text_color="#FFB900",
                anchor="w",
                wraplength=600,
                justify="left"
            )
            extra_warning.grid(row=4, column=0, sticky="w", pady=(1, 0))

        # Control widget
        control = self._create_control()
        if control:
            control.grid(row=0, column=2, rowspan=5, padx=8, pady=6, sticky="ne")

        # Create tooltip
        self._create_tooltip()

    def _get_short_name(self) -> str:
        """Get shortened display name for setting"""
        key = self.setting.key

        # Remove common prefixes
        prefixes = ['browser.', 'network.', 'privacy.', 'dom.', 'media.']
        for prefix in prefixes:
            if key.startswith(prefix):
                key = key[len(prefix):]
                break

        # Truncate if too long
        if len(key) > 50:
            key = key[:47] + '...'

        return key

    def _create_control(self) -> Optional[ctk.CTkBaseClass]:
        """Create appropriate control widget based on setting type"""
        if self.setting.setting_type == SettingType.TOGGLE:
            return self._create_toggle()
        elif self.setting.setting_type == SettingType.DROPDOWN:
            return self._create_dropdown()
        elif self.setting.setting_type == SettingType.SLIDER:
            return self._create_slider()
        elif self.setting.setting_type == SettingType.INPUT:
            return self._create_input()
        return None

    def _create_toggle(self) -> ctk.CTkSwitch:
        """Create toggle switch"""
        switch = ctk.CTkSwitch(
            self,
            text="",
            width=50,
            command=self._on_toggle_changed
        )

        # Set initial value
        if isinstance(self.setting.value, bool):
            if self.setting.value:
                switch.select()
            else:
                switch.deselect()

        return switch

    def _create_dropdown(self) -> ctk.CTkComboBox:
        """Create dropdown menu"""
        if not self.setting.options:
            return None

        # Convert options to strings
        options = [str(opt) for opt in self.setting.options]

        dropdown = ctk.CTkComboBox(
            self,
            values=options,
            width=200,
            command=self._on_dropdown_changed
        )

        # Set current value
        current = str(self.setting.value)
        if current in options:
            dropdown.set(current)
        elif options:
            dropdown.set(options[0])

        return dropdown

    def _create_slider(self) -> ctk.CTkFrame:
        """Create slider with value label"""
        frame = ctk.CTkFrame(self, fg_color="transparent")

        # Value label
        value_label = ctk.CTkLabel(
            frame,
            text=str(self.setting.value),
            width=50
        )
        value_label.pack(side="right", padx=5)

        # Slider
        min_val = self.setting.min_value or 0
        max_val = self.setting.max_value or 100

        slider = ctk.CTkSlider(
            frame,
            from_=min_val,
            to=max_val,
            width=150,
            command=lambda val: self._on_slider_changed(val, value_label)
        )
        slider.pack(side="right", padx=5)

        # Set initial value
        if isinstance(self.setting.value, (int, float)):
            slider.set(self.setting.value)

        return frame

    def _create_input(self) -> ctk.CTkEntry:
        """Create text input"""
        entry = ctk.CTkEntry(
            self,
            width=200
        )
        entry.insert(0, str(self.setting.value))
        entry.bind('<FocusOut>', lambda e: self._on_input_changed(entry.get()))
        entry.bind('<Return>', lambda e: self._on_input_changed(entry.get()))

        return entry

    def _create_tooltip(self):
        """Create tooltip with full description"""
        # Store tooltip info for hover display
        self.tooltip_text = self._build_tooltip_text()

    def _build_tooltip_text(self) -> str:
        """Build comprehensive tooltip text"""
        lines = []

        # Full key
        lines.append(f"Preference: {self.setting.key}")
        lines.append("")

        # Description
        if self.setting.description:
            lines.append(self.setting.description)
            lines.append("")

        # Level info
        level_desc = "User-editable in Firefox" if self.setting.level == SettingLevel.BASE else "Locked preference"
        lines.append(f"Level: {self.setting.level.value} ({level_desc})")

        # Intent tags
        if self.setting.intent_tags:
            lines.append(f"Tags: {', '.join(self.setting.intent_tags)}")

        # Breakage warning
        if self.setting.breakage_score > 5:
            lines.append("")
            lines.append(f"Warning: May break some sites (score: {self.setting.breakage_score}/10)")

        # Setting-specific warning
        if self.setting.warning:
            lines.append("")
            lines.append(f"Note: {self.setting.warning}")

        return "\n".join(lines)

    def _on_toggle_changed(self):
        """Handle toggle change"""
        if self.on_change:
            # Get switch widget
            switch = [w for w in self.winfo_children() if isinstance(w, ctk.CTkSwitch)]
            if switch:
                new_value = switch[0].get() == 1
                self.on_change(self.setting.key, new_value)

    def _on_dropdown_changed(self, value: str):
        """Handle dropdown change"""
        if self.on_change:
            self.on_change(self.setting.key, value)

    def _on_slider_changed(self, value: float, label: ctk.CTkLabel):
        """Handle slider change"""
        int_value = int(value)
        label.configure(text=str(int_value))

        if self.on_change:
            self.on_change(self.setting.key, int_value)

    def _on_input_changed(self, value: str):
        """Handle input change"""
        if self.on_change:
            self.on_change(self.setting.key, value)

    def _on_hover_enter(self, event):
        """Handle mouse hover enter - change background"""
        self.configure(fg_color=self.colors['hover_bg'])

    def _on_hover_leave(self, event):
        """Handle mouse hover leave - restore background"""
        self.configure(fg_color=self.colors['row_bg'])


class SettingTooltip(ctk.CTkToplevel):
    """
    Tooltip window for displaying setting information.

    Shows full description, tags, warnings on hover.
    """

    def __init__(self, parent, text: str, x: int, y: int):
        """
        Initialize tooltip.

        Args:
            parent: Parent widget
            text: Tooltip text to display
            x, y: Screen coordinates for tooltip
        """
        super().__init__(parent)

        # Make it a tooltip-style window
        self.withdraw()  # Hide initially
        self.overrideredirect(True)  # No window decorations
        self.attributes('-topmost', True)  # Always on top

        # Style
        self.configure(fg_color="#2D2D2D")

        # Content
        label = ctk.CTkLabel(
            self,
            text=text,
            justify="left",
            text_color="#FFFFFF",
            padx=10,
            pady=8,
            font=ctk.CTkFont(size=10)
        )
        label.pack()

        # Position
        self.geometry(f"+{x}+{y+20}")

        # Show after delay
        self.after(500, self.deiconify)

    def hide(self):
        """Hide and destroy tooltip"""
        self.withdraw()
        self.destroy()
