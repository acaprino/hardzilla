"""
Hardzilla Custom UI Widgets

Custom CustomTkinter widgets for the enhanced Hardzilla UI.
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Callable, Optional, Any

# Module exports
__all__ = [
    'CategorySlider',
    'SettingRow',
]


class CategorySlider(ctk.CTkFrame):
    """
    A 5-position horizontal slider for category presets.

    Displays a slider with 5 positions (0-4) with labels on left and right,
    clickable position buttons, and a description that updates based on selection.
    """

    # Styling constants
    BG_COLOR = "#2a2a4a"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    SELECTED_COLOR = "#3B8ED0"
    UNSELECTED_COLOR = "#606080"

    def __init__(
        self,
        parent,
        label_left: str,
        label_right: str,
        icon_left: str = "",
        icon_right: str = "",
        descriptions: Optional[List[str]] = None,
        on_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        """
        Initialize the CategorySlider.

        Args:
            parent: Parent widget
            label_left: Label for the left side (e.g., "Battery Saver")
            label_right: Label for the right side (e.g., "Max Power")
            icon_left: Icon for left side (e.g., "🔋")
            icon_right: Icon for right side (e.g., "🚀")
            descriptions: List of 5 descriptions for each position
            on_change: Callback function called when position changes
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Set default background color
        kwargs.setdefault("fg_color", self.BG_COLOR)
        kwargs.setdefault("corner_radius", 10)

        super().__init__(parent, **kwargs)

        self._label_left = label_left
        self._label_right = label_right
        self._icon_left = icon_left
        self._icon_right = icon_right
        self._descriptions = descriptions or [""] * 5
        self._on_change = on_change
        self._position = 2  # Default to center position
        self._position_buttons: List[ctk.CTkButton] = []

        # Ensure we have exactly 5 descriptions
        while len(self._descriptions) < 5:
            self._descriptions.append("")

        self._create_widgets()
        self._update_display()

    def _create_widgets(self):
        """Create and layout all widgets."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Main slider row
        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(15, 5))
        slider_frame.grid_columnconfigure(1, weight=1)

        # Left label with icon
        left_text = f"{self._icon_left} {self._label_left}" if self._icon_left else self._label_left
        self._left_label = ctk.CTkLabel(
            slider_frame,
            text=left_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.TEXT_PRIMARY,
            anchor="w"
        )
        self._left_label.grid(row=0, column=0, sticky="w", padx=(0, 15))

        # Position buttons frame (centered)
        buttons_frame = ctk.CTkFrame(slider_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="")

        # Create 5 position buttons
        for i in range(5):
            btn = ctk.CTkButton(
                buttons_frame,
                text="○",
                width=30,
                height=30,
                font=ctk.CTkFont(size=18),
                fg_color="transparent",
                hover_color="#404060",
                text_color=self.UNSELECTED_COLOR,
                command=lambda pos=i: self._on_position_click(pos)
            )
            btn.grid(row=0, column=i, padx=2)
            self._position_buttons.append(btn)

        # Right label with icon
        right_text = f"{self._label_right} {self._icon_right}" if self._icon_right else self._label_right
        self._right_label = ctk.CTkLabel(
            slider_frame,
            text=right_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.TEXT_PRIMARY,
            anchor="e"
        )
        self._right_label.grid(row=0, column=2, sticky="e", padx=(15, 0))

        # Description label
        self._description_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.TEXT_SECONDARY,
            wraplength=400,
            justify="center"
        )
        self._description_label.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=(5, 15))

    def _on_position_click(self, position: int):
        """Handle position button click."""
        if position != self._position:
            self._position = position
            self._update_display()
            if self._on_change:
                self._on_change(position)

    def _update_display(self):
        """Update the visual display based on current position."""
        # Update position buttons
        for i, btn in enumerate(self._position_buttons):
            if i == self._position:
                btn.configure(text="●", text_color=self.SELECTED_COLOR)
            else:
                btn.configure(text="○", text_color=self.UNSELECTED_COLOR)

        # Update description
        if 0 <= self._position < len(self._descriptions):
            self._description_label.configure(text=self._descriptions[self._position])

    def set_position(self, position: int):
        """
        Set the slider position.

        Args:
            position: Position value (0-4)
        """
        if 0 <= position <= 4:
            self._position = position
            self._update_display()

    def get_position(self) -> int:
        """
        Get the current slider position.

        Returns:
            Current position (0-4)
        """
        return self._position


class SettingRow(ctk.CTkFrame):
    """
    A single setting row with name, inline description, control, and expandable details.

    Displays a setting with its name, short description, and control (toggle or choice).
    Includes an info button that expands to show full details, impact, and recommendations.
    """

    # Styling constants
    BG_COLOR = "#2a2a4a"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    INFO_NORMAL = "#808080"
    INFO_EXPANDED = "#3B8ED0"

    # Impact colors
    IMPACT_COLORS = {
        "low": "#2FA572",
        "medium": "#FFA500",
        "high": "#E74C3C"
    }

    # Compatibility colors
    COMPATIBILITY_COLORS = {
        "none": "#2FA572",
        "minor": "#FFA500",
        "major": "#E74C3C"
    }

    def __init__(
        self,
        parent,
        name: str,
        short_desc: str,
        full_desc: str,
        setting_type: str,
        values: List[Any],
        labels: List[str],
        impact: str,
        compatibility: str,
        recommended: dict,
        variable: tk.Variable,
        **kwargs
    ):
        """
        Initialize the SettingRow.

        Args:
            parent: Parent widget
            name: Setting display name
            short_desc: Inline description (1-2 sentences)
            full_desc: Full description for details panel
            setting_type: 'toggle' or 'choice'
            values: Possible values for the setting
            labels: Display labels for the values
            impact: Impact level ('low', 'medium', 'high')
            compatibility: Compatibility impact ('none', 'minor', 'major')
            recommended: Dict mapping profile names to recommended values
            variable: Tkinter variable to bind to the control
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Set default background color
        kwargs.setdefault("fg_color", self.BG_COLOR)
        kwargs.setdefault("corner_radius", 8)

        super().__init__(parent, **kwargs)

        self._name = name
        self._short_desc = short_desc
        self._full_desc = full_desc
        self._setting_type = setting_type
        self._values = values
        self._labels = labels
        self._impact = impact.lower()
        self._compatibility = compatibility.lower()
        self._recommended = recommended
        self._variable = variable
        self._expanded = False
        self._details_frame: Optional[ctk.CTkFrame] = None

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout all widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Main row frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # Left side: name + info button + description
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")

        # Name row with info button
        name_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        name_frame.grid(row=0, column=0, sticky="w")

        # Setting name (bold)
        self._name_label = ctk.CTkLabel(
            name_frame,
            text=self._name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.TEXT_PRIMARY,
            anchor="w"
        )
        self._name_label.grid(row=0, column=0, sticky="w")

        # Info button
        self._info_button = ctk.CTkButton(
            name_frame,
            text="ⓘ",
            width=24,
            height=24,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#404060",
            text_color=self.INFO_NORMAL,
            command=self._toggle_details
        )
        self._info_button.grid(row=0, column=1, sticky="w", padx=(5, 0))

        # Short description
        self._short_desc_label = ctk.CTkLabel(
            left_frame,
            text=self._short_desc,
            font=ctk.CTkFont(size=12),
            text_color=self.TEXT_SECONDARY,
            anchor="w",
            wraplength=400,
            justify="left"
        )
        self._short_desc_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Right side: control
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=(20, 0))

        if self._setting_type == "toggle":
            self._control = ctk.CTkSwitch(
                control_frame,
                text="",
                variable=self._variable,
                onvalue=self._values[1] if len(self._values) > 1 else True,
                offvalue=self._values[0] if len(self._values) > 0 else False,
                width=50,
                height=24,
                progress_color="#3B8ED0",
                button_color="#ffffff",
                button_hover_color="#e0e0e0"
            )
            self._control.grid(row=0, column=0)
        else:  # choice
            self._control = ctk.CTkSegmentedButton(
                control_frame,
                values=self._labels,
                variable=self._variable,
                font=ctk.CTkFont(size=12),
                selected_color="#3B8ED0",
                selected_hover_color="#4A9FE0",
                unselected_color="#404060",
                unselected_hover_color="#505070"
            )
            self._control.grid(row=0, column=0)

            # Map variable to use labels for segmented button
            if self._variable.get() in self._values:
                idx = self._values.index(self._variable.get())
                if idx < len(self._labels):
                    self._variable.set(self._labels[idx])

    def _toggle_details(self):
        """Toggle the expanded details panel."""
        self._expanded = not self._expanded

        if self._expanded:
            self._show_details()
            self._info_button.configure(text_color=self.INFO_EXPANDED)
        else:
            self._hide_details()
            self._info_button.configure(text_color=self.INFO_NORMAL)

    def _show_details(self):
        """Show the expanded details panel."""
        if self._details_frame is not None:
            return

        self._details_frame = ctk.CTkFrame(self, fg_color="#1e1e3a", corner_radius=6)
        self._details_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._details_frame.grid_columnconfigure(0, weight=1)

        # Full description
        desc_label = ctk.CTkLabel(
            self._details_frame,
            text=self._full_desc,
            font=ctk.CTkFont(size=12),
            text_color=self.TEXT_PRIMARY,
            anchor="w",
            wraplength=500,
            justify="left"
        )
        desc_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        # Impact and compatibility row
        info_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="w", padx=15, pady=5)

        # Impact indicator
        impact_color = self.IMPACT_COLORS.get(self._impact, self.IMPACT_COLORS["low"])
        impact_label = ctk.CTkLabel(
            info_frame,
            text=f"Impact: {self._impact.capitalize()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=impact_color,
            anchor="w"
        )
        impact_label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Compatibility indicator
        compat_color = self.COMPATIBILITY_COLORS.get(self._compatibility, self.COMPATIBILITY_COLORS["none"])
        compat_text = {
            "none": "No Compatibility Issues",
            "minor": "Minor Compatibility Issues",
            "major": "Major Compatibility Issues"
        }.get(self._compatibility, "Unknown")

        compat_label = ctk.CTkLabel(
            info_frame,
            text=f"Compatibility: {compat_text}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=compat_color,
            anchor="w"
        )
        compat_label.grid(row=0, column=1, sticky="w")

        # Recommended values per profile
        if self._recommended:
            rec_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
            rec_frame.grid(row=2, column=0, sticky="w", padx=15, pady=(5, 10))

            rec_title = ctk.CTkLabel(
                rec_frame,
                text="Recommended:",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.TEXT_SECONDARY,
                anchor="w"
            )
            rec_title.grid(row=0, column=0, sticky="w")

            rec_text_parts = []
            for profile, value in self._recommended.items():
                # Format the value for display
                if isinstance(value, bool):
                    value_str = "On" if value else "Off"
                else:
                    value_str = str(value)
                rec_text_parts.append(f"{profile}: {value_str}")

            rec_values = ctk.CTkLabel(
                rec_frame,
                text="  |  ".join(rec_text_parts),
                font=ctk.CTkFont(size=11),
                text_color=self.TEXT_PRIMARY,
                anchor="w"
            )
            rec_values.grid(row=0, column=1, sticky="w", padx=(10, 0))

    def _hide_details(self):
        """Hide the expanded details panel."""
        if self._details_frame is not None:
            self._details_frame.destroy()
            self._details_frame = None

    def get_value(self) -> Any:
        """
        Get the current value of the setting.

        Returns:
            The current value from the bound variable
        """
        return self._variable.get()

    def set_value(self, value: Any):
        """
        Set the value of the setting.

        Args:
            value: The value to set
        """
        self._variable.set(value)

    def is_expanded(self) -> bool:
        """
        Check if the details panel is expanded.

        Returns:
            True if expanded, False otherwise
        """
        return self._expanded


