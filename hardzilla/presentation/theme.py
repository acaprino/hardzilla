#!/usr/bin/env python3
"""
Visual Theme and Styling
Enhanced color schemes, typography, and visual constants
"""

from typing import Dict


class Theme:
    """Enhanced visual theme for Hardzilla GUI"""

    # Color Palette - Windows 11 Dark Theme
    COLORS = {
        # Primary Colors (Windows Blue)
        'primary': '#0078D4',
        'primary_hover': '#106EBE',
        'primary_light': '#0078D4',

        # Secondary Colors (Windows Green)
        'secondary': '#0F7B0F',
        'secondary_hover': '#0A5D0A',
        'secondary_light': '#0F7B0F',

        # Accent Colors
        'accent': '#0078D4',
        'accent_hover': '#106EBE',
        'accent_light': '#0078D4',

        # Status Colors
        'success': '#0F7B0F',        # Windows green
        'warning': '#FFB900',        # Windows yellow
        'error': '#FF4343',          # Windows red
        'info': '#0078D4',           # Windows blue

        # Badge Colors (neutral in Win11 style)
        'badge_base': '#0078D4',
        'badge_base_light': '#383838',
        'badge_base_hover': '#454545',

        'badge_advanced': '#0078D4',
        'badge_advanced_light': '#383838',
        'badge_advanced_hover': '#454545',

        # Background Colors
        'bg_primary': '#202020',
        'bg_secondary': '#2D2D2D',
        'bg_tertiary': '#383838',
        'bg_dark': '#202020',
        'bg_darker': '#1A1A1A',

        # Text Colors
        'text_primary': '#FFFFFF',
        'text_secondary': '#9E9E9E',
        'text_tertiary': '#717171',
        'text_light': '#FFFFFF',

        # Border Colors
        'border_light': '#3D3D3D',
        'border_medium': '#454545',
        'border_dark': '#555555',

        # Card/Panel Colors
        'card_bg': '#2D2D2D',
        'card_border': '#3D3D3D',
        'card_shadow': 'rgba(0, 0, 0, 0.1)',

        # Frame Colors
        'frame_bg': '#2D2D2D',
        'frame_bg_light': '#2D2D2D',
    }

    # Typography
    FONTS = {
        'display': {
            'family': 'Segoe UI',
            'size': 28,
            'weight': 'bold'
        },
        'heading_1': {
            'family': 'Segoe UI',
            'size': 24,
            'weight': 'bold'
        },
        'heading_2': {
            'family': 'Segoe UI',
            'size': 20,
            'weight': 'bold'
        },
        'heading_3': {
            'family': 'Segoe UI',
            'size': 16,
            'weight': 'bold'
        },
        'body': {
            'family': 'Segoe UI',
            'size': 13,
            'weight': 'normal'
        },
        'body_large': {
            'family': 'Segoe UI',
            'size': 14,
            'weight': 'normal'
        },
        'caption': {
            'family': 'Segoe UI',
            'size': 11,
            'weight': 'normal'
        },
        'button': {
            'family': 'Segoe UI',
            'size': 13,
            'weight': 'bold'
        },
        'mono': {
            'family': 'Consolas',
            'size': 12,
            'weight': 'normal'
        }
    }

    # Spacing Scale (8px base)
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
        'xxxl': 64
    }

    # Border Radius (Windows 11: 4-8px range)
    RADIUS = {
        'sm': 4,
        'md': 4,
        'lg': 8,
        'xl': 8,
        'full': 9999
    }

    # Shadows
    SHADOWS = {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
    }

    # Component Sizes
    SIZES = {
        'button_sm': {'width': 100, 'height': 32},
        'button_md': {'width': 120, 'height': 40},
        'button_lg': {'width': 150, 'height': 48},
        'input_sm': {'height': 32},
        'input_md': {'height': 40},
        'input_lg': {'height': 48},
    }

    @classmethod
    def get_color(cls, key: str) -> str:
        """Get color by key"""
        return cls.COLORS.get(key, '#000000')

    @classmethod
    def get_font(cls, key: str) -> Dict:
        """Get font configuration by key"""
        return cls.FONTS.get(key, cls.FONTS['body'])

    @classmethod
    def get_spacing(cls, key: str) -> int:
        """Get spacing value by key"""
        return cls.SPACING.get(key, 8)

    @classmethod
    def get_radius(cls, key: str) -> int:
        """Get border radius by key"""
        return cls.RADIUS.get(key, 8)


class DarkTheme(Theme):
    """Dark mode color overrides (minimal - base Theme is now Win11 dark-native)"""

    COLORS = {
        **Theme.COLORS,
    }
