#!/usr/bin/env python3
"""
Screen Navigator
Manages navigation between the 3 wizard screens
"""

import logging
from typing import Dict, Optional, Callable
import customtkinter as ctk

logger = logging.getLogger(__name__)


class ScreenNavigator:
    """
    Manages navigation flow for the 3-screen wizard.

    Screens:
    1. Setup (Intent & Firefox path)
    2. Customize (Review/modify settings)
    3. Apply (Apply to Firefox)
    """

    def __init__(self, container: ctk.CTkFrame):
        """
        Initialize navigator.

        Args:
            container: Parent container to hold screens
        """
        self.container = container
        self.screens: Dict[str, ctk.CTkFrame] = {}
        self.current_screen: Optional[str] = None
        self.screen_order = ["setup", "customize", "apply"]

    def register_screen(self, name: str, screen: ctk.CTkFrame) -> None:
        """
        Register a screen.

        Args:
            name: Screen identifier
            screen: Screen widget instance
        """
        self.screens[name] = screen
        logger.info(f"Registered screen: {name}")

    def show_screen(self, name: str) -> None:
        """
        Show a specific screen, hiding others.

        Args:
            name: Screen identifier to show
        """
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not registered")

        # Hide current screen
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].pack_forget()

        # Show new screen
        self.screens[name].pack(fill="both", expand=True, padx=20, pady=20)
        self.current_screen = name

        logger.info(f"Showing screen: {name}")

    def next_screen(self) -> bool:
        """
        Navigate to next screen.

        Returns:
            True if navigated, False if already at last screen
        """
        if not self.current_screen:
            return False

        try:
            current_idx = self.screen_order.index(self.current_screen)
            if current_idx < len(self.screen_order) - 1:
                next_screen = self.screen_order[current_idx + 1]
                self.show_screen(next_screen)
                return True
        except ValueError:
            pass

        return False

    def previous_screen(self) -> bool:
        """
        Navigate to previous screen.

        Returns:
            True if navigated, False if already at first screen
        """
        if not self.current_screen:
            return False

        try:
            current_idx = self.screen_order.index(self.current_screen)
            if current_idx > 0:
                prev_screen = self.screen_order[current_idx - 1]
                self.show_screen(prev_screen)
                return True
        except ValueError:
            pass

        return False

    def get_progress(self) -> tuple[int, int]:
        """
        Get current progress.

        Returns:
            Tuple of (current_step, total_steps)
        """
        if not self.current_screen:
            return (0, len(self.screen_order))

        try:
            current_idx = self.screen_order.index(self.current_screen)
            return (current_idx + 1, len(self.screen_order))
        except ValueError:
            return (0, len(self.screen_order))