# For testing purposes
if __name__ == "__main__":
    # Create a test window
    root = ctk.CTk()
    root.title("Hardzilla Widgets Test")
    root.geometry("700x500")
    root.configure(fg_color="#1a1a2e")

    # Test CategorySlider
    slider = CategorySlider(
        root,
        label_left="Battery Saver",
        label_right="Max Power",
        icon_left="🔋",
        icon_right="🚀",
        descriptions=[
            "Maximum battery savings - reduced performance",
            "Balanced toward battery life",
            "Balanced performance and battery",
            "Balanced toward performance",
            "Maximum performance - higher power usage"
        ],
        on_change=lambda pos: print(f"Position changed to: {pos}")
    )
    slider.pack(fill="x", padx=20, pady=20)

    # Test SettingRow
    test_var = tk.BooleanVar(value=True)
    setting = SettingRow(
        root,
        name="Hardware Acceleration",
        short_desc="Enable GPU acceleration for rendering",
        full_desc="Hardware acceleration uses your graphics card (GPU) to render web pages faster. This can significantly improve performance for video playback and animations, but may cause issues with some graphics drivers.",
        setting_type="toggle",
        values=[False, True],
        labels=["Off", "On"],
        impact="high",
        compatibility="minor",
        recommended={"Standard": True, "Privacy": True, "Compatibility": False},
        variable=test_var
    )
    setting.pack(fill="x", padx=20, pady=10)

    # Test SettingRow with choice
    choice_var = tk.StringVar(value="Balanced")
    choice_setting = SettingRow(
        root,
        name="Cookie Policy",
        short_desc="Control how cookies are handled",
        full_desc="Cookies are small files websites store on your computer. Strict blocks all third-party cookies, Balanced blocks tracking cookies, and Permissive allows all cookies.",
        setting_type="choice",
        values=["strict", "balanced", "permissive"],
        labels=["Strict", "Balanced", "Permissive"],
        impact="medium",
        compatibility="minor",
        recommended={"Standard": "balanced", "Privacy": "strict", "Compatibility": "permissive"},
        variable=choice_var
    )
    choice_setting.pack(fill="x", padx=20, pady=10)

    root.mainloop()
