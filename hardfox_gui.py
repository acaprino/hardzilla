#!/usr/bin/env python3
"""
Hardfox v4.0 - GUI Application
Main entry point for the graphical user interface.

3-tab layout: Settings | Extensions | Utilities
Firefox profile path is global in the header.
"""

import sys
import logging
import argparse
from pathlib import Path
import json
import customtkinter as ctk
from tkinter import filedialog

# Configure logging (--debug flag enables DEBUG level)
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument('--debug', '-v', action='store_true', help='Enable debug logging')
_args, _ = _parser.parse_known_args()

logging.basicConfig(
    level=logging.DEBUG if _args.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from hardfox.composition_root import CompositionRoot
from hardfox.presentation.view_models import (
    SettingsViewModel,
    ApplyViewModel,
    UtilitiesViewModel
)
from hardfox.presentation.views import (
    SettingsView,
    ExtensionsView,
    UtilitiesView
)
from hardfox.presentation.controllers import (
    SettingsController,
    ApplyController,
    UtilitiesController
)
from hardfox.presentation.theme import Theme
from hardfox.presentation.utils import KeyboardHandler


class HardfoxGUI(ctk.CTk):
    """
    Main GUI application for Hardfox v4.0.

    Implements a 3-tab interface with a global Firefox path selector:
    1. Settings - Presets, customize, and apply settings
    2. Extensions - Select and install privacy extensions
    3. Utilities - Portable Firefox tools
    """

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Hardfox v4.0 - Firefox Privacy & Security Tool")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        logger.info("Initializing Hardfox v4.0 GUI...")

        # Initialize infrastructure
        self._init_infrastructure()

        # Initialize use cases
        self._init_use_cases()

        # Initialize ViewModels
        self._init_view_models()

        # Initialize Controllers
        self._init_controllers()

        # Build UI
        self._build_ui()

        # Initialize keyboard shortcuts
        self._init_keyboard_shortcuts()

        logger.info("Hardfox v4.0 GUI initialized successfully")

    def _init_infrastructure(self):
        """Initialize infrastructure layer via CompositionRoot."""
        self.composition_root = CompositionRoot(app_dir=Path(__file__).parent)

        self.app_dir = self.composition_root.app_dir
        self.profiles_dir = self.composition_root.profiles_dir
        self.parser = self.composition_root.parser
        self.settings_repo = self.composition_root.settings_repo
        self.firefox_repo = self.composition_root.firefox_repo
        self.profile_repo = self.composition_root.profile_repo

    def _init_use_cases(self):
        """Initialize application use cases via CompositionRoot."""
        self.setting_mapper = self.composition_root.setting_mapper
        self.pref_mapper = self.composition_root.pref_mapper
        self.intent_analyzer = self.composition_root.intent_analyzer
        self.generate_recommendation = self.composition_root.generate_recommendation
        self.apply_settings = self.composition_root.apply_settings
        self.save_profile = self.composition_root.save_profile
        self.load_profile = self.composition_root.load_profile
        self.import_from_firefox = self.composition_root.import_from_firefox
        self.load_preset = self.composition_root.load_preset
        self.install_extensions = self.composition_root.install_extensions
        self.uninstall_extensions = self.composition_root.uninstall_extensions
        self.convert_to_portable = self.composition_root.convert_to_portable
        self.update_portable_firefox = self.composition_root.update_portable_firefox
        self.create_portable_from_download = self.composition_root.create_portable_from_download

    def _init_view_models(self):
        """Initialize view models."""
        self.settings_vm = SettingsViewModel(settings_repo=self.settings_repo)
        self.apply_vm = ApplyViewModel()  # Extensions-only
        self.utilities_vm = UtilitiesViewModel()

    def _init_controllers(self):
        """Initialize controllers."""
        self.settings_controller = SettingsController(
            view_model=self.settings_vm,
            import_from_firefox=self.import_from_firefox,
            apply_settings=self.apply_settings,
            save_profile=self.save_profile,
            on_profile_imported=self._on_profile_imported,
            ui_callback=self._schedule_ui_update
        )

        self.apply_controller = ApplyController(
            view_model=self.apply_vm,
            apply_settings=self.apply_settings,
            save_profile=self.save_profile,
            install_extensions=self.install_extensions,
            uninstall_extensions=self.uninstall_extensions,
            ui_callback=self._schedule_ui_update
        )

        self.utilities_controller = UtilitiesController(
            view_model=self.utilities_vm,
            convert_to_portable=self.convert_to_portable,
            portable_repo=self.composition_root.portable_repo,
            update_portable_firefox=self.update_portable_firefox,
            create_portable_from_download=self.create_portable_from_download,
            ui_callback=self._schedule_ui_update
        )

    def _build_ui(self):
        """Build the user interface."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        # Header (with global Firefox path)
        header = self._build_header(main_frame)
        header.pack(fill="x", padx=20, pady=(20, 10))

        # Tabview (3 independent tabs)
        self.tabview = ctk.CTkTabview(main_frame, height=700)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create tabs
        self.tabview.add("Settings")
        self.tabview.add("Extensions")
        self.tabview.add("Utilities")

        # Create content in each tab
        self._create_tab_content()

        # Set default tab
        self.tabview.set("Settings")

    def _build_header(self, parent):
        """Build application header with global Firefox path selector."""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color="#2D2D2D",
            corner_radius=8,
        )
        header_frame.grid_columnconfigure(2, weight=1)

        # Icon/Logo
        icon_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=36)
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), pady=10)

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Hardfox",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=1, sticky="w", pady=(15, 0))

        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Firefox Privacy & Security Configurator",
            font=ctk.CTkFont(size=13),
            text_color="#9E9E9E"
        )
        subtitle.grid(row=1, column=1, sticky="w", pady=(0, 15))

        # Global Firefox Profile selector (right side of header)
        path_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        path_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=20, pady=10)
        path_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            path_frame,
            text="Firefox Profile:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CCCCCC"
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.global_path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Select Firefox profile directory...",
            font=ctk.CTkFont(size=12),
            height=32,
            width=350
        )
        self.global_path_entry.grid(row=0, column=1, padx=(0, 8))

        ctk.CTkButton(
            path_frame,
            text="Browse",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            command=self._browse_global_firefox_path
        ).grid(row=0, column=2)

        # Import status label
        self.global_import_status = ctk.CTkLabel(
            path_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.get_color('info')
        )
        self.global_import_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 0))

        return header_frame

    def _create_tab_content(self):
        """Create content for each tab."""
        logger.debug("_create_tab_content: creating views for all 3 tabs")

        # Tab 1: Settings (unified)
        self.settings_view = SettingsView(
            parent=self.tabview.tab("Settings"),
            view_model=self.settings_vm,
            on_preset_selected=self._on_preset_selected,
            on_json_imported=self._on_json_imported,
            on_apply=self._on_apply,
            profiles_dir=self.profiles_dir
        )
        self.settings_view.pack(fill="both", expand=True)

        # Tab 2: Extensions
        self.extensions_view = ExtensionsView(
            parent=self.tabview.tab("Extensions"),
            view_model=self.apply_vm,
            on_install_extensions=self._on_install_extensions,
            on_uninstall_extensions=self._on_uninstall_extensions,
            settings_view_model=self.settings_vm
        )
        self.extensions_view.pack(fill="both", expand=True)

        # Tab 3: Utilities
        self.utilities_view = UtilitiesView(
            parent=self.tabview.tab("Utilities"),
            view_model=self.utilities_vm,
            on_convert=self._on_convert_to_portable,
            on_cancel_convert=self._on_cancel_portable_conversion,
            on_estimate_requested=self._on_estimate_portable_size,
            on_check_update=self._on_check_portable_update,
            on_update=self._on_update_portable_firefox,
            on_cancel_update=self._on_cancel_portable_update,
            on_create_portable=self._on_create_portable_from_download,
            on_cancel_create=self._on_cancel_create_portable
        )
        self.utilities_view.pack(fill="both", expand=True)

    def _init_keyboard_shortcuts(self):
        """Initialize keyboard shortcuts."""
        self.keyboard_handler = KeyboardHandler(self)

        # Ctrl+S for apply (when on Settings tab)
        def handle_ctrl_s():
            if self.tabview.get() == "Settings":
                self._on_apply()

        self.keyboard_handler.register_shortcut('<Control-s>', handle_ctrl_s)
        logger.info("Keyboard shortcuts initialized")

    def _schedule_ui_update(self, callback):
        """Schedule a UI update to run on the main thread."""
        self.after(0, callback)

    # =================================================================
    # Global Firefox path
    # =================================================================

    def _browse_global_firefox_path(self):
        """Open directory browser for Firefox profile."""
        path = filedialog.askdirectory(title="Select Firefox Profile Directory")
        if path:
            is_valid, error_msg = self._validate_firefox_path(path)
            if is_valid:
                self.global_path_entry.delete(0, "end")
                self.global_path_entry.insert(0, path)
                self._on_firefox_path_changed(path)
            else:
                self.global_import_status.configure(
                    text=f"  {error_msg}",
                    text_color=Theme.get_color('error')
                )

    def _validate_firefox_path(self, path: str) -> tuple:
        """Validate Firefox profile path."""
        firefox_path = Path(path)

        if not firefox_path.exists():
            return False, "Directory does not exist"

        if not firefox_path.is_dir():
            return False, "Path is not a directory"

        has_prefs = (firefox_path / "prefs.js").exists()
        has_times = (firefox_path / "times.json").exists()

        if not (has_prefs or has_times):
            return False, "Not a valid Firefox profile (missing prefs.js or times.json)"

        return True, ""

    def _on_firefox_path_changed(self, path: str):
        """Handle Firefox path selection - propagate to all VMs."""
        logger.debug("_on_firefox_path_changed: path=%s", path)

        # Show loading status
        self.global_import_status.configure(
            text="Loading current Firefox settings...",
            text_color=Theme.get_color('info')
        )

        # Update settings_vm
        self.settings_vm.firefox_path = path

        # Sync to apply_vm (Extensions tab)
        self.apply_vm.firefox_path = path

        # Sync to utilities_vm
        self.utilities_vm.profile_path = path
        self.utilities_vm.firefox_install_dir = ''  # Reset to trigger re-detection
        self.utilities_controller.detect_firefox_installation(path)

        # Import settings from Firefox
        try:
            self.settings_controller.handle_firefox_path_changed(path)
        except Exception as e:
            logger.error(f"Failed to import from Firefox: {e}")
            self._show_error("Failed to import settings", str(e))

    def _on_profile_imported(self, profile):
        """Handle profile imported from Firefox."""
        if profile is None:
            self.global_import_status.configure(
                text="  Failed to import settings from Firefox profile",
                text_color=Theme.get_color('error')
            )
            return

        logger.info(f"Profile imported: {profile.name} with {len(profile.settings)} settings")

        # Update settings VM with imported profile
        self.settings_vm.profile = profile

        # Show success in header
        self.global_import_status.configure(
            text=f"  Loaded {len(profile.settings)} settings from Firefox profile",
            text_color=Theme.get_color('primary')
        )

    # =================================================================
    # Settings tab handlers
    # =================================================================

    def _on_preset_selected(self, preset_key: str):
        """Handle preset selection."""
        try:
            profile = self.load_preset.execute(preset_key)
            logger.info(f"Loaded preset '{preset_key}': {len(profile.settings)} settings")
            self.settings_vm.profile = profile
        except Exception as e:
            logger.error(f"Failed to load preset: {e}")
            self._show_error("Failed to load preset", str(e))

    def _on_json_imported(self, json_path: str):
        """Handle JSON profile import."""
        try:
            profile = self.load_profile.execute(json_path)
            logger.info(f"Loaded JSON profile '{profile.name}': {len(profile.settings)} settings")

            self.settings_vm.profile = profile

            self.settings_view.show_json_import_success(profile.name, len(profile.settings))

            self._show_info(
                "Profile Imported",
                f"Successfully loaded '{profile.name}' with {len(profile.settings)} settings.\n\n"
                f"BASE: {profile.get_base_settings_count()} | "
                f"ADVANCED: {profile.get_advanced_settings_count()}\n\n"
                f"Review and modify settings below, then click 'Apply Settings'."
            )

        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
            self.settings_view.show_json_import_error("File not found")
            self._show_error("Import Failed", "Could not find the selected JSON file.")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            self.settings_view.show_json_import_error("Invalid JSON format")
            self._show_error("Import Failed", "The selected file is not valid JSON.")

        except Exception as e:
            logger.error(f"Failed to import JSON profile: {e}")
            self.settings_view.show_json_import_error(str(e))
            self._show_error("Import Failed", f"Failed to import profile:\n\n{str(e)}")

    def _on_apply(self):
        """Handle apply button."""
        try:
            self.settings_controller.handle_apply()
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            self._show_error("Failed to apply settings", str(e))

    # =================================================================
    # Extensions tab handlers
    # =================================================================

    def _on_install_extensions(self):
        """Handle install extensions button."""
        logger.debug("_on_install_extensions: delegating to apply_controller")
        try:
            self.apply_controller.handle_install_extensions()
        except Exception as e:
            logger.error(f"Failed to install extensions: {e}", exc_info=True)
            self._show_error("Failed to install extensions", str(e))

    def _on_uninstall_extensions(self):
        """Handle uninstall extensions button."""
        logger.debug("_on_uninstall_extensions: delegating to apply_controller")
        try:
            self.apply_controller.handle_uninstall_extensions()
        except Exception as e:
            logger.error(f"Failed to uninstall extensions: {e}", exc_info=True)
            self._show_error("Failed to uninstall extensions", str(e))

    # =================================================================
    # Utilities tab handlers
    # =================================================================

    def _on_convert_to_portable(self):
        logger.debug("_on_convert_to_portable: starting conversion")
        try:
            self.utilities_controller.handle_convert()
        except Exception as e:
            logger.error(f"Failed to start conversion: {e}", exc_info=True)
            self._show_error("Conversion Failed", str(e))

    def _on_cancel_portable_conversion(self):
        self.utilities_controller.cancel_conversion()

    def _on_estimate_portable_size(self):
        self.utilities_controller.estimate_size()

    def _on_check_portable_update(self):
        portable_path = self.utilities_vm.portable_path
        if portable_path:
            self.utilities_controller.check_for_update(portable_path)

    def _on_update_portable_firefox(self):
        try:
            self.utilities_controller.handle_update()
        except Exception as e:
            logger.error(f"Failed to start update: {e}", exc_info=True)
            self._show_error("Update Failed", str(e))

    def _on_cancel_portable_update(self):
        self.utilities_controller.cancel_update()

    def _on_create_portable_from_download(self):
        try:
            self.utilities_controller.handle_create_portable()
        except Exception as e:
            logger.error(f"Failed to start create portable: {e}", exc_info=True)
            self._show_error("Create Portable Failed", str(e))

    def _on_cancel_create_portable(self):
        self.utilities_controller.cancel_create_portable()

    # =================================================================
    # Dialogs
    # =================================================================

    def _show_error(self, title: str, message: str):
        """Show error dialog."""
        error_window = ctk.CTkToplevel(self)
        error_window.title(title)
        error_window.geometry("400x200")

        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350
        ).pack(padx=20, pady=20)

        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=10)

    def _show_info(self, title: str, message: str):
        """Show info dialog."""
        info_window = ctk.CTkToplevel(self)
        info_window.title(title)
        info_window.geometry("450x250")

        ctk.CTkLabel(
            info_window,
            text="",
            font=ctk.CTkFont(size=48),
            text_color="#0F7B0F"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            info_window,
            text=message,
            wraplength=400,
            font=ctk.CTkFont(size=13)
        ).pack(padx=20, pady=10)

        ctk.CTkButton(
            info_window,
            text="OK",
            command=info_window.destroy,
            fg_color="#0078D4",
            hover_color="#106EBE"
        ).pack(pady=10)


def _apply_mica_effect(window):
    """Apply Windows 11 Mica backdrop effect if available."""
    try:
        import pywinstyles
        import sys
        version = sys.getwindowsversion()
        if version.major == 10 and version.build >= 22000:
            pywinstyles.apply_style(window, "mica")
            pywinstyles.change_header_color(window, "#202020")
            pywinstyles.change_title_color(window, "#ffffff")
            logger.info("Applied Windows 11 Mica backdrop effect")
    except ImportError:
        logger.debug("pywinstyles not installed, skipping Mica effect")
    except Exception as e:
        logger.debug("Could not apply Mica effect: %s", e)


def main():
    """Main entry point for GUI application."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = HardfoxGUI()

    _apply_mica_effect(app)

    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application closed by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n[ERROR] {e}")
        sys.exit(1)
