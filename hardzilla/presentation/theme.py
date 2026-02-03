#!/usr/bin/env python3
"""
Visual Theme and Styling
Enhanced color schemes, typography, and visual constants
"""

from typing import Dict


class Theme:
    """Enhanced visual theme for Hardzilla GUI"""

    # Color Palette - Modern, Professional
    COLORS = {
        # Primary Colors
        'primary': '#2563EB',        # Blue
        'primary_hover': '#1D4ED8',
        'primary_light': '#DBEAFE',

        # Secondary Colors
        'secondary': '#10B981',      # Green
        'secondary_hover': '#059669',
        'secondary_light': '#D1FAE5',

        # Accent Colors
        'accent': '#8B5CF6',         # Purple
        'accent_hover': '#7C3AED',
        'accent_light': '#EDE9FE',

        # Status Colors
        'success': '#10B981',        # Green
        'warning': '#F59E0B',        # Orange
        'error': '#EF4444',          # Red
        'info': '#3B82F6',           # Blue

        # Badge Colors
        'badge_base': '#2FA572',     # Green for BASE
        'badge_base_light': '#E8F5E9',
        'badge_base_hover': '#C8E6C9',

        'badge_advanced': '#8B5CF6', # Purple for ADVANCED
        'badge_advanced_light': '#F3E8FF',
        'badge_advanced_hover': '#E9D5FF',

        # Background Colors
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F9FAFB',
        'bg_tertiary': '#F3F4F6',
        'bg_dark': '#1F2937',
        'bg_darker': '#111827',

        # Text Colors
        'text_primary': '#111827',
        'text_secondary': '#6B7280',
        'text_tertiary': '#9CA3AF',
        'text_light': '#FFFFFF',

        # Border Colors
        'border_light': '#E5E7EB',
        'border_medium': '#D1D5DB',
        'border_dark': '#9CA3AF',

        # Card/Panel Colors
        'card_bg': '#FFFFFF',
        'card_border': '#E5E7EB',
        'card_shadow': 'rgba(0, 0, 0, 0.05)',
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

    # Border Radius
    RADIUS = {
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
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
    """Dark mode color overrides"""

    COLORS = {
        **Theme.COLORS,

        # Dark mode overrides
        'bg_primary': '#1F2937',
        'bg_secondary': '#111827',
        'bg_tertiary': '#0F172A',
        'bg_dark': '#0F172A',
        'bg_darker': '#020617',

        'text_primary': '#F9FAFB',
        'text_secondary': '#D1D5DB',
        'text_tertiary': '#9CA3AF',

        'card_bg': '#1F2937',
        'card_border': '#374151',

        'border_light': '#374151',
        'border_medium': '#4B5563',
        'border_dark': '#6B7280',
    }
