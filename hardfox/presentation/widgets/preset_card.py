#!/usr/bin/env python3
"""
Preset Tile Widget
Compact clickable tile for displaying preset profile in a grid layout.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable


class PresetTile(ctk.CTkFrame):
    """
    Compact preset tile (~130px tall) for 3-column grid layout.

    Shows:
    - Color-coded left border (3px)
    - Row 1: Icon emoji + Name (bold)
    - Row 2: One-line description (gray, truncated)
    - Row 3: Privacy score + Breakage risk badges
    - Entire tile clickable with hover effect
    """

    ICONS = {
        'code': '\U0001f4bb',
        'briefcase': '\U0001f4bc',
        'shield': '\U0001f6e1\ufe0f',
        'shield-check': '\u2705',
        'battery': '\U0001f50b',
        'gamepad': '\U0001f3ae',
        'globe': '\U0001f310',
        'incognito': '\U0001f575\ufe0f',
        'bank': '\U0001f3e6'
    }

    # Colors
    _BG = "#2D2D2D"
    _BG_HOVER = "#353535"
    _BG_SELECTED = "#333340"
    _BORDER_DEFAULT = "#3D3D3D"
    _TEXT_SECONDARY = "#9E9E9E"
    _BADGE_BG = "#383838"

    def __init__(
        self,
        parent,
        preset_data: Dict[str, Any],
        on_select: Callable[[], None],
        selected: bool = False
    ):
        self.preset_data = preset_data
        self.on_select = on_select
        self.selected = selected
        self.preset_color = preset_data.get('color', '#888888')

        super().__init__(
            parent,
            fg_color=self._BG_SELECTED if selected else self._BG,
            corner_radius=8,
            border_width=2 if selected else 1,
            border_color=self.preset_color if selected else self._BORDER_DEFAULT
        )

        self._build_ui()
        self._bind_click(self)

    def _build_ui(self):
        """Build compact tile layout."""
        # Color accent bar on the left
        accent = ctk.CTkFrame(
            self,
            width=3,
            fg_color=self.preset_color,
            corner_radius=0
        )
        accent.pack(side="left", fill="y", padx=(0, 0))
        self._accent = accent

        # Content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=(8, 10), pady=10)
        self._bind_click(content)

        # Row 1: Icon + Name
        icon = self.ICONS.get(self.preset_data.get('icon', 'globe'), '\U0001f310')
        name = self.preset_data.get('name', 'Unknown')

        name_label = ctk.CTkLabel(
            content,
            text=f"{icon}  {name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        self._bind_click(name_label)

        # Row 2: One-line description
        description = self.preset_data.get('description', '')
        desc_label = ctk.CTkLabel(
            content,
            text=description,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=280,
            text_color=self._TEXT_SECONDARY
        )
        desc_label.pack(anchor="w", pady=(4, 6))
        self._bind_click(desc_label)

        # Row 3: Badges
        stats = self.preset_data.get('stats', {})
        if stats:
            badges_frame = ctk.CTkFrame(content, fg_color="transparent")
            badges_frame.pack(anchor="w")
            self._bind_click(badges_frame)

            # Privacy score badge
            privacy_score = stats.get('privacy_score', 'N/A')
            privacy_badge = ctk.CTkLabel(
                badges_frame,
                text=f"\U0001f6e1 {privacy_score}",
                font=ctk.CTkFont(size=11),
                fg_color=self._BADGE_BG,
                corner_radius=4,
                padx=6,
                pady=2
            )
            privacy_badge.pack(side="left", padx=(0, 5))
            self._bind_click(privacy_badge)

            # Breakage risk badge
            breakage_risk = stats.get('breakage_risk', 'N/A')
            risk_color = self._get_risk_color(breakage_risk)

            risk_badge = ctk.CTkLabel(
                badges_frame,
                text=f"\u26a0 {breakage_risk}",
                font=ctk.CTkFont(size=11),
                fg_color=risk_color,
                text_color="#FFFFFF",
                corner_radius=4,
                padx=6,
                pady=2
            )
            risk_badge.pack(side="left")
            self._bind_click(risk_badge)

    def _get_risk_color(self, breakage_risk: str) -> str:
        """Get color for breakage risk badge."""
        if 'Very High' in breakage_risk or '(9' in breakage_risk or '(10' in breakage_risk:
            return "#C0392B"
        if 'High' in breakage_risk or '(7' in breakage_risk or '(8' in breakage_risk:
            return "#D35400"
        if 'Medium' in breakage_risk or '(4' in breakage_risk or '(5' in breakage_risk or '(6' in breakage_risk:
            return "#7D6608"
        if 'Low' in breakage_risk and 'Very' not in breakage_risk:
            return "#1E6B30"
        return "#0F7B0F"

    def _bind_click(self, widget):
        """Bind click and hover events to a widget."""
        widget.bind("<Button-1>", lambda e: self.on_select())
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Hover enter."""
        if not self.selected:
            self.configure(fg_color=self._BG_HOVER)

    def _on_leave(self, event):
        """Hover leave."""
        if not self.selected:
            self.configure(fg_color=self._BG)

    def set_selected(self, selected: bool):
        """Update selected state."""
        self.selected = selected
        self.configure(
            border_width=2 if selected else 1,
            border_color=self.preset_color if selected else self._BORDER_DEFAULT,
            fg_color=self._BG_SELECTED if selected else self._BG
        )
