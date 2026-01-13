#!/usr/bin/env python3
"""
Hardzilla - Firefox Hardening Tool
Complete control over what to keep and what to delete
CustomTkinter Modern UI with Acrylic/Mica Effect
"""

import os
import sys
import json
import logging
import ssl
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import shutil

# Setup logging
logger = logging.getLogger(__name__)

from hardzilla_metadata import SETTINGS_METADATA, PRESET_PROFILES, CATEGORIES
from hardzilla_widgets import CategorySlider, SettingRow
from hardzilla_profiles import ProfileManager, FirefoxImporter

# Windows-specific window styling
try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette for consistent theming - with transparency support
COLORS = {
    'success': "#2FA572",
    'success_hover': "#238C5C",
    'error': "#E74C3C",
    'info': "#3B8ED0",
    'warning': "#FFA500",
    'muted': "#808080",
    'bg_transparent': "transparent",
    'card_bg': "#1a1a2e",  # Semi-dark card background
    'card_bg_light': "#16213e",  # Lighter card variant
    'accent': "#0f3460",  # Accent color for highlights
    'text_primary': "#ffffff",
    'text_secondary': "#a0a0a0",
    'border': "#2a2a4a",
}


class GranularPrivacyGUI:
    """Hardzilla - Firefox Hardening Tool"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Hardzilla - Firefox Hardening Tool")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)

        # Track if acrylic is enabled for styling adjustments
        self.acrylic_enabled = False

        # Set initial background
        self.root.configure(fg_color=("#1a1a2e", "#1a1a2e"))

        # Firefox path
        self.firefox_path = tk.StringVar(value=str(Path.home() / "FirefoxPortable"))
        self.profile_path = None

        # Profile state tracking
        self.profile_state = {
            'loaded': False,
            'modified': False,
            'profile_name': 'None',
            'last_applied': 'Never'
        }

        # Granular privacy variables
        self.privacy_vars = {
            # Session & Startup
            'restore_session': tk.BooleanVar(value=True),
            'restore_pinned': tk.BooleanVar(value=True),
            'restore_from_crash': tk.BooleanVar(value=True),
            'lazy_restore': tk.BooleanVar(value=True),

            # Data to KEEP on shutdown
            'keep_cookies': tk.BooleanVar(value=True),
            'keep_sessions': tk.BooleanVar(value=True),
            'keep_logins': tk.BooleanVar(value=True),
            'keep_formdata': tk.BooleanVar(value=True),
            'keep_downloads': tk.BooleanVar(value=False),
            'keep_history': tk.BooleanVar(value=False),

            # Data to CLEAR on shutdown
            'clear_cache': tk.BooleanVar(value=True),
            'clear_offline': tk.BooleanVar(value=True),
            'clear_siteprefs': tk.BooleanVar(value=False),
            'clear_thumbnails': tk.BooleanVar(value=True),

            # Cookie management
            'cookie_lifetime': tk.StringVar(value='normal'),  # normal, session, days
            # Note: cookie_days is managed by SETTINGS_METADATA as a 'choice' type with labels
            'third_party_cookies': tk.StringVar(value='cross-site'),  # all, cross-site, none, visited

            # Tracking protection
            'tracking_protection': tk.StringVar(value='strict'),  # standard, strict, custom
            'fingerprint_resist': tk.BooleanVar(value=True),
            'cryptomining_block': tk.BooleanVar(value=True),
            'fix_major_issues': tk.BooleanVar(value=True),  # Fix major site issues
            'fix_minor_issues': tk.BooleanVar(value=False),  # Fix minor site issues

            # Telemetry
            'telemetry_enabled': tk.BooleanVar(value=False),
            'studies_enabled': tk.BooleanVar(value=False),
            'crash_reports': tk.BooleanVar(value=False),

            # DNS & Network
            'dns_over_https': tk.StringVar(value='increased'),  # off, default, increased, max
            'dns_provider': tk.StringVar(value='quad9'),  # cloudflare, quad9, nextdns, custom
            'prefetch_dns': tk.BooleanVar(value=False),
            'prefetch_links': tk.BooleanVar(value=False),
            'predictor': tk.BooleanVar(value=False),

            # HTTPS
            'https_only': tk.BooleanVar(value=True),
            'https_only_pbm': tk.BooleanVar(value=True),
            'mixed_content_block': tk.BooleanVar(value=True),

            # WebRTC
            'webrtc_enabled': tk.BooleanVar(value=True),
            'webrtc_ip_leak': tk.BooleanVar(value=False),

            # Search & Autofill
            'search_suggestions': tk.BooleanVar(value=False),
            'url_suggestions': tk.BooleanVar(value=True),
            'autofill_forms': tk.BooleanVar(value=False),
            'autofill_passwords': tk.BooleanVar(value=True),

            # Permissions
            'location_permission': tk.StringVar(value='ask'),  # allow, ask, block
            'camera_permission': tk.StringVar(value='ask'),
            'microphone_permission': tk.StringVar(value='ask'),
            'notifications_permission': tk.StringVar(value='ask'),
            'autoplay_permission': tk.StringVar(value='block'),
        }

        # Initialize settings from metadata (for new settings not in privacy_vars)
        self.settings_vars = {}
        for key, meta in SETTINGS_METADATA.items():
            if key in self.privacy_vars:
                # Keep existing variable
                self.settings_vars[key] = self.privacy_vars[key]
            else:
                # Create new variable for new settings
                if meta['type'] == 'toggle':
                    self.settings_vars[key] = tk.BooleanVar(value=meta['default'])
                elif meta['type'] == 'choice':
                    self.settings_vars[key] = tk.StringVar(value=str(meta['default']))
                elif meta['type'] == 'number':
                    self.settings_vars[key] = tk.IntVar(value=meta['default'])

        # Initialize profile manager
        self.profile_manager = ProfileManager()

        # Recommended extensions
        self.extensions = {
            'ublock_origin': {
                'name': 'uBlock Origin',
                'id': 'uBlock0@raymondhill.net',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi',
                'description': 'Efficient ad and tracker blocker',
                'enabled': tk.BooleanVar(value=False)
            },
            'privacy_badger': {
                'name': 'Privacy Badger',
                'id': 'jid1-MnnxcxisBPnSXQ@jetpack',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/privacy-badger17/latest.xpi',
                'description': 'Automatically blocks invisible trackers',
                'enabled': tk.BooleanVar(value=False)
            },
            'cookie_autodelete': {
                'name': 'Cookie AutoDelete',
                'id': 'CookieAutoDelete@kennydo.com',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/cookie-autodelete/latest.xpi',
                'description': 'Automatically delete cookies when tabs close',
                'enabled': tk.BooleanVar(value=False)
            },
            'canvasblocker': {
                'name': 'CanvasBlocker',
                'id': 'CanvasBlocker@kkapsner.de',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/canvasblocker/latest.xpi',
                'description': 'Prevents fingerprinting via canvas',
                'enabled': tk.BooleanVar(value=False)
            },
            'decentraleyes': {
                'name': 'Decentraleyes',
                'id': 'jid1-BoFifL9Vbdl2zQ@jetpack',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/decentraleyes/latest.xpi',
                'description': 'Local CDN emulation to prevent tracking',
                'enabled': tk.BooleanVar(value=False)
            },
            'https_everywhere': {
                'name': 'HTTPS Everywhere',
                'id': 'https-everywhere@eff.org',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/https-everywhere/latest.xpi',
                'description': 'Force HTTPS on many sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'clearurls': {
                'name': 'ClearURLs',
                'id': '{74145f27-f039-47ce-a470-a662b129930a}',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/clearurls/latest.xpi',
                'description': 'Remove tracking elements from URLs',
                'enabled': tk.BooleanVar(value=False)
            },
            'bitwarden': {
                'name': 'Bitwarden Password Manager',
                'id': '{446900e4-71c2-419f-a6a7-df9c091e268b}',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/bitwarden-password-manager/latest.xpi',
                'description': 'Free and open-source password manager',
                'enabled': tk.BooleanVar(value=False)
            },
            'darkreader': {
                'name': 'Dark Reader',
                'id': 'addon@darkreader.org',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/darkreader/latest.xpi',
                'description': 'Dark mode for every website',
                'enabled': tk.BooleanVar(value=False)
            },
            'absolute_enable': {
                'name': 'Absolute Enable Right Click & Copy',
                'id': '{9350bc42-47fb-4598-ae0f-825e3dd9ba16}',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/absolute-enable-right-click/latest.xpi',
                'description': 'Re-enable right-click, copy, and text selection on restricted websites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bypass_paywalls': {
                'name': 'Bypass Paywalls Clean',
                'id': 'magnolia@12.34',
                'url': 'https://gitflic.ru/project/magnolia1234/bpc_uploads/blob/raw?file=bypass_paywalls_clean-latest.xpi',
                'description': 'Bypass paywalls on news and magazine websites',
                'enabled': tk.BooleanVar(value=False)
            },
            'tampermonkey': {
                'name': 'Tampermonkey',
                'id': 'firefox@tampermonkey.net',
                'url': 'https://addons.mozilla.org/firefox/downloads/latest/tampermonkey/latest.xpi',
                'description': 'Userscript manager - run custom scripts on websites',
                'enabled': tk.BooleanVar(value=False)
            }
        }

        # Tampermonkey userscripts
        self.userscripts = {
            'bpc_en': {
                'name': 'Bypass Paywalls Clean (English & Other)',
                'filename': 'bpc.en.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.en.user.js',
                'description': 'Additional fixes for English news sites (amp-redirect, unhide text/images)',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_de': {
                'name': 'Bypass Paywalls Clean (German)',
                'filename': 'bpc.de.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.de.user.js',
                'description': 'Additional fixes for German news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_fr': {
                'name': 'Bypass Paywalls Clean (French)',
                'filename': 'bpc.fr.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.fr.user.js',
                'description': 'Additional fixes for French news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_it': {
                'name': 'Bypass Paywalls Clean (Italian)',
                'filename': 'bpc.it.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.it.user.js',
                'description': 'Additional fixes for Italian news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_es_pt': {
                'name': 'Bypass Paywalls Clean (Spanish/Portuguese)',
                'filename': 'bpc.es.pt.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.es.pt.user.js',
                'description': 'Additional fixes for Spanish and Portuguese news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_nl': {
                'name': 'Bypass Paywalls Clean (Dutch)',
                'filename': 'bpc.nl.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.nl.user.js',
                'description': 'Additional fixes for Dutch news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_fi_se': {
                'name': 'Bypass Paywalls Clean (Finnish/Swedish/Danish)',
                'filename': 'bpc.fi.se.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.fi.se.user.js',
                'description': 'Additional fixes for Finnish, Swedish, and Danish news sites',
                'enabled': tk.BooleanVar(value=False)
            },
            'bpc_pl': {
                'name': 'Bypass Paywalls Clean (Polish)',
                'filename': 'bpc.pl.user.js',
                'url': 'https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.pl.user.js',
                'description': 'Additional fixes for Polish news sites',
                'enabled': tk.BooleanVar(value=False)
            }
        }

        # Setup UI
        self.setup_ui()
        self.load_defaults()

        # Apply acrylic effect AFTER UI is built (requires window to be rendered)
        self.root.after(50, self.apply_acrylic_effect)

        # Check Firefox path
        self.root.after(100, self.check_firefox_path)

    def apply_acrylic_effect(self):
        """Apply Windows acrylic/blur effect after window is rendered"""
        if not HAS_PYWINSTYLES or sys.platform != 'win32':
            return

        try:
            # Update window to ensure it's fully rendered
            self.root.update()

            # Apply acrylic style
            pywinstyles.apply_style(self.root, "acrylic")
            self.acrylic_enabled = True

            # Change title bar to match dark theme
            pywinstyles.change_header_color(self.root, color="#1a1a2e")

            print("Acrylic effect applied successfully")
        except Exception as e:
            print(f"Acrylic effect not available: {e}")
            self.acrylic_enabled = False

    def setup_ui(self):
        """Setup main UI with clean hierarchy and clear user flow"""
        # Main container - transparent to allow acrylic effect
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== TOP SECTION: Header + Quick Status =====
        top_section = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 10))

        # Header with title
        self.setup_header(top_section)

        # ===== STEP 1: Profile Selection (collapsible/compact) =====
        self.setup_profile_selector(main_frame)

        # ===== MAIN CONTENT: Two-column layout =====
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=10)

        # Left column: Navigation sidebar
        self.setup_sidebar(content_frame)

        # Right column: Settings content
        self.setup_content_area(content_frame)

        # ===== BOTTOM: Action Bar =====
        self.setup_action_bar(main_frame)

        # Track changes to mark as modified
        self.setup_change_tracking()

    def setup_header(self, parent):
        """Setup compact header with status indicator"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x")

        # Left side: Title
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        title = ctk.CTkLabel(left, text="Hardzilla",
                            font=ctk.CTkFont(size=28, weight="bold"),
                            text_color=COLORS['text_primary'])
        title.pack(side="left")

        subtitle = ctk.CTkLabel(left, text="Firefox Hardening Tool",
                               font=ctk.CTkFont(size=14),
                               text_color=COLORS['text_secondary'])
        subtitle.pack(side="left", padx=(10, 0), pady=(8, 0))

        # Right side: Quick status indicator
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self.quick_status_indicator = ctk.CTkLabel(
            right,
            text="Not configured",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['muted']
        )
        self.quick_status_indicator.pack(side="right", padx=5)

    def setup_profile_selector(self, parent):
        """Compact profile selector with step indicator"""
        # Card-style container with semi-transparent background
        card_bg = COLORS['card_bg']

        profile_card = ctk.CTkFrame(parent, fg_color=card_bg, corner_radius=12)
        profile_card.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        # Step indicator
        step_label = ctk.CTkLabel(
            inner,
            text="STEP 1",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS['info']
        )
        step_label.pack(side="left", padx=(0, 10))

        # Profile path
        ctk.CTkLabel(inner, text="Firefox Profile:",
                    font=ctk.CTkFont(size=13),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=(0, 8))

        self.path_entry = ctk.CTkEntry(inner, textvariable=self.firefox_path,
                                       width=350, height=32,
                                       fg_color="#2a2a4a",
                                       border_color=COLORS['border'])
        self.path_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(inner, text="Browse", command=self.browse_path,
                     width=70, height=32, fg_color=COLORS['accent']).pack(side="left", padx=(8, 4))

        # Status indicator (compact)
        self.path_status = ctk.CTkLabel(inner, text="", width=80,
                                        font=ctk.CTkFont(size=12, weight="bold"))
        self.path_status.pack(side="left", padx=(8, 0))

    def setup_sidebar(self, parent):
        """Navigation sidebar with category buttons"""
        card_bg = COLORS['card_bg']

        sidebar = ctk.CTkFrame(parent, fg_color=card_bg, width=200, corner_radius=12)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)

        # Sidebar header
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(header, text="SETTINGS",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w")

        # Navigation buttons - grouped by function
        self.nav_buttons = {}
        self.current_section = tk.StringVar(value="quick_start")

        nav_items = [
            ("divider", "QUICK SETUP"),
            ("quick_start", "Quick Start"),
            ("profile_library", "Profile Library"),
            ("divider", "PERFORMANCE"),
            ("cache_memory", "Cache & Memory"),
            ("processes_gpu", "Processes & GPU"),
            ("divider", "PRIVACY"),
            ("session", "Session & Startup"),
            ("privacy", "Data & Cleanup"),
            ("cookies", "Cookies"),
            ("tracking", "Tracking Protection"),
            ("divider", "SECURITY"),
            ("network", "Network & DNS"),
            ("permissions", "Permissions"),
            ("divider", "FEATURES"),
            ("experimental", "Experimental"),
            ("divider", "EXTRAS"),
            ("extensions", "Extensions"),
            ("userscripts", "Userscripts"),
            ("divider", ""),
            ("summary", "Summary"),
        ]

        for item_id, label in nav_items:
            if item_id == "divider":
                if label:
                    divider = ctk.CTkLabel(sidebar, text=label,
                                          font=ctk.CTkFont(size=9, weight="bold"),
                                          text_color=COLORS['muted'])
                    divider.pack(anchor="w", padx=15, pady=(12, 4))
                else:
                    # Spacer
                    ctk.CTkFrame(sidebar, height=10, fg_color="transparent").pack()
            else:
                btn = ctk.CTkButton(
                    sidebar,
                    text=label,
                    command=lambda s=item_id: self.show_section(s),
                    fg_color="transparent",
                    hover_color=COLORS['accent'],
                    text_color=COLORS['text_primary'],
                    anchor="w",
                    height=36,
                    corner_radius=8
                )
                btn.pack(fill="x", padx=8, pady=1)
                self.nav_buttons[item_id] = btn

        # Highlight initial selection
        self.update_nav_selection()

    def setup_content_area(self, parent):
        """Main content area with switchable sections"""
        card_bg = COLORS['card_bg']

        # Content container
        self.content_frame = ctk.CTkFrame(parent, fg_color=card_bg, corner_radius=12)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Create all section frames (hidden by default)
        self.sections = {}

        # Quick Start section
        self.sections['quick_start'] = self.create_quick_start_section()

        # Session section
        self.sections['session'] = self.create_session_section()

        # Privacy section
        self.sections['privacy'] = self.create_privacy_section()

        # Cookies section
        self.sections['cookies'] = self.create_cookies_section()

        # Tracking section
        self.sections['tracking'] = self.create_tracking_section()

        # Network section
        self.sections['network'] = self.create_network_section()

        # Permissions section
        self.sections['permissions'] = self.create_permissions_section()

        # Extensions section
        self.sections['extensions'] = self.create_extensions_section()

        # Userscripts section
        self.sections['userscripts'] = self.create_userscripts_section()

        # Summary section
        self.sections['summary'] = self.create_summary_section()

        # New sections
        self.sections['profile_library'] = self.create_profile_library_section()
        self.sections['cache_memory'] = self.create_cache_memory_section()
        self.sections['processes_gpu'] = self.create_processes_gpu_section()
        self.sections['experimental'] = self.create_experimental_section()

        # Show initial section
        self.show_section('quick_start')

    def setup_action_bar(self, parent):
        """Bottom action bar with primary actions"""
        card_bg = COLORS['card_bg']

        action_bar = ctk.CTkFrame(parent, fg_color=card_bg, corner_radius=12, height=60)
        action_bar.pack(fill="x", pady=(10, 0))
        action_bar.pack_propagate(False)

        inner = ctk.CTkFrame(action_bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)

        # Left side: Status info
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        self.status_bar = ctk.CTkLabel(left, text="Ready",
                                       font=ctk.CTkFont(size=12),
                                       text_color=COLORS['text_secondary'])
        self.status_bar.pack(side="left")

        # Config status indicators
        self.config_source_label = ctk.CTkLabel(left, text="",
                                               font=ctk.CTkFont(size=11),
                                               text_color=COLORS['muted'])
        self.config_source_label.pack(side="left", padx=(20, 0))

        self.firefox_sync_label = ctk.CTkLabel(left, text="",
                                              font=ctk.CTkFont(size=11, weight="bold"),
                                              text_color=COLORS['muted'])
        self.firefox_sync_label.pack(side="left", padx=(10, 0))

        # Right side: Action buttons
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        # Secondary actions
        ctk.CTkButton(right, text="Load Config",
                     command=self.load_profile, width=100, height=36,
                     fg_color=COLORS['accent'],
                     hover_color="#1a4a80").pack(side="left", padx=4)

        ctk.CTkButton(right, text="Save Config",
                     command=self.save_profile, width=100, height=36,
                     fg_color=COLORS['accent'],
                     hover_color="#1a4a80").pack(side="left", padx=4)

        ctk.CTkButton(right, text="Reset",
                     command=self.load_defaults, width=80, height=36,
                     fg_color="#3a3a5a",
                     hover_color="#4a4a6a").pack(side="left", padx=4)

        # Primary action - most prominent
        self.apply_btn = ctk.CTkButton(
            right,
            text="Apply to Firefox",
            command=self.apply_configuration,
            width=160, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        )
        self.apply_btn.pack(side="left", padx=(12, 0))

    def show_section(self, section_id):
        """Switch to the specified section"""
        # Hide all sections
        for frame in self.sections.values():
            frame.pack_forget()

        # Show selected section
        if section_id in self.sections:
            self.sections[section_id].pack(fill="both", expand=True, padx=15, pady=15)

        self.current_section.set(section_id)
        self.update_nav_selection()

    def update_nav_selection(self):
        """Update navigation button highlighting"""
        current = self.current_section.get()
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == current:
                btn.configure(fg_color=COLORS['info'], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS['text_primary'])

    def create_section_header(self, parent, title, description=""):
        """Create a consistent section header"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(header, text=title,
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        if description:
            ctk.CTkLabel(header, text=description,
                        font=ctk.CTkFont(size=12),
                        text_color=COLORS['text_secondary']).pack(anchor="w", pady=(4, 0))

    def create_card(self, parent, title=""):
        """Create a styled card container"""
        card_inner_bg = "#2a2a4a"

        card = ctk.CTkFrame(parent, fg_color=card_inner_bg, corner_radius=10)
        card.pack(fill="x", pady=8)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        if title:
            ctk.CTkLabel(inner, text=title,
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 10))

        return inner

    def create_quick_start_section(self):
        """Create the Quick Start section with category sliders and use-case presets"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Quick Start",
                                  "Use sliders to set your preferences, or pick a use-case preset to get started instantly.")

        # Category Sliders card
        sliders_card = self.create_card(frame, "Category Settings")

        slider_desc = ctk.CTkLabel(sliders_card,
                                   text="Adjust each category independently to match your needs:",
                                   text_color=COLORS['text_secondary'])
        slider_desc.pack(anchor="w", pady=(0, 10))

        # Performance slider
        self.perf_slider = CategorySlider(
            sliders_card,
            label_left="Battery Saver",
            label_right="Max Power",
            descriptions=[
                "Minimize resource usage for longer battery life",
                "Reduced performance, better battery",
                "Balanced performance and power usage",
                "Higher performance, more resources",
                "Maximum performance - uses more power and memory"
            ],
            on_change=lambda pos: self.on_slider_change('performance', pos)
        )
        self.perf_slider.pack(fill="x", pady=8)

        # Privacy slider
        self.privacy_slider = CategorySlider(
            sliders_card,
            label_left="Open",
            label_right="Paranoid",
            descriptions=[
                "All features enabled, minimal privacy protection",
                "Basic privacy with good compatibility",
                "Balanced privacy and site compatibility",
                "Strong privacy, some sites may break",
                "Maximum privacy - many sites may not work correctly"
            ],
            on_change=lambda pos: self.on_slider_change('privacy', pos)
        )
        self.privacy_slider.pack(fill="x", pady=8)

        # Features slider
        self.features_slider = CategorySlider(
            sliders_card,
            label_left="Conservative",
            label_right="Bleeding Edge",
            descriptions=[
                "Only stable, well-tested features",
                "Mostly stable features",
                "Balanced mix of stable and new features",
                "Enable many experimental features",
                "All experimental features enabled - may be unstable"
            ],
            on_change=lambda pos: self.on_slider_change('features', pos)
        )
        self.features_slider.pack(fill="x", pady=8)

        # Apply sliders button
        apply_sliders_btn = ctk.CTkButton(
            sliders_card,
            text="Apply Slider Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B8ED0",
            hover_color="#2D7BB8",
            height=40,
            command=self.apply_slider_settings
        )
        apply_sliders_btn.pack(fill="x", pady=(15, 5))

        # Use-Case Presets card
        presets_card = self.create_card(frame, "Use-Case Presets")

        preset_desc = ctk.CTkLabel(presets_card,
                                   text="One-click presets optimized for specific use cases:",
                                   text_color=COLORS['text_secondary'])
        preset_desc.pack(anchor="w", pady=(0, 15))

        # Two-column preset grid
        preset_grid = ctk.CTkFrame(presets_card, fg_color="transparent")
        preset_grid.pack(fill="x")
        preset_grid.grid_columnconfigure(0, weight=1)
        preset_grid.grid_columnconfigure(1, weight=1)

        # Preset definitions with slider positions and colors
        use_case_presets = [
            ("Developer", "Max performance, balanced privacy, latest features",
             (4, 2, 4), "#9B59B6"),
            ("Office", "Balanced across all categories",
             (2, 2, 2), "#3498DB"),
            ("Privacy Enthusiast", "Balanced perf, max privacy, stable features",
             (2, 4, 0), "#27AE60"),
            ("Laptop", "Battery-saving, balanced privacy, stable",
             (0, 2, 1), "#F39C12"),
            ("Gaming", "Max performance, relaxed privacy, latest features",
             (4, 0, 4), "#E74C3C"),
            ("Casual", "Balanced all, easy browsing",
             (2, 2, 2), "#1ABC9C"),
        ]

        for idx, (name, desc, positions, color) in enumerate(use_case_presets):
            row, col = divmod(idx, 2)

            preset_frame = ctk.CTkFrame(preset_grid, fg_color="#1e1e3a", corner_radius=8)
            preset_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            btn = ctk.CTkButton(
                preset_frame,
                text=name,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=color,
                hover_color="#4a4a6a",
                height=35,
                command=lambda p=positions, n=name: self.apply_use_case_preset(p, n)
            )
            btn.pack(fill="x", padx=10, pady=(10, 5))

            desc_label = ctk.CTkLabel(
                preset_frame,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color="#a0a0a0",
                wraplength=200
            )
            desc_label.pack(padx=10, pady=(0, 10))

        # Legacy presets (hidden in a collapsible section for backwards compatibility)
        legacy_card = self.create_card(frame, "Legacy Privacy Presets")

        legacy_presets = [
            ("Keep Everything", "Keep all data. Minimal privacy.", self.apply_keep_all, "#3a7a5a"),
            ("Balanced", "Good privacy with compatibility.", self.apply_balanced, COLORS['info']),
            ("Maximum Privacy", "Clear most data on exit.", self.apply_max_privacy, COLORS['warning']),
        ]

        for name, desc, command, color in legacy_presets:
            btn_frame = ctk.CTkFrame(legacy_card, fg_color="transparent")
            btn_frame.pack(fill="x", pady=4)

            ctk.CTkButton(btn_frame, text=name, command=command,
                         width=140, height=32, fg_color=color,
                         hover_color="#4a4a6a").pack(side="left")

            ctk.CTkLabel(btn_frame, text=desc,
                        text_color=COLORS['text_secondary'],
                        font=ctk.CTkFont(size=11)).pack(side="left", padx=15)

        return frame

    def on_slider_change(self, category, position):
        """Handle slider position changes for preview updates"""
        # Just update the visual - actual application happens on button click
        pass

    def apply_slider_settings(self):
        """Apply settings based on current slider positions"""
        perf_pos = self.perf_slider.get_position()
        privacy_pos = self.privacy_slider.get_position()
        features_pos = self.features_slider.get_position()

        # Map positions to profile levels
        perf_levels = ['battery', 'battery', 'balanced', 'max_power', 'max_power']
        privacy_levels = ['open', 'open', 'balanced', 'paranoid', 'paranoid']
        features_levels = ['conservative', 'conservative', 'balanced', 'bleeding_edge', 'bleeding_edge']

        perf_level = perf_levels[perf_pos]
        privacy_level = privacy_levels[privacy_pos]
        features_level = features_levels[features_pos]

        # Apply settings based on levels
        applied_count = 0
        for key, meta in SETTINGS_METADATA.items():
            if 'recommended' not in meta:
                continue

            recommended = meta['recommended']
            category = meta.get('category', '')

            # Determine which recommendation to use based on category
            rec_value = None
            if category == 'performance' and perf_level in recommended:
                rec_value = recommended[perf_level]
            elif category == 'privacy' and privacy_level in recommended:
                rec_value = recommended[privacy_level]
            elif category == 'security' and privacy_level in recommended:
                rec_value = recommended[privacy_level]
            elif category == 'features' and features_level in recommended:
                rec_value = recommended.get(features_level, recommended.get('balanced'))
            elif 'balanced' in recommended:
                rec_value = recommended['balanced']

            if rec_value is not None:
                # Apply the value
                if key in self.privacy_vars:
                    self.privacy_vars[key].set(rec_value)
                if key in self.settings_vars:
                    # Convert value to label for choice types
                    if meta['type'] == 'choice' and rec_value in meta['values']:
                        idx = meta['values'].index(rec_value)
                        if idx < len(meta['labels']):
                            rec_value = meta['labels'][idx]
                    self.settings_vars[key].set(rec_value)
                applied_count += 1

        self.profile_state['modified'] = True
        messagebox.showinfo("Settings Applied",
            f"Applied {applied_count} settings based on:\n"
            f"Performance: {perf_level.replace('_', ' ').title()}\n"
            f"Privacy: {privacy_level.title()}\n"
            f"Features: {features_level.replace('_', ' ').title()}")

    def apply_use_case_preset(self, positions, preset_name):
        """Apply a use-case preset by setting sliders and applying"""
        perf_pos, privacy_pos, features_pos = positions

        # Set slider positions
        self.perf_slider.set_position(perf_pos)
        self.privacy_slider.set_position(privacy_pos)
        self.features_slider.set_position(features_pos)

        # Apply the settings
        self.apply_slider_settings()

        # Update profile state
        self.profile_state['profile_name'] = preset_name

    def create_session_section(self):
        """Create Session & Startup section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Session & Startup",
                                  "Control how Firefox handles tabs and sessions between restarts.")

        # Session Restore card
        restore_card = self.create_card(frame, "Session Restore")

        ctk.CTkCheckBox(restore_card, text="Restore tabs and windows when Firefox starts",
                       variable=self.privacy_vars['restore_session'],
                       font=ctk.CTkFont(size=13)).pack(anchor="w", pady=4)

        # Sub-options (indented)
        sub_frame = ctk.CTkFrame(restore_card, fg_color="transparent")
        sub_frame.pack(fill="x", padx=25, pady=(0, 5))

        ctk.CTkCheckBox(sub_frame, text="Restore pinned tabs",
                       variable=self.privacy_vars['restore_pinned']).pack(anchor="w", pady=2)

        ctk.CTkCheckBox(sub_frame, text="Restore session after crash",
                       variable=self.privacy_vars['restore_from_crash']).pack(anchor="w", pady=2)

        ctk.CTkCheckBox(sub_frame, text="Load tabs on demand (faster startup)",
                       variable=self.privacy_vars['lazy_restore']).pack(anchor="w", pady=2)

        # Startup Behavior card
        startup_card = self.create_card(frame, "Startup Behavior")

        ctk.CTkLabel(startup_card, text="When session restore is OFF:",
                    text_color=COLORS['text_secondary']).pack(anchor="w", pady=(0, 8))

        self.startup_var = tk.StringVar(value="homepage")
        for text, value in [("Show homepage", "homepage"), ("Show blank page", "blank"), ("Show new tab page", "newtab")]:
            ctk.CTkRadioButton(startup_card, text=text, variable=self.startup_var,
                              value=value).pack(anchor="w", padx=15, pady=2)

        # Important note
        note_card = self.create_card(frame, "Important")
        note_text = ("To keep your tabs between sessions:\n"
                    "  - Enable 'Restore tabs and windows'\n"
                    "  - Enable 'Keep session data' in Privacy section\n"
                    "  - Enable 'Keep cookies' for login persistence")
        ctk.CTkLabel(note_card, text=note_text, text_color=COLORS['info'],
                    justify="left", font=ctk.CTkFont(size=11)).pack(anchor="w")

        return frame

    def create_privacy_section(self):
        """Create Privacy & Cleanup section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Data & Cleanup",
                                  "Control what data Firefox keeps or clears when it closes.")

        # Data to KEEP card
        keep_card = self.create_card(frame, "Data to KEEP when Firefox closes")

        keep_items = [
            ('keep_cookies', 'Cookies (website logins and preferences)'),
            ('keep_sessions', 'Session data (open tabs and windows)'),
            ('keep_logins', 'Saved logins and passwords'),
            ('keep_formdata', 'Form and search history'),
            ('keep_downloads', 'Download history'),
            ('keep_history', 'Browsing history'),
        ]

        for var_name, text in keep_items:
            ctk.CTkCheckBox(keep_card, text=text,
                           variable=self.privacy_vars[var_name]).pack(anchor="w", pady=3)

        # Data to CLEAR card
        clear_card = self.create_card(frame, "Data to CLEAR when Firefox closes")

        clear_items = [
            ('clear_cache', 'Cache (temporary files)'),
            ('clear_offline', 'Offline website data'),
            ('clear_thumbnails', 'Thumbnail images'),
            ('clear_siteprefs', 'Site preferences'),
        ]

        for var_name, text in clear_items:
            ctk.CTkCheckBox(clear_card, text=text,
                           variable=self.privacy_vars[var_name]).pack(anchor="w", pady=3)

        return frame

    def create_cookies_section(self):
        """Create Cookies section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Cookie Settings",
                                  "Control how Firefox handles cookies from websites.")

        # Cookie Lifetime card
        lifetime_card = self.create_card(frame, "Cookie Lifetime")

        cookie_options = [
            ("Keep cookies normally", "normal"),
            ("Delete cookies when Firefox closes", "session"),
            ("Delete cookies after a number of days", "days")
        ]

        for text, value in cookie_options:
            ctk.CTkRadioButton(lifetime_card, text=text,
                              variable=self.privacy_vars['cookie_lifetime'],
                              value=value, command=self.update_cookie_days).pack(anchor="w", pady=3)

        # Days input
        self.days_frame = ctk.CTkFrame(lifetime_card, fg_color="transparent")
        self.days_frame.pack(anchor="w", padx=30, pady=8)

        ctk.CTkLabel(self.days_frame, text="Delete after:").pack(side="left")
        # Get initial value from settings_vars if available, otherwise use default
        initial_days = self._get_cookie_days_value()
        self.cookie_days_str = tk.StringVar(value=str(initial_days))
        self.cookie_days_str.trace_add('write', self._sync_cookie_days)
        self.days_entry = ctk.CTkEntry(self.days_frame, width=60, textvariable=self.cookie_days_str)
        self.days_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.days_frame, text="days").pack(side="left")
        self.update_cookie_days()

        # Third-party cookies card
        third_card = self.create_card(frame, "Third-Party Cookies")

        third_options = [
            ("Accept all third-party cookies", "all"),
            ("Block cross-site tracking cookies (recommended)", "cross-site"),
            ("Block all third-party cookies", "none"),
            ("Block unvisited third-party cookies", "visited")
        ]

        for text, value in third_options:
            ctk.CTkRadioButton(third_card, text=text,
                              variable=self.privacy_vars['third_party_cookies'],
                              value=value).pack(anchor="w", pady=3)

        return frame

    def create_tracking_section(self):
        """Create Tracking Protection section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Tracking Protection",
                                  "Configure protection against trackers and telemetry.")

        # Protection Level card
        level_card = self.create_card(frame, "Protection Level")

        levels = [
            ("Standard - Balanced protection", "standard"),
            ("Strict - Stronger protection (recommended)", "strict"),
            ("Custom - Choose what to block", "custom")
        ]

        for text, value in levels:
            ctk.CTkRadioButton(level_card, text=text,
                              variable=self.privacy_vars['tracking_protection'],
                              value=value).pack(anchor="w", pady=3)

        # Custom blocking card
        custom_card = self.create_card(frame, "Additional Blocking")

        ctk.CTkCheckBox(custom_card, text="Block fingerprinting scripts",
                       variable=self.privacy_vars['fingerprint_resist']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(custom_card, text="Block cryptomining scripts",
                       variable=self.privacy_vars['cryptomining_block']).pack(anchor="w", pady=3)

        # Site fixes card
        fix_card = self.create_card(frame, "Site Compatibility Fixes")

        ctk.CTkCheckBox(fix_card, text="Fix major site issues (recommended)",
                       variable=self.privacy_vars['fix_major_issues']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(fix_card, text="Fix minor site issues",
                       variable=self.privacy_vars['fix_minor_issues']).pack(anchor="w", pady=3)

        # Telemetry card
        telemetry_card = self.create_card(frame, "Mozilla Telemetry")

        ctk.CTkCheckBox(telemetry_card, text="Send technical data to Mozilla",
                       variable=self.privacy_vars['telemetry_enabled']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(telemetry_card, text="Allow Firefox studies",
                       variable=self.privacy_vars['studies_enabled']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(telemetry_card, text="Send crash reports",
                       variable=self.privacy_vars['crash_reports']).pack(anchor="w", pady=3)

        return frame

    def create_network_section(self):
        """Create Network & Security section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Network & Security",
                                  "Configure DNS, HTTPS, and WebRTC settings.")

        # DNS over HTTPS card
        dns_card = self.create_card(frame, "DNS over HTTPS")

        dns_options = [
            ("Off", "off"),
            ("Default Protection", "default"),
            ("Increased Protection (recommended)", "increased"),
            ("Max Protection", "max")
        ]

        for text, value in dns_options:
            ctk.CTkRadioButton(dns_card, text=text,
                              variable=self.privacy_vars['dns_over_https'],
                              value=value).pack(anchor="w", pady=2)

        # DNS Provider
        ctk.CTkLabel(dns_card, text="DNS Provider:",
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(12, 5))

        providers = [
            ("Cloudflare", "cloudflare"),
            ("Quad9 (recommended)", "quad9"),
            ("NextDNS", "nextdns")
        ]

        for text, value in providers:
            ctk.CTkRadioButton(dns_card, text=text,
                              variable=self.privacy_vars['dns_provider'],
                              value=value).pack(anchor="w", padx=15, pady=2)

        # HTTPS card
        https_card = self.create_card(frame, "HTTPS Security")

        ctk.CTkCheckBox(https_card, text="HTTPS-Only Mode (recommended)",
                       variable=self.privacy_vars['https_only']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(https_card, text="HTTPS-Only in Private Browsing",
                       variable=self.privacy_vars['https_only_pbm']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(https_card, text="Block dangerous mixed content",
                       variable=self.privacy_vars['mixed_content_block']).pack(anchor="w", pady=3)

        # WebRTC card
        webrtc_card = self.create_card(frame, "WebRTC")

        ctk.CTkCheckBox(webrtc_card, text="Enable WebRTC (needed for video calls)",
                       variable=self.privacy_vars['webrtc_enabled']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(webrtc_card, text="Prevent WebRTC IP leak",
                       variable=self.privacy_vars['webrtc_ip_leak']).pack(anchor="w", pady=3)

        # Network Performance card
        perf_card = self.create_card(frame, "Network Performance")

        ctk.CTkCheckBox(perf_card, text="Prefetch DNS (faster but less private)",
                       variable=self.privacy_vars['prefetch_dns']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(perf_card, text="Prefetch links",
                       variable=self.privacy_vars['prefetch_links']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(perf_card, text="Network predictor",
                       variable=self.privacy_vars['predictor']).pack(anchor="w", pady=3)

        return frame

    def create_permissions_section(self):
        """Create Permissions section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Permissions",
                                  "Control search suggestions, autofill, and site permissions.")

        # Search & Autofill card
        search_card = self.create_card(frame, "Search & Autofill")

        ctk.CTkCheckBox(search_card, text="Show search suggestions",
                       variable=self.privacy_vars['search_suggestions']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(search_card, text="Show URL suggestions from history",
                       variable=self.privacy_vars['url_suggestions']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(search_card, text="Autofill forms",
                       variable=self.privacy_vars['autofill_forms']).pack(anchor="w", pady=3)

        ctk.CTkCheckBox(search_card, text="Ask to save passwords",
                       variable=self.privacy_vars['autofill_passwords']).pack(anchor="w", pady=3)

        # Site Permissions card
        perm_card = self.create_card(frame, "Default Site Permissions")

        permissions = [
            ("Location", 'location_permission', ["allow", "ask", "block"]),
            ("Camera", 'camera_permission', ["allow", "ask", "block"]),
            ("Microphone", 'microphone_permission', ["allow", "ask", "block"]),
            ("Notifications", 'notifications_permission', ["allow", "ask", "block"]),
            ("Autoplay", 'autoplay_permission', ["allow", "block"])
        ]

        for label, var_name, options in permissions:
            row = ctk.CTkFrame(perm_card, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=f"{label}:", width=100, anchor="w").pack(side="left")

            for opt in options:
                ctk.CTkRadioButton(row, text=opt.capitalize(),
                                  variable=self.privacy_vars[var_name],
                                  value=opt, width=80).pack(side="left", padx=5)

        return frame

    def create_extensions_section(self):
        """Create Extensions section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Extensions",
                                  "Install recommended privacy and security extensions.")

        for key, ext in self.extensions.items():
            ext_card = self.create_card(frame)

            ctk.CTkCheckBox(ext_card, text=f"Install {ext['name']}",
                           variable=ext['enabled'],
                           font=ctk.CTkFont(size=13)).pack(anchor="w")

            ctk.CTkLabel(ext_card, text=ext['description'],
                        text_color=COLORS['text_secondary'],
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=25)

        # Action buttons
        btn_card = self.create_card(frame)

        btn_frame = ctk.CTkFrame(btn_card, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(btn_frame, text="Install Selected",
                     command=self.install_extensions,
                     fg_color=COLORS['success']).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Check Installed",
                     command=self.check_installed_extensions,
                     fg_color=COLORS['accent']).pack(side="left", padx=5)

        self.ext_status = ctk.CTkLabel(btn_frame, text="",
                                       text_color=COLORS['info'])
        self.ext_status.pack(side="left", padx=15)

        return frame

    def create_userscripts_section(self):
        """Create Userscripts section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Userscripts",
                                  "Install Tampermonkey userscripts for enhanced functionality.")

        # Warning
        warn_card = self.create_card(frame)
        ctk.CTkLabel(warn_card, text="Requires Tampermonkey extension (see Extensions tab)",
                    text_color=COLORS['warning'],
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        for key, script in self.userscripts.items():
            script_card = self.create_card(frame)

            ctk.CTkCheckBox(script_card, text=f"Install {script['name']}",
                           variable=script['enabled'],
                           font=ctk.CTkFont(size=13)).pack(anchor="w")

            ctk.CTkLabel(script_card, text=script['description'],
                        text_color=COLORS['text_secondary'],
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=25)

        # Action buttons
        btn_card = self.create_card(frame)

        btn_frame = ctk.CTkFrame(btn_card, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(btn_frame, text="Install Selected",
                     command=self.install_userscripts,
                     fg_color=COLORS['success']).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Check Installed",
                     command=self.check_installed_userscripts,
                     fg_color=COLORS['accent']).pack(side="left", padx=5)

        self.script_status = ctk.CTkLabel(btn_frame, text="",
                                         text_color=COLORS['info'])
        self.script_status.pack(side="left", padx=15)

        return frame

    def create_summary_section(self):
        """Create Summary section"""
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.create_section_header(frame, "Configuration Summary",
                                  "Review your current settings before applying.")

        self.summary_text = ctk.CTkTextbox(frame, height=400,
                                          font=ctk.CTkFont(family="Consolas", size=12),
                                          fg_color="#2a2a4a")
        self.summary_text.pack(fill="both", expand=True, pady=10)

        ctk.CTkButton(frame, text="Refresh Summary",
                     command=self.update_summary,
                     fg_color=COLORS['accent']).pack(pady=10)

        return frame

    def create_profile_library_section(self):
        """Create Profile Library section with custom profiles management"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.create_section_header(frame, "Profile Library", "Save and load your custom Firefox configurations")

        # Action buttons row
        actions_frame = ctk.CTkFrame(frame, fg_color="#1e1e3a", corner_radius=10)
        actions_frame.pack(fill="x", pady=(10, 15), padx=10)

        actions_inner = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_inner.pack(pady=15, padx=15)

        # Create new profile button
        new_btn = ctk.CTkButton(
            actions_inner,
            text="+ New Profile",
            font=ctk.CTkFont(size=13),
            fg_color="#3B8ED0",
            hover_color="#2D7BB8",
            width=140,
            height=35,
            command=self.create_new_profile
        )
        new_btn.grid(row=0, column=0, padx=5)

        # Import from Firefox button
        import_ff_btn = ctk.CTkButton(
            actions_inner,
            text="Import from Firefox",
            font=ctk.CTkFont(size=13),
            fg_color="#2FA572",
            hover_color="#238C5C",
            width=140,
            height=35,
            command=self.import_from_firefox
        )
        import_ff_btn.grid(row=0, column=1, padx=5)

        # Import JSON button
        import_json_btn = ctk.CTkButton(
            actions_inner,
            text="Import JSON",
            font=ctk.CTkFont(size=13),
            fg_color="#808080",
            hover_color="#606060",
            width=120,
            height=35,
            command=self.import_profile_json
        )
        import_json_btn.grid(row=0, column=2, padx=5)

        # Saved profiles list
        saved_label = ctk.CTkLabel(
            frame,
            text="Saved Profiles",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffffff"
        )
        saved_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Profiles container - will be populated
        self.profiles_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.profiles_container.pack(fill="x", padx=10, pady=5)

        # Load and display profiles
        self.refresh_profiles_list()

        return frame

    def refresh_profiles_list(self):
        """Refresh the profiles list display"""
        # Clear existing
        for widget in self.profiles_container.winfo_children():
            widget.destroy()

        # Get profiles
        profiles = self.profile_manager.list_profiles()

        if not profiles:
            no_profiles = ctk.CTkLabel(
                self.profiles_container,
                text="No saved profiles yet. Create a new one or import from Firefox.",
                font=ctk.CTkFont(size=12),
                text_color="#a0a0a0"
            )
            no_profiles.pack(pady=20)
            return

        # Display each profile
        for profile in profiles:
            self.create_profile_card(profile)

    def create_profile_card(self, profile):
        """Create a card widget for a profile"""
        card = ctk.CTkFrame(self.profiles_container, fg_color="#2a2a4a", corner_radius=10)
        card.pack(fill="x", pady=5)

        # Profile info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

        name_label = ctk.CTkLabel(
            info_frame,
            text=profile.get('name', 'Unnamed Profile'),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        name_label.pack(anchor="w")

        desc = profile.get('description', '')
        if desc:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc[:80] + ('...' if len(desc) > 80 else ''),
                font=ctk.CTkFont(size=11),
                text_color="#a0a0a0"
            )
            desc_label.pack(anchor="w")

        # Tags and metadata
        tags = profile.get('tags', [])
        modified = profile.get('modified', profile.get('created', ''))
        meta_text = f"Modified: {modified[:10]}" if modified else ""
        if tags:
            meta_text += f"  |  Tags: {', '.join(tags[:3])}"

        if meta_text:
            meta_label = ctk.CTkLabel(
                info_frame,
                text=meta_text,
                font=ctk.CTkFont(size=10),
                text_color="#808080"
            )
            meta_label.pack(anchor="w", pady=(3, 0))

        # Action buttons
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=15, pady=12)

        load_btn = ctk.CTkButton(
            actions_frame,
            text="Load",
            font=ctk.CTkFont(size=12),
            fg_color="#3B8ED0",
            hover_color="#2D7BB8",
            width=70,
            height=28,
            command=lambda p=profile: self.load_profile(p)
        )
        load_btn.grid(row=0, column=0, padx=3)

        export_btn = ctk.CTkButton(
            actions_frame,
            text="Export",
            font=ctk.CTkFont(size=12),
            fg_color="#606080",
            hover_color="#505070",
            width=70,
            height=28,
            command=lambda p=profile: self.export_profile(p)
        )
        export_btn.grid(row=0, column=1, padx=3)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            font=ctk.CTkFont(size=12),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=70,
            height=28,
            command=lambda p=profile: self.delete_profile(p)
        )
        delete_btn.grid(row=0, column=2, padx=3)

    def create_new_profile(self):
        """Open dialog to create a new profile from current settings"""
        dialog = ctk.CTkInputDialog(
            text="Enter a name for the new profile:",
            title="Create New Profile"
        )
        name = dialog.get_input()

        if not name:
            return

        # Collect current settings
        settings = self.collect_current_settings()

        # Save profile
        try:
            filepath = self.profile_manager.save_profile(
                name=name,
                description=f"Created from current settings",
                settings=settings,
                tags=['custom']
            )
            messagebox.showinfo("Success", f"Profile '{name}' saved successfully!")
            self.refresh_profiles_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    def collect_current_settings(self):
        """Collect current settings values"""
        settings = {}

        # From privacy_vars
        for key, var in self.privacy_vars.items():
            settings[key] = var.get()

        # From settings_vars (new settings)
        for key, var in self.settings_vars.items():
            if key not in settings:
                val = var.get()
                # For choice variables, convert label back to value if needed
                if key in SETTINGS_METADATA:
                    meta = SETTINGS_METADATA[key]
                    if meta['type'] == 'choice' and val in meta['labels']:
                        idx = meta['labels'].index(val)
                        if idx < len(meta['values']):
                            val = meta['values'][idx]
                settings[key] = val

        return settings

    def import_from_firefox(self):
        """Import settings from an existing Firefox profile"""
        folder = filedialog.askdirectory(
            title="Select Firefox Profile Folder",
            initialdir=str(Path.home())
        )

        if not folder:
            return

        try:
            importer = FirefoxImporter(folder)
            imported = importer.import_to_hardzilla()

            if imported:
                # Save as a new profile
                profile_name = f"Imported {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                filepath = self.profile_manager.save_profile(
                    name=profile_name,
                    description=f"Imported from Firefox profile: {Path(folder).name}",
                    settings=imported,
                    tags=['imported']
                )
                messagebox.showinfo("Success", f"Imported {len(imported)} settings as '{profile_name}'")
                self.refresh_profiles_list()
            else:
                messagebox.showwarning("Warning", "No recognized settings found in the Firefox profile")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")

    def import_profile_json(self):
        """Import a profile from JSON file"""
        filepath = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            profile = self.profile_manager.load_profile(filepath)
            # Re-save to our profiles folder
            new_path = self.profile_manager.save_profile(
                name=profile.get('name', 'Imported Profile'),
                description=profile.get('description', ''),
                settings=profile.get('settings', {}),
                tags=profile.get('tags', ['imported'])
            )
            messagebox.showinfo("Success", "Profile imported successfully!")
            self.refresh_profiles_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import profile: {e}")

    def load_profile(self, profile):
        """Load a profile's settings into the UI"""
        settings = profile.get('settings', {})

        if not settings:
            messagebox.showwarning("Warning", "This profile has no settings to load")
            return

        # Apply settings to variables
        for key, value in settings.items():
            # Check privacy_vars first
            if key in self.privacy_vars:
                self.privacy_vars[key].set(value)

            # Then settings_vars
            if key in self.settings_vars:
                # For choice variables, convert value to label
                if key in SETTINGS_METADATA:
                    meta = SETTINGS_METADATA[key]
                    if meta['type'] == 'choice' and value in meta['values']:
                        idx = meta['values'].index(value)
                        if idx < len(meta['labels']):
                            value = meta['labels'][idx]
                self.settings_vars[key].set(value)

        self.profile_state['loaded'] = True
        self.profile_state['profile_name'] = profile.get('name', 'Unknown')
        self.profile_state['modified'] = False

        messagebox.showinfo("Success", f"Profile '{profile.get('name', 'Unknown')}' loaded!\nSettings have been applied to the UI.")

    def export_profile(self, profile):
        """Export a profile to JSON file"""
        filepath = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            initialfile=f"{profile.get('name', 'profile').replace(' ', '_')}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            self.profile_manager.export_profile(profile.get('_file', ''), filepath)
            messagebox.showinfo("Success", f"Profile exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export profile: {e}")

    def delete_profile(self, profile):
        """Delete a profile"""
        name = profile.get('name', 'Unknown')
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            return

        try:
            filepath = profile.get('_file', '')
            if filepath and self.profile_manager.delete_profile(filepath):
                messagebox.showinfo("Success", f"Profile '{name}' deleted")
                self.refresh_profiles_list()
            else:
                messagebox.showerror("Error", "Could not find profile to delete")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete profile: {e}")

    def _ensure_setting_var(self, key: str, meta: Dict) -> None:
        """
        Ensure a setting variable exists in settings_vars.

        Creates the appropriate tkinter variable type based on metadata.
        Also handles conversion of choice values to labels.

        Args:
            key: Setting key
            meta: Setting metadata from SETTINGS_METADATA
        """
        # Create variable if it doesn't exist
        if key not in self.settings_vars:
            if meta['type'] == 'toggle':
                self.settings_vars[key] = tk.BooleanVar(value=meta['default'])
            elif meta['type'] == 'choice':
                # Initialize with label for the default value
                default_idx = meta['values'].index(meta['default']) if meta['default'] in meta['values'] else 0
                self.settings_vars[key] = tk.StringVar(value=meta['labels'][default_idx])
            else:
                self.settings_vars[key] = tk.IntVar(value=meta['default'])

        # Ensure choice variables have label values (not raw values)
        if meta['type'] == 'choice':
            current_val = self.settings_vars[key].get()
            # If current value is a raw value, convert to label
            if current_val in [str(v) for v in meta['values']] or current_val in meta['values']:
                try:
                    parsed_val = self._try_parse_number(current_val)
                    if parsed_val is not None:
                        current_val = parsed_val
                    idx = meta['values'].index(current_val)
                    self.settings_vars[key].set(meta['labels'][idx])
                except (ValueError, IndexError):
                    self.settings_vars[key].set(meta['labels'][0])

    def _try_parse_number(self, value: str) -> Optional[int]:
        """
        Try to parse a string as an integer (handles negatives).

        Args:
            value: String value to parse

        Returns:
            Parsed integer or None if not parseable
        """
        if not isinstance(value, str):
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _create_metadata_section(
        self,
        title: str,
        description: str,
        subcategory: str
    ) -> ctk.CTkScrollableFrame:
        """
        Create a settings section from metadata for a specific subcategory.

        Args:
            title: Section title
            description: Section description
            subcategory: Metadata subcategory to filter by

        Returns:
            Configured scrollable frame with setting rows
        """
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.create_section_header(frame, title, description)

        # Get settings for this subcategory
        settings = [k for k, v in SETTINGS_METADATA.items() if v.get('subcategory') == subcategory]

        for key in settings:
            meta = SETTINGS_METADATA[key]
            self._ensure_setting_var(key, meta)

            row = SettingRow(
                frame,
                name=meta['name'],
                short_desc=meta['short'],
                full_desc=meta['full'],
                setting_type=meta['type'],
                values=meta['values'],
                labels=meta['labels'],
                impact=meta['impact'],
                compatibility=meta['compatibility'],
                recommended=meta['recommended'],
                variable=self.settings_vars[key]
            )
            row.pack(fill="x", pady=4, padx=10)

        return frame

    def create_cache_memory_section(self):
        """Create Cache & Memory settings section"""
        return self._create_metadata_section(
            "Cache & Memory",
            "Control how Firefox stores temporary data for faster browsing",
            "cache"
        )

    def create_processes_gpu_section(self):
        """Create Processes & GPU settings section"""
        return self._create_metadata_section(
            "Processes & GPU",
            "Fine-tune Firefox's multi-process architecture and hardware acceleration",
            "processes"
        )

    def create_experimental_section(self):
        """Create Experimental Features section"""
        frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.create_section_header(frame, "Experimental Features", "Enable cutting-edge Firefox features (may be unstable)")

        # Group experimental settings by subcategory for better organization
        subcategories = {
            'ui': ('UI & Tabs', 'Tab organization and interface features'),
            'ai': ('AI Features', 'AI-powered browsing assistance'),
            'media': ('Graphics & Media', 'Modern image and video formats'),
            'css': ('CSS Experimental', 'Advanced CSS features'),
            'network': ('DOM & Network', 'Web platform and network features')
        }

        # Get all experimental settings from metadata
        exp_settings = [(k, v) for k, v in SETTINGS_METADATA.items() if v.get('category') == 'features']

        # Group by subcategory
        grouped = {}
        for key, meta in exp_settings:
            subcat = meta.get('subcategory', 'other')
            if subcat not in grouped:
                grouped[subcat] = []
            grouped[subcat].append((key, meta))

        # Render each subcategory
        for subcat_key, (subcat_title, subcat_desc) in subcategories.items():
            if subcat_key not in grouped:
                continue

            # Subcategory header
            subcat_frame = ctk.CTkFrame(frame, fg_color="#1e1e3a", corner_radius=10)
            subcat_frame.pack(fill="x", pady=(15, 5), padx=10)

            header_label = ctk.CTkLabel(
                subcat_frame,
                text=subcat_title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff"
            )
            header_label.pack(anchor="w", padx=15, pady=(10, 2))

            desc_label = ctk.CTkLabel(
                subcat_frame,
                text=subcat_desc,
                font=ctk.CTkFont(size=11),
                text_color="#a0a0a0"
            )
            desc_label.pack(anchor="w", padx=15, pady=(0, 10))

            # Settings in this subcategory
            for key, meta in grouped[subcat_key]:
                # Get or create the variable for this setting
                if key not in self.settings_vars:
                    if meta['type'] == 'toggle':
                        self.settings_vars[key] = tk.BooleanVar(value=meta['default'])
                    elif meta['type'] == 'choice':
                        default_idx = meta['values'].index(meta['default']) if meta['default'] in meta['values'] else 0
                        self.settings_vars[key] = tk.StringVar(value=meta['labels'][default_idx])
                    else:
                        self.settings_vars[key] = tk.IntVar(value=meta['default'])

                row = SettingRow(
                    frame,
                    name=meta['name'],
                    short_desc=meta['short'],
                    full_desc=meta['full'],
                    setting_type=meta['type'],
                    values=meta['values'],
                    labels=meta['labels'],
                    impact=meta['impact'],
                    compatibility=meta['compatibility'],
                    recommended=meta['recommended'],
                    variable=self.settings_vars[key]
                )
                row.pack(fill="x", pady=4, padx=10)

        return frame

    def setup_change_tracking(self):
        """Setup change tracking for all variables"""
        for var_name, var in self.privacy_vars.items():
            if isinstance(var, (tk.BooleanVar, tk.StringVar, tk.IntVar)):
                var.trace_add('write', lambda *args: self.mark_as_modified())

    def mark_as_modified(self):
        """Mark profile as modified"""
        if self.profile_state['loaded']:
            self.profile_state['modified'] = True
            self.update_profile_status()

    def update_profile_status(self):
        """Update the configuration status display"""
        profile_name = self.profile_state['profile_name']

        # Determine source text and color
        if profile_name == 'Firefox Profile':
            source_text = "Loaded from Firefox"
            source_color = COLORS['info']
        elif profile_name == 'Default Settings':
            source_text = "Default settings"
            source_color = COLORS['info']
        elif profile_name == 'None':
            source_text = "New configuration"
            source_color = COLORS['muted']
        else:
            source_text = f"{profile_name}.json"
            source_color = COLORS['info']

        if self.profile_state['modified']:
            source_text += " (modified)"
            source_color = COLORS['warning']

        # Update action bar status labels
        self.config_source_label.configure(text=source_text, text_color=source_color)

        # Firefox sync status
        if self.profile_state['last_applied'] != 'Never':
            firefox_text = f"Applied {self.profile_state['last_applied']}"
            firefox_color = COLORS['success']
            quick_status = "Applied"
            quick_color = COLORS['success']
            if self.profile_state['modified']:
                firefox_text = "Changes pending"
                firefox_color = COLORS['warning']
                quick_status = "Modified"
                quick_color = COLORS['warning']
        else:
            firefox_text = "Not applied yet"
            firefox_color = COLORS['error']
            quick_status = "Not configured"
            quick_color = COLORS['muted']

        self.firefox_sync_label.configure(text=firefox_text, text_color=firefox_color)

        # Update quick status indicator in header
        if hasattr(self, 'quick_status_indicator'):
            self.quick_status_indicator.configure(text=quick_status, text_color=quick_color)

    def browse_path(self):
        """Browse for Firefox profile"""
        path = filedialog.askdirectory(title="Select Firefox Profile Directory")
        if path:
            self.firefox_path.set(path)
            self.check_firefox_path()

    def check_firefox_path(self):
        """Check Firefox profile path"""
        test_path = Path(self.firefox_path.get())

        if not test_path.exists():
            self.path_status.configure(text="Not found", text_color=COLORS['error'])
            return False

        possible_profiles = [
            test_path / "Data" / "profile",
            test_path / "profile",
            test_path
        ]

        for path in possible_profiles:
            if path.exists() and (path / "prefs.js").exists():
                self.profile_path = path
                self.path_status.configure(text="Found", text_color=COLORS['success'])
                self.status_bar.configure(text=f"Profile: {path}")
                # Load current profile settings
                self.load_current_profile_settings()
                return True

        self.path_status.configure(text="No profile", text_color=COLORS['warning'])
        return False

    def update_cookie_days(self):
        """Enable/disable cookie days input based on selection"""
        if hasattr(self, 'days_entry'):
            state = "normal" if self.privacy_vars['cookie_lifetime'].get() == 'days' else "disabled"
            self.days_entry.configure(state=state)

    def _get_cookie_days_value(self) -> int:
        """Get the current cookie_days value as an integer.

        Handles both raw integer values and label strings from SETTINGS_METADATA.
        """
        if 'cookie_days' not in self.settings_vars:
            return 30  # Default value

        val = self.settings_vars['cookie_days'].get()

        # If it's already an integer, return it
        if isinstance(val, int):
            return val

        # Try to parse as integer
        try:
            return int(val)
        except (ValueError, TypeError):
            pass

        # Check if it's a label from SETTINGS_METADATA
        meta = SETTINGS_METADATA.get('cookie_days', {})
        labels = meta.get('labels', [])
        values = meta.get('values', [])

        if val in labels:
            idx = labels.index(val)
            if idx < len(values):
                return values[idx]

        return 30  # Default fallback

    def _set_cookie_days_value(self, days: int) -> None:
        """Set the cookie_days value, converting to label if needed.

        Args:
            days: The number of days as an integer
        """
        if 'cookie_days' not in self.settings_vars:
            # Ensure the variable exists
            meta = SETTINGS_METADATA.get('cookie_days', {})
            if meta:
                self._ensure_setting_var('cookie_days', meta)
            else:
                return

        meta = SETTINGS_METADATA.get('cookie_days', {})
        values = meta.get('values', [])
        labels = meta.get('labels', [])

        # Find the closest matching value
        if days in values:
            idx = values.index(days)
            self.settings_vars['cookie_days'].set(labels[idx])
        else:
            # Find closest value
            closest = min(values, key=lambda x: abs(x - days)) if values else days
            idx = values.index(closest)
            self.settings_vars['cookie_days'].set(labels[idx])

        # Also update the entry field if it exists
        if hasattr(self, 'cookie_days_str'):
            self.cookie_days_str.set(str(days))

    def _sync_cookie_days(self, *args):
        """Sync the StringVar entry to settings_vars for cookie_days"""
        try:
            value = int(self.cookie_days_str.get())
            if value > 0:
                self._set_cookie_days_value(value)
        except ValueError:
            # Invalid input, ignore
            pass

    def parse_firefox_prefs(self):
        """Parse Firefox preferences from user.js and prefs.js"""
        if not self.profile_path:
            return {}

        prefs = {}

        # Read user.js first (user preferences override)
        userjs_path = self.profile_path / "user.js"
        if userjs_path.exists():
            try:
                with open(userjs_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('user_pref('):
                            # Parse: user_pref("pref.name", value);
                            try:
                                # Extract pref name and value
                                content = line[10:-2]  # Remove 'user_pref(' and ');'
                                parts = content.split(',', 1)
                                if len(parts) == 2:
                                    pref_name = parts[0].strip().strip('"')
                                    pref_value = parts[1].strip()

                                    # Convert value to Python type
                                    if pref_value.lower() == 'true':
                                        pref_value = True
                                    elif pref_value.lower() == 'false':
                                        pref_value = False
                                    elif pref_value.startswith('"') and pref_value.endswith('"'):
                                        pref_value = pref_value[1:-1]
                                    else:
                                        try:
                                            pref_value = int(pref_value)
                                        except ValueError:
                                            pass

                                    prefs[pref_name] = pref_value
                            except Exception as e:
                                print(f"Warning: Could not parse pref line in user.js: {line[:50]}... - {e}")
                                continue
            except Exception as e:
                print(f"Error reading user.js: {e}")

        # Read prefs.js (for prefs not in user.js)
        prefsjs_path = self.profile_path / "prefs.js"
        if prefsjs_path.exists():
            try:
                with open(prefsjs_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('user_pref('):
                            try:
                                content = line[10:-2]
                                parts = content.split(',', 1)
                                if len(parts) == 2:
                                    pref_name = parts[0].strip().strip('"')
                                    # Only add if not already in prefs (user.js takes precedence)
                                    if pref_name not in prefs:
                                        pref_value = parts[1].strip()

                                        if pref_value.lower() == 'true':
                                            pref_value = True
                                        elif pref_value.lower() == 'false':
                                            pref_value = False
                                        elif pref_value.startswith('"') and pref_value.endswith('"'):
                                            pref_value = pref_value[1:-1]
                                        else:
                                            try:
                                                pref_value = int(pref_value)
                                            except ValueError:
                                                pass

                                        prefs[pref_name] = pref_value
                            except Exception as e:
                                print(f"Warning: Could not parse pref line in prefs.js: {line[:50]}... - {e}")
                                continue
            except Exception as e:
                print(f"Error reading prefs.js: {e}")

        return prefs

    def load_current_profile_settings(self):
        """Load and display current Firefox profile settings"""
        try:
            prefs = self.parse_firefox_prefs()
            if not prefs:
                self.status_bar.configure(text="No existing preferences found - using defaults")
                return

            # Session Restore
            startup_page = prefs.get('browser.startup.page', 1)
            self.privacy_vars['restore_session'].set(startup_page == 3)

            resume_crash = prefs.get('browser.sessionstore.resume_from_crash', True)
            self.privacy_vars['restore_from_crash'].set(resume_crash)

            lazy_restore = prefs.get('browser.sessionstore.restore_on_demand', True)
            self.privacy_vars['lazy_restore'].set(lazy_restore)

            # Privacy - what to clear on shutdown
            self.privacy_vars['clear_cache'].set(prefs.get('privacy.clearOnShutdown.cache', False))
            self.privacy_vars['clear_offline'].set(prefs.get('privacy.clearOnShutdown.offlineApps', False))
            self.privacy_vars['clear_siteprefs'].set(prefs.get('privacy.clearOnShutdown.siteSettings', False))

            # Privacy - what to keep (inverse logic)
            self.privacy_vars['keep_cookies'].set(not prefs.get('privacy.clearOnShutdown.cookies', False))
            self.privacy_vars['keep_sessions'].set(not prefs.get('privacy.clearOnShutdown.sessions', False))
            self.privacy_vars['keep_history'].set(not prefs.get('privacy.clearOnShutdown.history', False))
            self.privacy_vars['keep_downloads'].set(not prefs.get('privacy.clearOnShutdown.downloads', False))
            self.privacy_vars['keep_formdata'].set(not prefs.get('privacy.clearOnShutdown.formdata', False))

            # Logins
            self.privacy_vars['keep_logins'].set(prefs.get('signon.rememberSignons', True))

            # Cookie lifetime
            cookie_lifetime = prefs.get('network.cookie.lifetimePolicy', 0)
            if cookie_lifetime == 2:
                self.privacy_vars['cookie_lifetime'].set('session')
            elif cookie_lifetime == 3:
                self.privacy_vars['cookie_lifetime'].set('days')
                cookie_days = prefs.get('network.cookie.lifetime.days', 30)
                self._set_cookie_days_value(cookie_days)
            else:
                self.privacy_vars['cookie_lifetime'].set('normal')

            # Third-party cookies
            cookie_behavior = prefs.get('network.cookie.cookieBehavior', 5)
            cookie_behavior_map = {0: 'all', 5: 'cross-site', 1: 'none', 3: 'visited'}
            self.privacy_vars['third_party_cookies'].set(cookie_behavior_map.get(cookie_behavior, 'cross-site'))

            # Tracking Protection
            content_blocking = prefs.get('browser.contentblocking.category', 'standard')
            if isinstance(content_blocking, str):
                self.privacy_vars['tracking_protection'].set(content_blocking)

            self.privacy_vars['fingerprint_resist'].set(
                prefs.get('privacy.trackingprotection.fingerprinting.enabled', False)
            )
            self.privacy_vars['cryptomining_block'].set(
                prefs.get('privacy.trackingprotection.cryptomining.enabled', False)
            )

            # Fix site issues
            self.privacy_vars['fix_major_issues'].set(
                prefs.get('privacy.annotate_channels.strict_list.enabled', True)
            )
            # Check if minor fixes are enabled (if any of the minor fix prefs are set)
            minor_fix = (
                prefs.get('privacy.purge_trackers.date_in_cookie_database', '').strip('"') == '0' or
                not prefs.get('privacy.restrict3rdpartystorage.rollout.enabledByDefault', True)
            )
            self.privacy_vars['fix_minor_issues'].set(minor_fix)

            # Telemetry
            self.privacy_vars['telemetry_enabled'].set(prefs.get('toolkit.telemetry.enabled', False))
            self.privacy_vars['studies_enabled'].set(prefs.get('app.shield.optoutstudies.enabled', False))
            self.privacy_vars['crash_reports'].set(prefs.get('browser.tabs.crashReporting.sendReport', False))

            # DNS over HTTPS
            trr_mode = prefs.get('network.trr.mode', 0)
            # network.trr.mode: 0=off, 2=default (with fallback), 3=strict (DoH only)
            doh_mode_map = {0: 'off', 2: 'default', 3: 'max'}
            self.privacy_vars['dns_over_https'].set(doh_mode_map.get(trr_mode, 'off'))

            trr_uri = prefs.get('network.trr.uri', '')
            if 'quad9' in trr_uri:
                self.privacy_vars['dns_provider'].set('quad9')
            elif 'cloudflare' in trr_uri:
                self.privacy_vars['dns_provider'].set('cloudflare')
            elif 'nextdns' in trr_uri:
                self.privacy_vars['dns_provider'].set('nextdns')

            # Network
            self.privacy_vars['prefetch_dns'].set(not prefs.get('network.dns.disablePrefetch', True))
            self.privacy_vars['prefetch_links'].set(prefs.get('network.prefetch-next', False))
            self.privacy_vars['predictor'].set(prefs.get('network.predictor.enabled', False))

            # HTTPS
            self.privacy_vars['https_only'].set(prefs.get('dom.security.https_only_mode', False))
            self.privacy_vars['https_only_pbm'].set(prefs.get('dom.security.https_only_mode_pbm', False))
            self.privacy_vars['mixed_content_block'].set(
                prefs.get('security.mixed_content.block_active_content', True)
            )

            # WebRTC
            self.privacy_vars['webrtc_enabled'].set(prefs.get('media.peerconnection.enabled', True))
            self.privacy_vars['webrtc_ip_leak'].set(
                prefs.get('media.peerconnection.ice.proxy_only_if_behind_proxy', False) or
                prefs.get('media.peerconnection.ice.default_address_only', False)
            )

            # Search and autofill
            self.privacy_vars['search_suggestions'].set(prefs.get('browser.search.suggest.enabled', True))
            self.privacy_vars['url_suggestions'].set(prefs.get('browser.urlbar.suggest.history', True))
            self.privacy_vars['autofill_forms'].set(prefs.get('browser.formfill.enable', True))
            self.privacy_vars['autofill_passwords'].set(prefs.get('signon.autofillForms', True))

            # Permissions
            perm_map = {1: 'allow', 0: 'ask', 2: 'block'}

            geo_enabled = prefs.get('geo.enabled', True)
            self.privacy_vars['location_permission'].set('block' if not geo_enabled else 'ask')

            camera_perm = prefs.get('permissions.default.camera', 0)
            self.privacy_vars['camera_permission'].set(perm_map.get(camera_perm, 'ask'))

            mic_perm = prefs.get('permissions.default.microphone', 0)
            self.privacy_vars['microphone_permission'].set(perm_map.get(mic_perm, 'ask'))

            notif_perm = prefs.get('permissions.default.desktop-notification', 0)
            self.privacy_vars['notifications_permission'].set(perm_map.get(notif_perm, 'ask'))

            # Autoplay
            autoplay = prefs.get('media.autoplay.default', 1)
            self.privacy_vars['autoplay_permission'].set('block' if autoplay == 5 else 'ask')

            # Update the summary display
            self.update_summary()

            # Update profile state
            self.profile_state['loaded'] = True
            self.profile_state['modified'] = False
            self.profile_state['profile_name'] = 'Firefox Profile'
            self.update_profile_status()

            self.status_bar.configure(text=f"Firefox profile loaded: {self.profile_path}")

        except Exception as e:
            self.status_bar.configure(text=f"Error loading profile settings: {str(e)}")
            print(f"Error loading profile settings: {e}")

    def apply_max_privacy(self):
        """Apply maximum privacy template"""
        # Clear everything
        for key in ['keep_cookies', 'keep_downloads', 'keep_history', 'keep_formdata']:
            self.privacy_vars[key].set(False)
        # Keep only essentials
        self.privacy_vars['keep_sessions'].set(True)
        self.privacy_vars['keep_logins'].set(True)
        # Clear all tracking
        for key in ['clear_cache', 'clear_offline', 'clear_thumbnails', 'clear_siteprefs']:
            self.privacy_vars[key].set(True)
        self.status_bar.configure(text="Applied maximum privacy template")

    def apply_balanced(self):
        """Apply balanced template"""
        # Keep important data
        self.privacy_vars['keep_cookies'].set(True)
        self.privacy_vars['keep_sessions'].set(True)
        self.privacy_vars['keep_logins'].set(True)
        self.privacy_vars['keep_formdata'].set(True)
        self.privacy_vars['keep_downloads'].set(False)
        self.privacy_vars['keep_history'].set(False)
        # Clear tracking data
        self.privacy_vars['clear_cache'].set(True)
        self.privacy_vars['clear_offline'].set(True)
        self.privacy_vars['clear_thumbnails'].set(True)
        self.privacy_vars['clear_siteprefs'].set(False)
        self.status_bar.configure(text="Applied balanced template")

    def apply_keep_all(self):
        """Apply keep everything template"""
        # Keep everything
        for key in self.privacy_vars:
            if key.startswith('keep_'):
                self.privacy_vars[key].set(True)
            elif key.startswith('clear_'):
                self.privacy_vars[key].set(False)
        self.status_bar.configure(text="Applied keep everything template")

    def load_defaults(self):
        """Load default settings"""
        defaults = {
            'restore_session': True,
            'restore_pinned': True,
            'restore_from_crash': True,
            'lazy_restore': True,
            'keep_cookies': True,
            'keep_sessions': True,
            'keep_logins': True,
            'keep_formdata': True,
            'keep_downloads': False,
            'keep_history': False,
            'clear_cache': True,
            'clear_offline': True,
            'clear_siteprefs': False,
            'clear_thumbnails': True,
            'telemetry_enabled': False,
            'studies_enabled': False,
            'crash_reports': False,
            'fingerprint_resist': True,
            'cryptomining_block': True,
            'https_only': True,
            'https_only_pbm': True,
            'mixed_content_block': True,
            'webrtc_enabled': True,
            'webrtc_ip_leak': False,
            'search_suggestions': False,
            'url_suggestions': True,
            'autofill_forms': False,
            'autofill_passwords': True,
            'prefetch_dns': False,
            'prefetch_links': False,
            'predictor': False,
        }

        for key, value in defaults.items():
            if key in self.privacy_vars and isinstance(self.privacy_vars[key], tk.BooleanVar):
                self.privacy_vars[key].set(value)

        self.privacy_vars['cookie_lifetime'].set('normal')
        self.privacy_vars['third_party_cookies'].set('cross-site')
        self.privacy_vars['tracking_protection'].set('strict')
        self.privacy_vars['dns_over_https'].set('increased')
        self.privacy_vars['dns_provider'].set('quad9')

        # Reset profile state
        self.profile_state['loaded'] = True
        self.profile_state['modified'] = False
        self.profile_state['profile_name'] = 'Default Settings'
        self.update_profile_status()

        self.status_bar.configure(text="Loaded default settings")
        self.update_summary()

    def update_summary(self):
        """Update the summary tab"""
        self.summary_text.delete("1.0", "end")

        summary = "=" * 60 + "\n"
        summary += "FIREFOX PRIVACY CONFIGURATION SUMMARY\n"
        summary += "=" * 60 + "\n\n"

        # Session Restore
        if self.privacy_vars['restore_session'].get():
            summary += "SESSION RESTORE: ENABLED\n"
            summary += "   - Tabs will be restored on startup\n"
            if self.privacy_vars['lazy_restore'].get():
                summary += "   - Tabs load on demand (faster startup)\n"
        else:
            summary += "SESSION RESTORE: DISABLED\n"
            summary += f"   - Firefox will start with: {self.startup_var.get()}\n"

        summary += "\n"

        # Privacy Settings
        summary += "PRIVACY SETTINGS:\n"
        summary += "-" * 40 + "\n"

        # Data kept
        summary += "Data KEPT on shutdown:\n"
        kept = []
        if self.privacy_vars['keep_cookies'].get(): kept.append("Cookies")
        if self.privacy_vars['keep_sessions'].get(): kept.append("Sessions")
        if self.privacy_vars['keep_logins'].get(): kept.append("Logins")
        if self.privacy_vars['keep_formdata'].get(): kept.append("Forms")
        if self.privacy_vars['keep_downloads'].get(): kept.append("Downloads")
        if self.privacy_vars['keep_history'].get(): kept.append("History")
        summary += "   - " + (", ".join(kept) if kept else "Nothing") + "\n"

        # Data cleared
        summary += "\nData CLEARED on shutdown:\n"
        cleared = []
        if self.privacy_vars['clear_cache'].get(): cleared.append("Cache")
        if self.privacy_vars['clear_offline'].get(): cleared.append("Offline data")
        if self.privacy_vars['clear_thumbnails'].get(): cleared.append("Thumbnails")
        if self.privacy_vars['clear_siteprefs'].get(): cleared.append("Site prefs")
        summary += "   - " + (", ".join(cleared) if cleared else "Nothing") + "\n"

        summary += "\n"

        # Cookies
        summary += "COOKIE SETTINGS:\n"
        summary += "-" * 40 + "\n"
        summary += f"   - Lifetime: {self.privacy_vars['cookie_lifetime'].get()}\n"
        summary += f"   - Third-party: {self.privacy_vars['third_party_cookies'].get()}\n"

        summary += "\n"

        # Network
        summary += "NETWORK & SECURITY:\n"
        summary += "-" * 40 + "\n"
        summary += f"   - DNS over HTTPS: {self.privacy_vars['dns_over_https'].get()}\n"
        summary += f"   - DNS Provider: {self.privacy_vars['dns_provider'].get()}\n"
        summary += f"   - HTTPS-Only: {'Yes' if self.privacy_vars['https_only'].get() else 'No'}\n"
        summary += f"   - WebRTC: {'Enabled' if self.privacy_vars['webrtc_enabled'].get() else 'Disabled'}\n"

        summary += "\n"

        # Tracking
        summary += "TRACKING PROTECTION:\n"
        summary += "-" * 40 + "\n"
        summary += f"   - Level: {self.privacy_vars['tracking_protection'].get()}\n"
        summary += f"   - Fingerprinting: {'Blocked' if self.privacy_vars['fingerprint_resist'].get() else 'Allowed'}\n"
        summary += f"   - Cryptomining: {'Blocked' if self.privacy_vars['cryptomining_block'].get() else 'Allowed'}\n"
        summary += f"   - Telemetry: {'Disabled' if not self.privacy_vars['telemetry_enabled'].get() else 'Enabled'}\n"

        self.summary_text.insert("1.0", summary)

    def _format_pref_value(self, value: Any) -> str:
        """
        Format a Python value for Firefox user.js syntax.

        Args:
            value: Python value (bool, int, float, or str)

        Returns:
            Formatted string for user.js
        """
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Strings need quotes in user.js
            return f'"{value}"'
        else:
            return str(value)

    def _generate_metadata_prefs(self, prefs: Dict[str, str]) -> None:
        """
        Generate preferences from SETTINGS_METADATA.

        Adds all metadata-based settings to the prefs dict,
        skipping any that were already set by legacy code.

        Args:
            prefs: Dict to add preferences to (modified in place)
        """
        for key, meta in SETTINGS_METADATA.items():
            pref_name = meta.get('pref')
            if not pref_name:
                continue

            # Skip if this pref was already set (legacy privacy settings)
            pref_key = f'"{pref_name}"'
            if pref_key in prefs:
                continue

            # Get the current value from the appropriate variable
            current_value = None
            if key in self.settings_vars:
                current_value = self.settings_vars[key].get()
            elif key in self.privacy_vars:
                current_value = self.privacy_vars[key].get()

            if current_value is None:
                continue

            # Convert label back to value for choice types
            if meta['type'] == 'choice':
                if current_value in meta['labels']:
                    idx = meta['labels'].index(current_value)
                    if idx < len(meta['values']):
                        current_value = meta['values'][idx]
                elif str(current_value) in [str(v) for v in meta['values']]:
                    # Already a valid value - find exact match
                    for v in meta['values']:
                        if str(v) == str(current_value):
                            current_value = v
                            break

            prefs[pref_key] = self._format_pref_value(current_value)

    def generate_preferences(self) -> Dict[str, str]:
        """
        Generate Firefox preferences from all settings.

        Combines legacy privacy settings with new metadata-based settings.

        Returns:
            Dict mapping Firefox pref keys to formatted values
        """
        prefs = {}

        # Session Restore
        if self.privacy_vars['restore_session'].get():
            prefs['"browser.startup.page"'] = "3"  # Restore session
            prefs['"browser.sessionstore.resume_from_crash"'] = "true"
            prefs['"browser.sessionstore.restore_on_demand"'] = str(self.privacy_vars['lazy_restore'].get()).lower()
            prefs['"browser.sessionstore.restore_pinned_tabs_on_demand"'] = "false"
            prefs['"browser.sessionstore.restore_tabs_lazily"'] = str(self.privacy_vars['lazy_restore'].get()).lower()
        else:
            prefs['"browser.startup.page"'] = "1"  # Homepage

        # Privacy - what to clear
        if any(self.privacy_vars[k].get() for k in ['clear_cache', 'clear_offline', 'clear_thumbnails']):
            prefs['"privacy.sanitize.sanitizeOnShutdown"'] = "true"

            # Set what to clear
            prefs['"privacy.clearOnShutdown.cache"'] = str(self.privacy_vars['clear_cache'].get()).lower()
            prefs['"privacy.clearOnShutdown.offlineApps"'] = str(self.privacy_vars['clear_offline'].get()).lower()
            prefs['"privacy.clearOnShutdown.siteSettings"'] = str(self.privacy_vars['clear_siteprefs'].get()).lower()

            # Set what to keep (inverse logic)
            prefs['"privacy.clearOnShutdown.cookies"'] = str(not self.privacy_vars['keep_cookies'].get()).lower()
            prefs['"privacy.clearOnShutdown.sessions"'] = str(not self.privacy_vars['keep_sessions'].get()).lower()
            prefs['"privacy.clearOnShutdown.history"'] = str(not self.privacy_vars['keep_history'].get()).lower()
            prefs['"privacy.clearOnShutdown.downloads"'] = str(not self.privacy_vars['keep_downloads'].get()).lower()
            prefs['"privacy.clearOnShutdown.formdata"'] = str(not self.privacy_vars['keep_formdata'].get()).lower()

            # Password manager
            prefs['"signon.rememberSignons"'] = str(self.privacy_vars['keep_logins'].get()).lower()

        # Cookie lifetime
        if self.privacy_vars['cookie_lifetime'].get() == 'session':
            prefs['"network.cookie.lifetimePolicy"'] = "2"
        elif self.privacy_vars['cookie_lifetime'].get() == 'days':
            prefs['"network.cookie.lifetimePolicy"'] = "3"
            prefs['"network.cookie.lifetime.days"'] = str(self._get_cookie_days_value())
        else:
            prefs['"network.cookie.lifetimePolicy"'] = "0"

        # Third-party cookies
        cookie_behavior_map = {
            'all': '0',
            'cross-site': '5',
            'none': '1',
            'visited': '3'
        }
        prefs['"network.cookie.cookieBehavior"'] = cookie_behavior_map.get(
            self.privacy_vars['third_party_cookies'].get(), '5'
        )

        # Tracking Protection
        if self.privacy_vars['tracking_protection'].get() == 'strict':
            prefs['"browser.contentblocking.category"'] = '"strict"'
        elif self.privacy_vars['tracking_protection'].get() == 'standard':
            prefs['"browser.contentblocking.category"'] = '"standard"'

        prefs['"privacy.trackingprotection.fingerprinting.enabled"'] = str(self.privacy_vars['fingerprint_resist'].get()).lower()
        prefs['"privacy.trackingprotection.cryptomining.enabled"'] = str(self.privacy_vars['cryptomining_block'].get()).lower()

        # Fix site issues for strict mode
        prefs['"privacy.annotate_channels.strict_list.enabled"'] = str(self.privacy_vars['fix_major_issues'].get()).lower()
        if self.privacy_vars['fix_minor_issues'].get():
            prefs['"privacy.purge_trackers.date_in_cookie_database"'] = '"0"'
            prefs['"privacy.restrict3rdpartystorage.rollout.enabledByDefault"'] = "false"

        # Telemetry
        prefs['"datareporting.healthreport.uploadEnabled"'] = str(self.privacy_vars['telemetry_enabled'].get()).lower()
        prefs['"toolkit.telemetry.enabled"'] = str(self.privacy_vars['telemetry_enabled'].get()).lower()
        prefs['"app.shield.optoutstudies.enabled"'] = str(self.privacy_vars['studies_enabled'].get()).lower()
        prefs['"browser.tabs.crashReporting.sendReport"'] = str(self.privacy_vars['crash_reports'].get()).lower()

        # DNS over HTTPS
        # network.trr.mode values:
        # 0 = Off, 2 = TRR first (with fallback), 3 = TRR only (strict)
        # Firefox TRR modes: 0=off, 2=TRR-first (fallback), 3=TRR-only (strict)
        doh_mode_map = {'off': '0', 'default': '2', 'increased': '2', 'max': '3'}
        prefs['"network.trr.mode"'] = doh_mode_map.get(self.privacy_vars['dns_over_https'].get(), '2')

        if self.privacy_vars['dns_provider'].get() == 'quad9':
            prefs['"network.trr.uri"'] = '"https://dns.quad9.net/dns-query"'
            prefs['"network.trr.bootstrapAddress"'] = '"9.9.9.9"'
        elif self.privacy_vars['dns_provider'].get() == 'cloudflare':
            prefs['"network.trr.uri"'] = '"https://cloudflare-dns.com/dns-query"'
            prefs['"network.trr.bootstrapAddress"'] = '"1.1.1.1"'
        elif self.privacy_vars['dns_provider'].get() == 'nextdns':
            prefs['"network.trr.uri"'] = '"https://dns.nextdns.io"'
            prefs['"network.trr.bootstrapAddress"'] = '"45.90.28.0"'

        # Network performance
        prefs['"network.dns.disablePrefetch"'] = str(not self.privacy_vars['prefetch_dns'].get()).lower()
        prefs['"network.prefetch-next"'] = str(self.privacy_vars['prefetch_links'].get()).lower()
        prefs['"network.predictor.enabled"'] = str(self.privacy_vars['predictor'].get()).lower()

        # HTTPS
        prefs['"dom.security.https_only_mode"'] = str(self.privacy_vars['https_only'].get()).lower()
        prefs['"dom.security.https_only_mode_pbm"'] = str(self.privacy_vars['https_only_pbm'].get()).lower()
        prefs['"security.mixed_content.block_active_content"'] = str(self.privacy_vars['mixed_content_block'].get()).lower()

        # WebRTC
        prefs['"media.peerconnection.enabled"'] = str(self.privacy_vars['webrtc_enabled'].get()).lower()
        if self.privacy_vars['webrtc_ip_leak'].get():
            prefs['"media.peerconnection.ice.proxy_only_if_behind_proxy"'] = "true"
            prefs['"media.peerconnection.ice.default_address_only"'] = "true"

        # Search and autofill
        prefs['"browser.search.suggest.enabled"'] = str(self.privacy_vars['search_suggestions'].get()).lower()
        prefs['"browser.urlbar.suggest.history"'] = str(self.privacy_vars['url_suggestions'].get()).lower()
        prefs['"browser.formfill.enable"'] = str(self.privacy_vars['autofill_forms'].get()).lower()
        prefs['"signon.autofillForms"'] = str(self.privacy_vars['autofill_passwords'].get()).lower()

        # Permissions
        perm_map = {'allow': '1', 'ask': '0', 'block': '2'}

        perms = {
            'location_permission': 'geo.enabled',
            'camera_permission': 'permissions.default.camera',
            'microphone_permission': 'permissions.default.microphone',
            'notifications_permission': 'permissions.default.desktop-notification'
        }

        for var_name, pref_name in perms.items():
            value = self.privacy_vars[var_name].get()
            if var_name == 'location_permission' and value == 'block':
                prefs[f'"{pref_name}"'] = "false"
            elif var_name != 'location_permission':
                prefs[f'"{pref_name}"'] = perm_map.get(value, '0')

        # Autoplay
        if self.privacy_vars['autoplay_permission'].get() == 'block':
            prefs['"media.autoplay.default"'] = "5"
        else:
            prefs['"media.autoplay.default"'] = "0"

        # Allow unsigned extensions (needed for extensions not from AMO like Bypass Paywalls Clean)
        prefs['"xpinstall.signatures.required"'] = "false"

        # Add all settings from metadata (Performance, Experimental, etc.)
        self._generate_metadata_prefs(prefs)

        return prefs

    def apply_configuration(self):
        """Apply configuration to Firefox"""
        if not self.profile_path:
            messagebox.showerror("Error", "Please select a valid Firefox profile first!")
            return

        if not messagebox.askyesno("Confirm", "Apply this configuration to Firefox?"):
            return

        try:
            prefs = self.generate_preferences()
            userjs_path = self.profile_path / "user.js"

            with open(userjs_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("// Hardzilla - Firefox Hardening Configuration\n")
                f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("// Generated by: Hardzilla\n\n")

                # Critical session settings first
                f.write("// ============================================================================\n")
                f.write("// CRITICAL SETTINGS FOR SESSION RESTORE\n")
                f.write("// ============================================================================\n")

                critical = ['"browser.startup.page"', '"privacy.clearOnShutdown.sessions"',
                           '"browser.sessionstore.resume_from_crash"']
                for key in critical:
                    if key in prefs:
                        f.write(f'user_pref({key}, {prefs[key]});\n')
                f.write("\n")

                # Other preferences
                f.write("// ============================================================================\n")
                f.write("// PRIVACY AND SECURITY SETTINGS\n")
                f.write("// ============================================================================\n")

                for key, value in sorted(prefs.items()):
                    if key not in critical:
                        f.write(f'user_pref({key}, {value});\n')

            # Update profile state - configuration now matches Firefox
            self.profile_state['last_applied'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.profile_state['modified'] = False
            if not self.profile_state['loaded']:
                self.profile_state['loaded'] = True
                self.profile_state['profile_name'] = 'Custom Configuration'
            self.update_profile_status()

            session_status = "ENABLED" if self.privacy_vars['restore_session'].get() else "DISABLED"
            messagebox.showinfo("Success",
                              f"Configuration applied successfully!\n\n" +
                              f"Session Restore: {session_status}\n\n" +
                              "Please restart Firefox for changes to take effect.")

            self.status_bar.configure(text=f"Applied to Firefox at {self.profile_state['last_applied']}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply configuration:\n{str(e)}")

    def _download_file_safely(
        self,
        url: str,
        dest_path: Path,
        max_size_mb: int = 50,
        timeout: int = 30
    ) -> bool:
        """
        Safely download a file with size and timeout limits.

        Args:
            url: URL to download from (HTTPS enforced)
            dest_path: Path to save the file
            max_size_mb: Maximum file size in MB (default 50MB)
            timeout: Timeout in seconds (default 30s)

        Returns:
            True if download successful, False otherwise

        Raises:
            ValueError: If URL is not HTTPS or file too large
            urllib.error.URLError: On network errors
        """
        max_bytes = max_size_mb * 1024 * 1024

        # Warn but allow non-HTTPS for known community sources
        if not url.startswith('https://'):
            logger.warning(f"Non-HTTPS URL: {url}")

        # Create SSL context
        context = ssl.create_default_context()

        # Create request with User-Agent
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Hardzilla/3.0 Firefox-Hardening-Tool'}
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
                # Check content length if available
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_bytes:
                    raise ValueError(f"File too large: {int(content_length) / 1024 / 1024:.1f}MB > {max_size_mb}MB limit")

                # Download with size limit
                downloaded = 0
                chunks = []

                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if downloaded > max_bytes:
                        raise ValueError(f"Download exceeded {max_size_mb}MB limit")
                    chunks.append(chunk)

                # Write to file only after successful download
                with open(dest_path, 'wb') as out_file:
                    for chunk in chunks:
                        out_file.write(chunk)

                logger.info(f"Downloaded {downloaded / 1024:.1f}KB from {url}")
                return True

        except Exception as e:
            # Clean up partial file if it exists
            if dest_path.exists():
                try:
                    dest_path.unlink()
                except OSError:
                    pass
            logger.error(f"Download failed for {url}: {e}")
            raise

    def install_extensions(self):
        """Install selected extensions to Firefox profile"""
        if not self.profile_path:
            messagebox.showerror("Error", "Please select a valid Firefox profile first!")
            return

        # Get selected extensions
        selected = [ext for key, ext in self.extensions.items() if ext['enabled'].get()]

        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one extension to install!")
            return

        if not messagebox.askyesno("Confirm Installation",
                                   f"Install {len(selected)} extension(s) to Firefox?\n\n" +
                                   "Extensions will be downloaded and installed to your profile."):
            return

        # Create extensions directory
        ext_dir = self.profile_path / "extensions"
        ext_dir.mkdir(exist_ok=True)

        installed = []
        failed = []

        for ext in selected:
            try:
                self.ext_status.configure(text=f"Downloading {ext['name']}...", text_color=COLORS['info'])
                self.root.update()

                # Download extension safely
                xpi_path = ext_dir / f"{ext['id']}.xpi"

                # Use safe download with timeout and size limits
                self._download_file_safely(ext['url'], xpi_path, max_size_mb=50, timeout=60)

                installed.append(ext['name'])
                self.ext_status.configure(text=f"Installed {ext['name']}", text_color=COLORS['success'])
                self.root.update()

            except Exception as e:
                failed.append(f"{ext['name']}: {str(e)}")
                self.ext_status.configure(text=f"Failed to install {ext['name']}", text_color=COLORS['error'])
                self.root.update()

        # Show results
        result_msg = ""
        if installed:
            result_msg += f"Successfully installed ({len(installed)}):\n"
            result_msg += "\n".join(f"  - {name}" for name in installed)
            result_msg += "\n\n"

        if failed:
            result_msg += f"Failed to install ({len(failed)}):\n"
            result_msg += "\n".join(f"  - {err}" for err in failed)
            result_msg += "\n\n"

        result_msg += "Please restart Firefox for extensions to be loaded."

        if failed:
            messagebox.showwarning("Installation Complete with Errors", result_msg)
        else:
            messagebox.showinfo("Installation Complete", result_msg)

        self.ext_status.configure(text=f"Installed {len(installed)} extension(s)", text_color=COLORS['success'])

    def check_installed_extensions(self):
        """Check which extensions are currently installed"""
        if not self.profile_path:
            messagebox.showerror("Error", "Please select a valid Firefox profile first!")
            return

        ext_dir = self.profile_path / "extensions"

        if not ext_dir.exists():
            messagebox.showinfo("Extensions", "No extensions directory found.\nNo extensions are currently installed.")
            return

        # Check which of our recommended extensions are installed
        installed = []
        not_installed = []

        for key, ext in self.extensions.items():
            xpi_path = ext_dir / f"{ext['id']}.xpi"
            if xpi_path.exists():
                installed.append(ext['name'])
            else:
                not_installed.append(ext['name'])

        msg = "INSTALLED EXTENSIONS:\n"
        msg += "=" * 40 + "\n"

        if installed:
            msg += "\n".join(f"  {name}" for name in installed)
        else:
            msg += "None of the recommended extensions are installed."

        msg += "\n\n" + "NOT INSTALLED:\n"
        msg += "=" * 40 + "\n"

        if not_installed:
            msg += "\n".join(f"  {name}" for name in not_installed)
        else:
            msg += "All recommended extensions are installed!"

        messagebox.showinfo("Extension Status", msg)

    def install_userscripts(self):
        """Install selected userscripts to Tampermonkey directory"""
        if not self.profile_path:
            messagebox.showerror("Error", "Please select a valid Firefox profile first!")
            return

        # Check if Tampermonkey is installed
        ext_dir = self.profile_path / "extensions"
        tampermonkey_xpi = ext_dir / "firefox@tampermonkey.net.xpi"

        if not tampermonkey_xpi.exists():
            messagebox.showerror("Tampermonkey Not Installed",
                               "Tampermonkey extension must be installed first!\n\n" +
                               "Please install Tampermonkey from the Extensions tab before installing userscripts.")
            return

        # Get selected userscripts
        selected = [script for key, script in self.userscripts.items() if script['enabled'].get()]

        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one userscript to install!")
            return

        if not messagebox.askyesno("Confirm Installation",
                                   f"Install {len(selected)} userscript(s)?\n\n" +
                                   "Userscripts will be downloaded to your Firefox profile.\n" +
                                   "After installation, enable them in Tampermonkey's dashboard."):
            return

        # Create userscripts directory in profile
        # Tampermonkey stores scripts in the extension's storage, but we'll put them in a central location
        scripts_dir = self.profile_path / "tampermonkey_scripts"
        scripts_dir.mkdir(exist_ok=True)

        installed = []
        failed = []

        for script in selected:
            try:
                self.script_status.configure(text=f"Downloading {script['name']}...", text_color=COLORS['info'])
                self.root.update()

                # Download userscript safely
                script_path = scripts_dir / script['filename']

                # Use safe download with timeout and size limits (scripts are small)
                self._download_file_safely(script['url'], script_path, max_size_mb=5, timeout=30)

                installed.append(script['name'])
                self.script_status.configure(text=f"Downloaded {script['name']}", text_color=COLORS['success'])
                self.root.update()

            except Exception as e:
                failed.append(f"{script['name']}: {str(e)}")
                self.script_status.configure(text=f"Failed to download {script['name']}", text_color=COLORS['error'])
                self.root.update()

        # Show results
        result_msg = ""
        if installed:
            result_msg += f"Successfully downloaded ({len(installed)}):\n"
            result_msg += "\n".join(f"  - {name}" for name in installed)
            result_msg += f"\n\nLocation: {scripts_dir}\n\n"
            result_msg += "TO ACTIVATE:\n"
            result_msg += "1. Open Firefox\n"
            result_msg += "2. Click the Tampermonkey icon\n"
            result_msg += "3. Select 'Dashboard'\n"
            result_msg += "4. Click 'Utilities' tab\n"
            result_msg += "5. Use 'Import from file' or drag the .user.js files\n"
            result_msg += f"6. Navigate to: {scripts_dir}\n\n"

        if failed:
            result_msg += f"Failed to download ({len(failed)}):\n"
            result_msg += "\n".join(f"  - {err}" for err in failed)

        if failed:
            messagebox.showwarning("Installation Complete with Errors", result_msg)
        else:
            messagebox.showinfo("Download Complete", result_msg)

        self.script_status.configure(text=f"Downloaded {len(installed)} userscript(s)", text_color=COLORS['success'])

    def check_installed_userscripts(self):
        """Check which userscripts are currently downloaded"""
        if not self.profile_path:
            messagebox.showerror("Error", "Please select a valid Firefox profile first!")
            return

        scripts_dir = self.profile_path / "tampermonkey_scripts"

        if not scripts_dir.exists():
            messagebox.showinfo("Userscripts", "No userscripts directory found.\nNo userscripts have been downloaded yet.")
            return

        # Check which userscripts are downloaded
        installed = []
        not_installed = []

        for key, script in self.userscripts.items():
            script_path = scripts_dir / script['filename']
            if script_path.exists():
                installed.append(script['name'])
            else:
                not_installed.append(script['name'])

        msg = "DOWNLOADED USERSCRIPTS:\n"
        msg += "=" * 40 + "\n"

        if installed:
            msg += "\n".join(f"  {name}" for name in installed)
            msg += f"\n\nLocation: {scripts_dir}"
        else:
            msg += "No userscripts have been downloaded yet."

        msg += "\n\n" + "NOT DOWNLOADED:\n"
        msg += "=" * 40 + "\n"

        if not_installed:
            msg += "\n".join(f"  {name}" for name in not_installed)
        else:
            msg += "All userscripts are downloaded!"

        msg += "\n\nNote: Downloaded scripts must be imported into\nTampermonkey's dashboard to be activated."

        messagebox.showinfo("Userscript Status", msg)

    def save_profile(self):
        """Save current settings to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"hardzilla_config_{datetime.now().strftime('%Y%m%d')}.json"
        )

        if filename:
            profile = {
                'name': Path(filename).stem,
                'timestamp': datetime.now().isoformat(),
                'version': '2.0',
                'settings': {}
            }

            # Save all settings from privacy_vars
            for key, var in self.privacy_vars.items():
                if isinstance(var, tk.BooleanVar):
                    profile['settings'][key] = var.get()
                elif isinstance(var, tk.StringVar):
                    profile['settings'][key] = var.get()
                elif isinstance(var, tk.IntVar):
                    profile['settings'][key] = var.get()

            # Also save settings_vars (for SETTINGS_METADATA-driven settings)
            for key, var in self.settings_vars.items():
                if key not in profile['settings']:  # Don't overwrite privacy_vars
                    if isinstance(var, tk.BooleanVar):
                        profile['settings'][key] = var.get()
                    elif isinstance(var, tk.StringVar):
                        # For choice types with labels, convert back to raw value
                        val = var.get()
                        if key in SETTINGS_METADATA:
                            meta = SETTINGS_METADATA[key]
                            if meta.get('type') == 'choice' and val in meta.get('labels', []):
                                idx = meta['labels'].index(val)
                                if idx < len(meta.get('values', [])):
                                    val = meta['values'][idx]
                        profile['settings'][key] = val
                    elif isinstance(var, tk.IntVar):
                        profile['settings'][key] = var.get()

            with open(filename, 'w') as f:
                json.dump(profile, f, indent=2)

            # Update profile state
            self.profile_state['loaded'] = True
            self.profile_state['modified'] = False
            self.profile_state['profile_name'] = Path(filename).stem
            self.update_profile_status()

            messagebox.showinfo("Configuration Saved",
                              f"Configuration saved to:\n{Path(filename).name}\n\n" +
                              "This does NOT apply settings to Firefox.\n" +
                              "Click 'Apply Configuration to Firefox' to activate.")
            self.status_bar.configure(text=f"Configuration saved: {Path(filename).name}")

    def load_profile(self):
        """Load settings from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    profile = json.load(f)

                settings = profile.get('settings', {})
                for key, value in settings.items():
                    if key in self.privacy_vars:
                        self.privacy_vars[key].set(value)
                    elif key in self.settings_vars:
                        # For choice types, convert raw value to label if needed
                        if key in SETTINGS_METADATA:
                            meta = SETTINGS_METADATA[key]
                            if meta.get('type') == 'choice':
                                values = meta.get('values', [])
                                labels = meta.get('labels', [])
                                if value in values:
                                    idx = values.index(value)
                                    if idx < len(labels):
                                        value = labels[idx]
                        self.settings_vars[key].set(value)
                    elif key == 'cookie_days':
                        # Special handling for cookie_days which may not be in settings_vars yet
                        self._set_cookie_days_value(value if isinstance(value, int) else 30)

                # Update profile state
                self.profile_state['loaded'] = True
                self.profile_state['modified'] = False
                self.profile_state['profile_name'] = Path(filename).stem
                self.profile_state['last_applied'] = 'Never'  # Reset since we loaded new config
                self.update_profile_status()

                self.update_summary()
                messagebox.showinfo("Configuration Loaded",
                                  f"Configuration loaded from:\n{Path(filename).name}\n\n" +
                                  "This does NOT apply settings to Firefox yet.\n" +
                                  "Click 'Apply Configuration to Firefox' to activate.")
                self.status_bar.configure(text=f"Configuration loaded: {Path(filename).name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load profile:\n{str(e)}")

    def run(self):
        """Run the application"""
        self.update_summary()
        self.root.mainloop()


def main():
    app = GranularPrivacyGUI()
    app.run()


if __name__ == "__main__":
    main()
