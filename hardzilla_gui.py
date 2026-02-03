#!/usr/bin/env python3
"""
Hardzilla v4.0 - GUI Application
Main entry point for the graphical user interface
"""

import sys
import logging
from pathlib import Path
import customtkinter as ctk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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

    Implements a 3-tab interface:
    1. Setup & Presets - Choose profile and Firefox path
    2. Customize Settings - Review and modify settings
    3. Apply to Firefox - Apply configuration to Firefox
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
        self.customize_vm = CustomizeViewModel()
        self.apply_vm = ApplyViewModel()

    def _init_controllers(self):
        """Initialize controllers"""
        self.setup_controller = SetupController(
            view_model=self.setup_vm,
            generate_recommendation=self.generate_recommendation,
            on_next=self._on_setup_next,
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
        # Tab 1: Setup & Presets
        self.setup_view = SetupView(
            parent=self.tabview.tab("Setup & Presets"),
            view_model=self.setup_vm,
            on_generate_recommendation=self._on_generate_recommendation,
            on_next=self._on_setup_next
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

        # Tab 3: Apply to Firefox
        self.apply_view = ApplyView(
            parent=self.tabview.tab("Apply to Firefox"),
            view_model=self.apply_vm,
            on_apply=self._on_apply,
            on_install_extensions=self._on_install_extensions,
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
    def _on_generate_recommendation(self):
        """Handle generate recommendation button"""
        try:
            self.setup_controller.handle_generate_recommendation()
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            self._show_error("Failed to generate recommendation", str(e))

    def _on_setup_next(self):
        """Handle next from setup tab"""
        # Validate Firefox path before proceeding
        if not self.setup_vm.firefox_path:
            self._show_error(
                "Firefox Path Required",
                "Please select a Firefox profile directory before proceeding."
            )
            return

        if not self.setup_controller.validate_firefox_path(self.setup_vm.firefox_path):
            self._show_error(
                "Invalid Firefox Path",
                "The selected directory is not a valid Firefox profile.\n\n"
                "Please select a directory containing prefs.js or times.json."
            )
            return

        # Get or generate profile
        profile = self.setup_vm.generated_profile

        # If no generated profile but preset is selected, load preset
        if not profile and self.setup_vm.selected_preset:
            try:
                profile = self.load_preset.execute(self.setup_vm.selected_preset)
                self.setup_vm.generated_profile = profile  # Cache it
            except Exception as e:
                logger.error(f"Failed to load preset: {e}")
                self._show_error("Failed to load preset", str(e))
                return

        # Proceed to next tab
        if profile:
            self.customize_vm.profile = profile
            self.tabview.set("Customize Settings")
        else:
            self._show_error(
                "No Configuration Selected",
                "Please select a preset or generate a recommendation before proceeding."
            )

    def _on_customize_next(self):
        """Handle next from customize tab"""
        # Pass profile and firefox path to apply view
        if self.customize_vm.profile:
            self.apply_vm.profile = self.customize_vm.profile
            self.apply_vm.firefox_path = self.setup_vm.firefox_path
            self.tabview.set("Apply to Firefox")

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
        try:
            self.apply_controller.handle_install_extensions()
        except Exception as e:
            logger.error(f"Failed to install extensions: {e}")
            self._show_error("Failed to install extensions", str(e))

    def _on_apply_back(self):
        """Handle back from apply tab"""
        self.tabview.set("Customize Settings")

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
