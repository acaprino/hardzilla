#!/usr/bin/env python3
"""
Hardzilla v4.0 - Main Entry Point
Composition Root: Wire up all dependencies and launch application
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from hardzilla.composition_root import CompositionRoot


class HardzillaApp:
    """
    Main application class - Composition Root.

    Wires up all dependencies using Dependency Injection.
    This is where the entire dependency graph is constructed.
    """

    def __init__(self):
        """Initialize application with all dependencies via CompositionRoot"""
        logger.info("Initializing Hardzilla v4.0...")

        # Initialize all dependencies via composition root
        self.composition_root = CompositionRoot(app_dir=Path(__file__).parent)

        # Expose dependencies for convenience
        self.app_dir = self.composition_root.app_dir
        self.profiles_dir = self.composition_root.profiles_dir
        self.parser = self.composition_root.parser
        self.settings_repo = self.composition_root.settings_repo
        self.firefox_repo = self.composition_root.firefox_repo
        self.profile_repo = self.composition_root.profile_repo
        self.setting_mapper = self.composition_root.setting_mapper
        self.pref_mapper = self.composition_root.pref_mapper
        self.intent_analyzer = self.composition_root.intent_analyzer
        self.generate_recommendation = self.composition_root.generate_recommendation
        self.apply_settings = self.composition_root.apply_settings
        self.save_profile = self.composition_root.save_profile
        self.load_profile = self.composition_root.load_profile
        self.import_from_firefox = self.composition_root.import_from_firefox

        logger.info("[OK] Hardzilla v4.0 initialized successfully")

    def run_cli_demo(self):
        """
        Run a CLI demonstration of the intent-based configuration system.
        This will be replaced by the GUI in Phase 4.
        """
        print("\n" + "="*60)
        print("  Hardzilla v4.0 - Firefox Hardening Tool")
        print("  CLI Demo (GUI coming soon)")
        print("="*60 + "\n")

        # Demo: Generate recommendation from intent
        print("[DEMO] Intent-Based Configuration\n")

        print("Simulating user answers:")
        print("  • Use cases: Banking, Shopping")
        print("  • Privacy level: Strong")
        print("  • Breakage tolerance: 40%")
        print()

        profile = self.generate_recommendation.execute(
            use_cases=["banking", "shopping"],
            privacy_level="strong",
            breakage_tolerance=40
        )

        print(f"[OK] Generated profile: '{profile.name}'")
        print(f"  - BASE settings: {profile.get_base_settings_count()}")
        print(f"  - ADVANCED settings: {profile.get_advanced_settings_count()}")
        print(f"  - Total: {len(profile.settings)} settings configured")
        print()

        # Show sample settings
        print("[SETTINGS] Sample configured settings:")
        print()

        sample_count = 0
        for key, setting in list(profile.settings.items())[:10]:
            print(f"  [{setting.level.value}] {setting.key}")
            print(f"      Value: {setting.value}")
            print(f"      Category: {setting.category}")
            sample_count += 1

        print(f"  ... and {len(profile.settings) - sample_count} more")
        print()

        # Save profile option
        print("[SAVE] Saving profile...")
        self.save_profile.execute(profile)
        saved_path = self.profiles_dir / f"{profile.name.lower().replace(' ', '_')}.json"
        print(f"[OK] Profile saved to: {saved_path.name}")
        print()

        print("="*60)
        print("\n[NEXT STEPS]")
        print()
        print("To apply this profile to Firefox:")
        print("1. Close Firefox completely")
        print("2. Run: python hardzilla_main.py --apply <firefox_profile_path>")
        print()
        print("To use the GUI (coming soon):")
        print("- Phase 4 will add a 3-screen wizard interface")
        print("- Screen 1: Answer intent questions")
        print("- Screen 2: Review/customize settings")
        print("- Screen 3: Apply to Firefox profile")
        print()
        print("="*60 + "\n")

    def apply_profile_to_firefox(self, firefox_path: str, profile_name: str):
        """
        Apply a saved profile to a Firefox installation.

        Args:
            firefox_path: Path to Firefox profile directory
            profile_name: Name of saved profile to apply
        """
        print(f"\n[LOAD] Loading profile: {profile_name}")
        profile = self.load_profile.execute(profile_name)

        print(f"[OK] Loaded {len(profile.settings)} settings")
        print()

        firefox_profile = Path(firefox_path)
        if not self.firefox_repo.validate_profile_path(firefox_profile):
            print(f"[ERROR] Invalid Firefox profile path: {firefox_path}")
            print()
            print("Please provide a valid Firefox profile directory.")
            print("Example: C:\\Users\\YourName\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\xxx.default")
            return

        print(f"[APPLY] Applying to Firefox profile: {firefox_profile.name}")
        print()
        print("[WARNING] IMPORTANT: Make sure Firefox is closed!")
        input("Press Enter to continue or Ctrl+C to cancel...")
        print()

        results = self.apply_settings.execute(
            profile_path=firefox_profile,
            settings=profile.settings,
            level=None  # Apply both BASE and ADVANCED
        )

        print(f"[OK] Applied {results['base_applied']} BASE settings (prefs.js)")
        print(f"[OK] Applied {results['advanced_applied']} ADVANCED settings (user.js)")
        print()
        print("="*60)
        print("[SUCCESS] Settings applied to Firefox.")
        print()
        print("Next steps:")
        print("1. Start Firefox")
        print("2. Check about:config to verify settings")
        print("3. Browse normally - settings are active!")
        print("="*60 + "\n")


def main():
    """Main entry point with CLI argument handling"""
    app = HardzillaApp()

    # Simple CLI argument handling (will be replaced by GUI)
    if len(sys.argv) > 1:
        if sys.argv[1] == "--apply" and len(sys.argv) >= 4:
            firefox_path = sys.argv[2]
            profile_name = sys.argv[3]
            app.apply_profile_to_firefox(firefox_path, profile_name)
        elif sys.argv[1] == "--help":
            print("\nHardzilla v4.0 - Firefox Hardening Tool")
            print("\nUsage:")
            print("  python hardzilla_main.py              Run demo")
            print("  python hardzilla_main.py --apply <firefox_path> <profile_name>")
            print("  python hardzilla_main.py --help       Show this help")
            print()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Run with --help for usage")
    else:
        # Run demo by default
        app.run_cli_demo()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n[ERROR] {e}")
        print("\nRun with --help for usage")
        sys.exit(1)
