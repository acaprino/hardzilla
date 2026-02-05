#!/usr/bin/env python3
"""
Enhanced UI Widgets with Professional Styling
"""

import customtkinter as ctk
from typing import Optional, Callable
from hardzilla.presentation.theme import Theme


class StyledButton(ctk.CTkButton):
    """Enhanced button with better styling"""

    def __init__(
        self,
        master,
        text: str = "",
        command: Optional[Callable] = None,
        variant: str = "primary",  # primary, secondary, success, warning, danger
        size: str = "md",  # sm, md, lg
        **kwargs
    ):
        # Get theme colors
        color_map = {
            'primary': (Theme.get_color('primary'), Theme.get_color('primary_hover')),
            'secondary': (Theme.get_color('secondary'), Theme.get_color('secondary_hover')),
            'success': (Theme.get_color('success'), '#0A5D0A'),
            'warning': (Theme.get_color('warning'), '#E5A700'),
            'danger': (Theme.get_color('error'), '#CC3333'),
            'ghost': ('transparent', Theme.get_color('bg_tertiary'))
        }

        fg_color, hover_color = color_map.get(variant, color_map['primary'])

        # Get size
        size_config = {
            'sm': Theme.SIZES['button_sm'],
            'md': Theme.SIZES['button_md'],
            'lg': Theme.SIZES['button_lg']
        }
        btn_size = size_config.get(size, size_config['md'])

        # Font
        font_config = Theme.get_font('button')
        font = ctk.CTkFont(
            family=font_config['family'],
            size=font_config['size'],
            weight=font_config['weight']
        )

        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=Theme.get_radius('md'),
            width=btn_size['width'],
            height=btn_size['height'],
            border_width=0,
            **kwargs
        )


class Card(ctk.CTkFrame):
    """Card container with shadow effect"""

    def __init__(
        self,
        master,
        title: Optional[str] = None,
        padding: int = Theme.SPACING['md'],
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.get_color('card_bg'),
            corner_radius=Theme.get_radius('lg'),
            border_width=1,
            border_color=Theme.get_color('border_light'),
            **kwargs
        )

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Title if provided
        if title:
            title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(
                    family='Segoe UI',
                    size=16,
                    weight='bold'
                ),
                text_color=Theme.get_color('text_primary')
            )
            title_label.grid(
                row=0,
                column=0,
                sticky="w",
                padx=padding,
                pady=(padding, padding // 2)
            )


class Badge(ctk.CTkLabel):
    """Badge/tag component"""

    def __init__(
        self,
        master,
        text: str = "",
        variant: str = "default",  # default, success, warning, error, info
        **kwargs
    ):
        color_map = {
            'default': (Theme.get_color('bg_tertiary'), Theme.get_color('text_secondary')),
            'success': (Theme.get_color('bg_tertiary'), Theme.get_color('success')),
            'warning': (Theme.get_color('bg_tertiary'), Theme.get_color('warning')),
            'error': (Theme.get_color('bg_tertiary'), Theme.get_color('error')),
            'info': (Theme.get_color('bg_tertiary'), Theme.get_color('primary')),
            'base': (Theme.get_color('badge_base'), '#FFFFFF'),
            'advanced': (Theme.get_color('badge_advanced'), '#FFFFFF')
        }

        bg_color, text_color = color_map.get(variant, color_map['default'])

        super().__init__(
            master,
            text=text,
            font=ctk.CTkFont(
                family='Segoe UI',
                size=10,
                weight='bold'
            ),
            fg_color=bg_color,
            text_color=text_color,
            corner_radius=Theme.get_radius('sm'),
            padx=8,
            pady=4,
            **kwargs
        )


class SectionHeader(ctk.CTkFrame):
    """Section header with optional subtitle"""

    def __init__(
        self,
        master,
        title: str,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color='transparent',
            **kwargs
        )

        self.grid_columnconfigure(1, weight=1)

        # Icon (if provided)
        col = 0
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.grid(row=0, column=col, rowspan=2 if subtitle else 1, padx=(0, 12))
            col += 1

        # Title
        font_config = Theme.get_font('heading_2')
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(
                family=font_config['family'],
                size=font_config['size'],
                weight=font_config['weight']
            ),
            text_color=Theme.get_color('text_primary'),
            anchor="w"
        )
        title_label.grid(row=0, column=col, sticky="w")

        # Subtitle (if provided)
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(
                    family='Segoe UI',
                    size=12
                ),
                text_color=Theme.get_color('text_secondary'),
                anchor="w"
            )
            subtitle_label.grid(row=1, column=col, sticky="w", pady=(2, 0))


class SearchBox(ctk.CTkEntry):
    """Enhanced search input with icon"""

    def __init__(
        self,
        master,
        placeholder: str = "Search...",
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            placeholder_text=f"🔍 {placeholder}",
            font=ctk.CTkFont(
                family='Segoe UI',
                size=13
            ),
            height=40,
            corner_radius=Theme.get_radius('md'),
            border_width=1,
            border_color=Theme.get_color('border_medium'),
            **kwargs
        )

        if on_change:
            self.bind('<KeyRelease>', lambda e: on_change(self.get()))


class StatsCard(ctk.CTkFrame):
    """Statistics display card"""

    def __init__(
        self,
        master,
        label: str,
        value: str,
        subtitle: Optional[str] = None,
        color: str = "primary",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.get_color('card_bg'),
            corner_radius=Theme.get_radius('lg'),
            border_width=1,
            border_color=Theme.get_color('border_light'),
            **kwargs
        )

        # Value (large)
        value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(
                family='Segoe UI',
                size=32,
                weight='bold'
            ),
            text_color=Theme.get_color(color)
        )
        value_label.pack(padx=20, pady=(20, 5))

        # Label
        label_label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(
                family='Segoe UI',
                size=12,
                weight='bold'
            ),
            text_color=Theme.get_color('text_secondary')
        )
        label_label.pack(padx=20, pady=(0, 5))

        # Subtitle (if provided)
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(
                    family='Segoe UI',
                    size=10
                ),
                text_color=Theme.get_color('text_tertiary')
            )
            subtitle_label.pack(padx=20, pady=(0, 20))


class ProgressBar(ctk.CTkProgressBar):
    """Enhanced progress bar"""

    def __init__(
        self,
        master,
        height: int = 8,
        **kwargs
    ):
        super().__init__(
            master,
            height=height,
            corner_radius=Theme.get_radius('full'),
            progress_color=Theme.get_color('primary'),
            fg_color=Theme.get_color('bg_tertiary'),
            **kwargs
        )


class Divider(ctk.CTkFrame):
    """Horizontal divider line"""

    def __init__(
        self,
        master,
        **kwargs
    ):
        super().__init__(
            master,
            height=1,
            fg_color=Theme.get_color('border_light'),
            **kwargs
        )
