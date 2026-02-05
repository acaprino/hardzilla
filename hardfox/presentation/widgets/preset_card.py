#!/usr/bin/env python3
"""
Preset Card Widget
Visual card for displaying preset profile with highlights and stats
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional


class PresetCard(ctk.CTkFrame):
    """
    Visual card for preset profile with highlights and stats.

    Shows:
    - Preset name + icon emoji
    - Key highlights (checkmarks for benefits, X for limitations)
    - Stats (settings changed, privacy score, breakage risk)
    - "Select" button with thin border selection state
    """

    # Icon emojis for presets
    ICONS = {
        'code': '💻',
        'briefcase': '💼',
        'shield': '🛡️',
        'shield-check': '✅',
        'battery': '🔋',
        'gamepad': '🎮',
        'globe': '🌐',
        'incognito': '🕵️',
        'bank': '🏦'
    }

    def __init__(
        self,
        parent,
        preset_data: Dict[str, Any],
        on_select: Callable[[], None],
        selected: bool = False
    ):
        """
        Initialize preset card.

        Args:
            parent: Parent widget
            preset_data: Dictionary with preset metadata (name, description, highlights, stats)
            on_select: Callback when card is selected
            selected: Whether this card is currently selected
        """
        super().__init__(parent)

        self.preset_data = preset_data
        self.on_select = on_select
        self.selected = selected

        # Card dimensions
        self.card_width = 280
        self.card_height = 480

        # Extract color for border
        self.preset_color = preset_data.get('color', '#888888')

        # Store reference to select button for updates
        self.select_button = None

        # Configure card appearance
        self.configure(
            width=self.card_width,
            height=self.card_height,
            fg_color="#2D2D2D",
            corner_radius=8,
            border_width=1,
            border_color=self.preset_color if selected else "#3D3D3D"
        )

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build card UI components"""
        # Main content frame with padding
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)

        # Icon + Name header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        icon_emoji = self.ICONS.get(self.preset_data.get('icon', 'globe'), '🌐')
        name = self.preset_data.get('name', 'Unknown')

        header_label = ctk.CTkLabel(
            header,
            text=f"{icon_emoji}  {name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        header_label.pack(anchor="w")

        # Description (max 3 lines)
        description = self.preset_data.get('description', '')
        desc_label = ctk.CTkLabel(
            content,
            text=description,
            font=ctk.CTkFont(size=13),
            anchor="w",
            justify="left",
            wraplength=240,
            text_color="#9E9E9E"
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # Divider
        divider1 = ctk.CTkFrame(content, height=1, fg_color="#3D3D3D")
        divider1.pack(fill="x", pady=(5, 10))

        # Highlights section
        highlights = self.preset_data.get('highlights', [])
        if highlights:
            highlights_frame = ctk.CTkScrollableFrame(
                content,
                height=180,
                fg_color="transparent",
                scrollbar_button_color="#3D3D3D",
                scrollbar_button_hover_color="#454545"
            )
            highlights_frame.pack(fill="x", pady=(0, 10))

            for highlight in highlights:
                if highlight.startswith('✓'):
                    # Positive feature (green checkmark)
                    color = "#0F7B0F"
                    icon = "✓"
                    text = highlight[1:].strip()
                elif highlight.startswith('✗'):
                    # Limitation (orange X)
                    color = "#FFB900"
                    icon = "✗"
                    text = highlight[1:].strip()
                else:
                    # Neutral
                    color = "#9E9E9E"
                    icon = "•"
                    text = highlight

                highlight_label = ctk.CTkLabel(
                    highlights_frame,
                    text=f"{icon} {text}",
                    font=ctk.CTkFont(size=12),
                    anchor="w",
                    justify="left",
                    wraplength=220,
                    text_color=color
                )
                highlight_label.pack(anchor="w", pady=2)

        # Divider
        divider2 = ctk.CTkFrame(content, height=1, fg_color="#3D3D3D")
        divider2.pack(fill="x", pady=(10, 10))

        # Stats badges
        stats = self.preset_data.get('stats', {})
        if stats:
            stats_frame = ctk.CTkFrame(content, fg_color="transparent")
            stats_frame.pack(fill="x", pady=(0, 10))

            # Settings changed badge
            settings_changed = stats.get('settings_changed', 'N/A')
            settings_badge = ctk.CTkLabel(
                stats_frame,
                text=f"⚙️ {settings_changed}",
                font=ctk.CTkFont(size=11),
                fg_color="#383838",
                corner_radius=5,
                padx=8,
                pady=4
            )
            settings_badge.pack(side="left", padx=(0, 5))

            # Privacy score badge
            privacy_score = stats.get('privacy_score', 'N/A')
            privacy_badge = ctk.CTkLabel(
                stats_frame,
                text=f"🛡️ {privacy_score}",
                font=ctk.CTkFont(size=11),
                fg_color="#383838",
                corner_radius=5,
                padx=8,
                pady=4
            )
            privacy_badge.pack(side="left", padx=5)

            # Breakage risk badge (on new line if space limited)
            breakage_risk = stats.get('breakage_risk', 'N/A')
            # Extract numeric risk for color coding
            if 'Very High' in breakage_risk or '(9' in breakage_risk or '(10' in breakage_risk:
                risk_color = "#FF4343"
            elif 'High' in breakage_risk or '(7' in breakage_risk or '(8' in breakage_risk:
                risk_color = "#FFB900"
            elif 'Medium' in breakage_risk or '(4' in breakage_risk or '(5' in breakage_risk or '(6' in breakage_risk:
                risk_color = "#FFB900"
            else:
                risk_color = "#0F7B0F"

            stats_frame2 = ctk.CTkFrame(content, fg_color="transparent")
            stats_frame2.pack(fill="x", pady=(5, 0))

            risk_badge = ctk.CTkLabel(
                stats_frame2,
                text=f"⚠️ {breakage_risk}",
                font=ctk.CTkFont(size=11),
                fg_color=risk_color,
                text_color="#FFFFFF",
                corner_radius=5,
                padx=8,
                pady=4
            )
            risk_badge.pack(anchor="w")

        # Select button at bottom (always visible, not in scroll area)
        self.select_button = ctk.CTkButton(
            content,
            text="✨ Select This" if not self.selected else "✓ Selected",
            command=self.on_select,
            fg_color=self.preset_color if not self.selected else "#0F7B0F",
            hover_color=self._darken_color(self.preset_color) if not self.selected else "#0A5D0A",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.select_button.pack(side="bottom", fill="x", pady=(10, 0))

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20% for hover effect"""
        try:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')

            # Convert to RGB
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

            # Darken by 20%
            r = int(r * 0.8)
            g = int(g * 0.8)
            b = int(b * 0.8)

            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):  # FIX: Catch only expected exceptions
            return "#3D3D3D"  # Fallback

    def set_selected(self, selected: bool):
        """Update selected state - optimized to only update button"""
        self.selected = selected

        # Update border (visual feedback for selection)
        self.configure(
            border_width=2 if selected else 1,
            border_color=self.preset_color if selected else "#3D3D3D"
        )

        # Update button appearance only (no full rebuild needed)
        if self.select_button:
            self.select_button.configure(
                text="✓ Selected" if selected else "✨ Select This",
                fg_color="#0F7B0F" if selected else self.preset_color,
                hover_color="#0A5D0A" if selected else self._darken_color(self.preset_color)
            )
