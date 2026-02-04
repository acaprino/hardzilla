#!/usr/bin/env python3
"""
Hardzilla v4.0 - GUI Application
Main entry point for the graphical user interface
"""

import sys
import logging
from pathlib import Path
import json
import customtkinter as ctk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from hardzilla.composition_root import CompositionRoot
from hardzilla.presentation.view_models import (
    SetupViewModel,
    CustomizeViewModel,
    ApplyViewModel
)
from hardzilla.presentation.views import (
    SetupView,
    CustomizeView,
    ExtensionsView,
    ApplyView
)
from hardzilla.presentation.controllers import (
    SetupController,
    ApplyController
)
from hardzilla.presentation.utils import KeyboardHandler


class HardzillaGUI(ctk.CTk):
    """
    Main GUI application for Hardzilla v4.0.

    Implements a 4-tab interface:
    1. Setup & Presets - Choose profile and Firefox path
    2. Customize Settings - Review and modify settings
    3. Extensions - Select and install privacy extensions
    4. Apply to Firefox - Apply configuration to Firefox
    """

    def __init__(self):
        """Initialize the GUI application"""
        super().__init__()

        # Configure window
        self.title("Hardzilla v4.0 - Firefox Privacy & Security Tool")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        logger.info("Initializing Hardzilla v4.0 GUI...")

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

        logger.info("Hardzilla v4.0 GUI initialized successfully")

    def _init_infrastructure(self):
        """Initialize infrastructure layer via CompositionRoot"""
        self.composition_root = CompositionRoot(app_dir=Path(__file__).parent)

        # Expose dependencies for convenience
        self.app_dir = self.composition_root.app_dir
        self.profiles_dir = self.composition_root.profiles_dir
        self.parser = self.composition_root.parser
        self.settings_repo = self.composition_root.settings_repo
        self.firefox_repo = self.composition_root.firefox_repo
        self.profile_repo = self.composition_root.profile_repo

    def _init_use_cases(self):
        """Initialize application use cases via CompositionRoot"""
        # Expose use cases and services for convenience
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

    def _init_view_models(self):
        """Initialize view models"""
        self.setup_vm = SetupViewModel()
        self.customize_vm = CustomizeViewModel(settings_repo=self.settings_repo)
        self.apply_vm = ApplyViewModel()

    def _init_controllers(self):
        """Initialize controllers"""
        self.setup_controller = SetupController(
            view_model=self.setup_vm,
            generate_recommendation=self.generate_recommendation,
            import_from_firefox=self.import_from_firefox,
            on_next=self._on_setup_next,
            on_profile_imported=self._on_profile_imported,
            ui_callback=self._schedule_ui_update
        )

        self.apply_controller = ApplyController(
            view_model=self.apply_vm,
            apply_settings=self.apply_settings,
            save_profile=self.save_profile,
            install_extensions=self.install_extensions,
            ui_callback=self._schedule_ui_update
        )

    def _build_ui(self):
        """Build the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        # Header
        header = self._build_header(main_frame)
        header.pack(fill="x", padx=20, pady=20)

        # Tabview (replaces wizard navigation)
        self.tabview = ctk.CTkTabview(main_frame, height=700)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create tabs
        self.tabview.add("Setup & Presets")
        self.tabview.add("Customize Settings")
        self.tabview.add("Extensions")
        self.tabview.add("Apply to Firefox")

        # Create content in each tab
        self._create_tab_content()

        # Set default tab
        self.tabview.set("Setup & Presets")

    def _build_header(self, parent):
        """Build application header with enhanced styling"""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color="#1E293B",
            corner_radius=12,
            height=80
        )
        header_frame.grid_columnconfigure(1, weight=1)

        # Icon/Logo
        icon_label = ctk.CTkLabel(
            header_frame,
            text="🛡️",
            font=ctk.CTkFont(size=36)
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=20, pady=10)

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Hardzilla",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=1, sticky="w", pady=(15, 0))

        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Firefox Privacy & Security Configurator",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        subtitle.grid(row=1, column=1, sticky="w", pady=(0, 15))

        return header_frame

    def _create_tab_content(self):
        """Create content for each tab"""
        logger.debug("_create_tab_content: creating views for all 4 tabs")
        # Tab 1: Setup & Presets
        self.setup_view = SetupView(
            parent=self.tabview.tab("Setup & Presets"),
            view_model=self.setup_vm,
            on_generate_recommendation=self._on_generate_recommendation,
            on_next=self._on_setup_next,
            on_firefox_path_changed=self._on_firefox_path_changed,
            on_preset_selected=self._on_preset_selected,
            on_json_imported=self._on_json_imported,
            profiles_dir=self.profiles_dir
        )
        self.setup_view.pack(fill="both", expand=True)

        # Tab 2: Customize Settings
        self.customize_view = CustomizeView(
            parent=self.tabview.tab("Customize Settings"),
            view_model=self.customize_vm,
            on_next=self._on_customize_next,
            on_back=self._on_customize_back
        )
        self.customize_view.pack(fill="both", expand=True)

        logger.debug("_create_tab_content: creating ExtensionsView (Tab 3)")
        # Tab 3: Extensions
        self.extensions_view = ExtensionsView(
            parent=self.tabview.tab("Extensions"),
            view_model=self.apply_vm,
            on_install_extensions=self._on_install_extensions,
            on_next=self._on_extensions_next,
            on_back=self._on_extensions_back
        )
        self.extensions_view.pack(fill="both", expand=True)

        # Tab 4: Apply to Firefox
        self.apply_view = ApplyView(
            parent=self.tabview.tab("Apply to Firefox"),
            view_model=self.apply_vm,
            on_apply=self._on_apply,
            on_back=self._on_apply_back
        )
        self.apply_view.pack(fill="both", expand=True)

    def _init_keyboard_shortcuts(self):
        """Initialize keyboard shortcuts"""
        self.keyboard_handler = KeyboardHandler(self)

        # Register Ctrl+S for apply (when on apply tab)
        def handle_ctrl_s():
            if self.tabview.get() == "Apply to Firefox":
                self._on_apply()

        self.keyboard_handler.register_shortcut('<Control-s>', handle_ctrl_s)

        logger.info("Keyboard shortcuts initialized")

    def _schedule_ui_update(self, callback):
        """
        Schedule a UI update to run on the main thread.

        Used by controllers to update UI from background threads.

        Args:
            callback: Function to call on main thread
        """
        self.after(0, callback)

    # Event handlers
    def _on_preset_selected(self, preset_key: str):
        """Handle preset selection - update customize settings"""
        try:
            # Load preset
            profile = self.load_preset.execute(preset_key)
            logger.info(f"Loaded preset '{preset_key}': {len(profile.settings)} settings")

            # Update customize view with preset values
            self.customize_vm.profile = profile

            # Clear any previously imported JSON profile (mutual exclusivity)
            self.setup_vm.generated_profile = None

        except Exception as e:
            logger.error(f"Failed to load preset: {e}")
            self._show_error("Failed to load preset", str(e))

    def _on_json_imported(self, json_path: str):
        """Handle JSON profile import"""
        try:
            # Load profile from JSON
            profile = self.load_profile.execute(json_path)
            logger.info(f"Loaded JSON profile '{profile.name}': {len(profile.settings)} settings")

            # Update view models
            self.setup_vm.generated_profile = profile
            self.customize_vm.profile = profile

            # Show success in setup view
            self.setup_view.show_json_import_success(profile.name, len(profile.settings))

            # Show info dialog
            self._show_info(
                "Profile Imported",
                f"Successfully loaded '{profile.name}' with {len(profile.settings)} settings.\n\n"
                f"BASE: {profile.get_base_settings_count()} | "
                f"ADVANCED: {profile.get_advanced_settings_count()}\n\n"
                f"Switch to the 'Customize Settings' tab to review and modify your settings."
            )

        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
            self.setup_view.show_json_import_error("File not found")
            self._show_error(
                "Import Failed",
                "Could not find the selected JSON file.\n\nPlease check the file path and try again."
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            self.setup_view.show_json_import_error("Invalid JSON format")
            self._show_error(
                "Import Failed",
                "The selected file is not valid JSON.\n\nPlease select a valid profile JSON file."
            )

        except Exception as e:
            logger.error(f"Failed to import JSON profile: {e}")
            self.setup_view.show_json_import_error(str(e))
            self._show_error(
                "Import Failed",
                f"Failed to import profile from JSON:\n\n{str(e)}"
            )

    def _on_firefox_path_changed(self, path: str):
        """Handle Firefox path selection - import current settings"""
        try:
            self.setup_controller.handle_firefox_path_changed(path)
        except Exception as e:
            logger.error(f"Failed to import from Firefox: {e}")
            self._show_error("Failed to import settings", str(e))

    def _on_profile_imported(self, profile):
        """Handle profile imported from Firefox"""
        if profile is None:
            # Import failed - clear loading status and show error
            self.setup_view._clear_import_status()
            self._show_error(
                "Import Failed",
                "Failed to import settings from the selected Firefox profile.\n\n"
                "Please check that Firefox is closed and the profile is valid."
            )
            return

        logger.info(f"Profile imported: {profile.name} with {len(profile.settings)} settings")

        # Update customize view with imported profile
        self.customize_vm.profile = profile

        # Update setup view to show success
        self.setup_view.show_import_success(len(profile.settings))

        # Show notification
        self._show_info(
            "Firefox Settings Imported",
            f"Loaded {profile.get_base_settings_count()} BASE and "
            f"{profile.get_advanced_settings_count()} ADVANCED settings from your Firefox profile.\n\n"
            f"Switch to the 'Customize Settings' tab to review and modify your settings."
        )

    def _on_generate_recommendation(self):
        """Handle generate recommendation button"""
        try:
            self.setup_controller.handle_generate_recommendation()
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            self._show_error("Failed to generate recommendation", str(e))

    def _on_setup_next(self):
        """Handle next from setup tab"""
        # Optional: Load preset if selected
        if self.setup_vm.selected_preset and not self.setup_vm.generated_profile:
            try:
                profile = self.load_preset.execute(self.setup_vm.selected_preset)
                self.setup_vm.generated_profile = profile
                self.customize_vm.profile = profile  # Update settings values
            except Exception as e:
                logger.error(f"Failed to load preset: {e}")
                self._show_error("Failed to load preset", str(e))
                return
        elif self.setup_vm.generated_profile:
            # Update customize view with generated profile
            self.customize_vm.profile = self.setup_vm.generated_profile

        # Always allow going to customize tab (settings are pre-loaded from metadata)
        self.tabview.set("Customize Settings")

    def _on_customize_next(self):
        """Handle next from customize tab"""
        logger.debug("_on_customize_next: navigating from Customize Settings to Extensions")
        from hardzilla.domain.entities import Profile

        # Build profile from current ViewModel settings (includes user modifications)
        settings = self.customize_vm.settings
        logger.debug("_on_customize_next: customize_vm has %d settings", len(settings) if settings else 0)

        if not settings:
            self._show_error(
                "No Settings",
                "No settings available to apply. Please select a preset or import from Firefox."
            )
            return

        # Create or update profile with current settings
        profile_name = self.customize_vm.profile.name if self.customize_vm.profile else "Custom Configuration"
        profile = Profile(
            name=profile_name,
            settings=settings.copy(),
            metadata={},
            generated_by="user_customization"
        )

        # Pass to apply view model
        self.apply_vm.profile = profile
        self.apply_vm.firefox_path = self.setup_vm.firefox_path
        logger.debug("_on_customize_next: apply_vm.profile='%s' (%d settings), firefox_path=%s",
                      profile.name, len(profile.settings), self.setup_vm.firefox_path)
        self.tabview.set("Extensions")

    def _on_customize_back(self):
        """Handle back from customize tab"""
        self.tabview.set("Setup & Presets")

    def _on_apply(self):
        """Handle apply button"""
        try:
            self.apply_controller.handle_apply()
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            self._show_error("Failed to apply settings", str(e))

    def _on_install_extensions(self):
        """Handle install extensions button"""
        logger.debug("_on_install_extensions: delegating to apply_controller.handle_install_extensions()")
        logger.debug("_on_install_extensions: selected_extensions=%s", self.apply_vm.selected_extensions)
        logger.debug("_on_install_extensions: firefox_path=%s", self.apply_vm.firefox_path)
        try:
            self.apply_controller.handle_install_extensions()
        except Exception as e:
            logger.error(f"Failed to install extensions: {e}", exc_info=True)
            self._show_error("Failed to install extensions", str(e))

    def _on_extensions_next(self):
        """Handle next from extensions tab"""
        logger.debug("_on_extensions_next: navigating Extensions -> Apply to Firefox")
        logger.debug("_on_extensions_next: %d extensions selected", len(self.apply_vm.selected_extensions))
        self.tabview.set("Apply to Firefox")

    def _on_extensions_back(self):
        """Handle back from extensions tab"""
        logger.debug("_on_extensions_back: navigating Extensions -> Customize Settings")
        self.tabview.set("Customize Settings")

    def _on_apply_back(self):
        """Handle back from apply tab"""
        logger.debug("_on_apply_back: navigating Apply to Firefox -> Extensions")
        self.tabview.set("Extensions")

    def _show_error(self, title: str, message: str):
        """Show error dialog"""
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
        """Show info dialog"""
        info_window = ctk.CTkToplevel(self)
        info_window.title(title)
        info_window.geometry("450x250")

        # Success icon
        ctk.CTkLabel(
            info_window,
            text="✓",
            font=ctk.CTkFont(size=48),
            text_color="#2FA572"
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
            fg_color="#2FA572",
            hover_color="#238C5C"
        ).pack(pady=10)


def main():
    """Main entry point for GUI application"""
    # Set appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create and run application
    app = HardzillaGUI()
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
