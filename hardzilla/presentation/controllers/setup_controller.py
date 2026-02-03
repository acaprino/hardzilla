#!/usr/bin/env python3
"""
Setup Controller
Handles logic for Screen 1 (Intent & Setup)
"""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from hardzilla.presentation.view_models import SetupViewModel
from hardzilla.application.use_cases import GenerateRecommendationUseCase

logger = logging.getLogger(__name__)


class SetupController:
    """
    Controller for Setup screen.

    Coordinates between SetupView, SetupViewModel, and use cases.
    """

    def __init__(
        self,
        view_model: SetupViewModel,
        generate_recommendation: GenerateRecommendationUseCase,
        on_next: Callable = None,
        ui_callback: Optional[Callable[[Callable], None]] = None
    ):
        """
        Initialize controller.

        Args:
            view_model: SetupViewModel instance
            generate_recommendation: Use case for generating recommendations
            on_next: Callback when user proceeds to next screen
            ui_callback: Callback for scheduling UI updates from background thread
        """
        self.view_model = view_model
        self.generate_recommendation = generate_recommendation
        self.on_next = on_next
        self.ui_callback = ui_callback
        self._generate_thread: Optional[threading.Thread] = None

    def handle_generate_recommendation(self) -> None:
        """
        Handle generate recommendation button click.

        Validates inputs and generates profile in background thread.
        """
        # Prevent double-clicks
        if self._generate_thread and self._generate_thread.is_alive():
            logger.warning("Generation already in progress")
            return

        # Validate inputs before starting thread
        if not self.view_model.use_cases:
            logger.warning("No use cases selected")
            raise ValueError("Please select at least one use case")

        # Set loading state
        self._update_ui_state(is_loading=True)

        # Run in background thread
        self._generate_thread = threading.Thread(
            target=self._generate_worker,
            daemon=True,
            name="GenerateRecommendationThread"
        )
        self._generate_thread.start()

    def _generate_worker(self) -> None:
        """
        Worker thread for generating recommendations.

        Runs IntentAnalyzer without blocking UI.
        """
        try:
            # Generate recommendation
            profile = self.generate_recommendation.execute(
                use_cases=self.view_model.use_cases,
                privacy_level=self.view_model.privacy_level,
                breakage_tolerance=self.view_model.breakage_tolerance
            )

            logger.info(f"Generated profile: {profile.name}")

            # Schedule UI update on main thread
            self._update_ui_state(
                is_loading=False,
                profile=profile
            )

        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}", exc_info=True)
            self._update_ui_state(
                is_loading=False,
                error=str(e)
            )

    def _update_ui_state(
        self,
        is_loading: Optional[bool] = None,
        profile = None,
        error: Optional[str] = None
    ) -> None:
        """
        Update ViewModel state safely from any thread.

        Args:
            is_loading: Whether generation is in progress
            profile: Generated profile
            error: Error message if failed
        """
        def update():
            if is_loading is not None:
                self.view_model.is_loading = is_loading
            if profile is not None:
                self.view_model.generated_profile = profile
            if error is not None:
                # Could add error_message to SetupViewModel if needed
                logger.error(f"UI state error: {error}")

        # Schedule on main thread if callback provided, otherwise run directly
        if self.ui_callback:
            self.ui_callback(update)
        else:
            update()

    def handle_preset_selection(self, preset_name: str) -> None:
        """
        Handle manual preset selection.

        Args:
            preset_name: Name of preset to select
        """
        self.view_model.selected_preset = preset_name
        logger.info(f"Selected preset: {preset_name}")

    def validate_firefox_path(self, path: str) -> bool:
        """
        Validate Firefox profile path.

        Args:
            path: Path to validate

        Returns:
            True if valid, False otherwise
        """
        firefox_path = Path(path)
        if not firefox_path.exists():
            return False

        # Check for Firefox profile markers
        has_prefs = (firefox_path / "prefs.js").exists()
        has_times = (firefox_path / "times.json").exists()

        return has_prefs or has_times

    def handle_next(self) -> None:
        """Handle next button click"""
        if self.view_model.can_proceed and self.on_next:
            self.on_next()
