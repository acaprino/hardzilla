#!/usr/bin/env python3
"""
Keyboard Navigation Handler
Provides keyboard shortcuts and navigation for Hardzilla GUI
"""

import logging
from typing import Callable, Dict, Optional
import customtkinter as ctk

logger = logging.getLogger(__name__)


class KeyboardHandler:
    """
    Manages keyboard shortcuts and navigation for the application.

    Provides:
    - Global shortcuts (Ctrl+S, Ctrl+F, etc.)
    - Navigation shortcuts (Tab, Arrow keys)
    - Action shortcuts (Enter, Escape, Space)
    - Search focus (/)
    """

    def __init__(self, root: ctk.CTk):
        """
        Initialize keyboard handler.

        Args:
            root: Root window to bind shortcuts to
        """
        self.root = root
        self.shortcuts: Dict[str, Callable] = {}
        self.enabled = True

        # Bind global shortcuts
        self._bind_global_shortcuts()

    def _bind_global_shortcuts(self):
        """Bind global keyboard shortcuts"""
        # Ctrl+Q to quit
        self.root.bind('<Control-q>', lambda e: self._handle_quit())

        # Ctrl+W to close window
        self.root.bind('<Control-w>', lambda e: self._handle_quit())

        # F1 for help (future)
        self.root.bind('<F1>', lambda e: self._handle_help())

    def register_shortcut(self, key: str, callback: Callable):
        """
        Register a keyboard shortcut.

        Args:
            key: Key combination (e.g., '<Control-s>', '<slash>')
            callback: Function to call when shortcut pressed
        """
        self.shortcuts[key] = callback
        self.root.bind(key, lambda e: self._execute_shortcut(key))

    def unregister_shortcut(self, key: str):
        """Unregister a keyboard shortcut"""
        if key in self.shortcuts:
            del self.shortcuts[key]
            self.root.unbind(key)

    def _execute_shortcut(self, key: str):
        """Execute registered shortcut callback"""
        if not self.enabled:
            return

        if key in self.shortcuts:
            try:
                self.shortcuts[key]()
            except Exception as e:
                logger.error(f"Error executing shortcut {key}: {e}")

    def _handle_quit(self):
        """Handle quit shortcut"""
        logger.info("Quit shortcut pressed")
        self.root.quit()

    def _handle_help(self):
        """Handle help shortcut"""
        logger.info("Help shortcut pressed")
        self._show_shortcuts_dialog()

    def _show_shortcuts_dialog(self):
        """Show dialog with keyboard shortcuts"""
        dialog = KeyboardShortcutsDialog(self.root)
        dialog.focus()

    def enable(self):
        """Enable keyboard shortcuts"""
        self.enabled = True

    def disable(self):
        """Disable keyboard shortcuts (e.g., when dialog open)"""
        self.enabled = False


class KeyboardShortcutsDialog(ctk.CTkToplevel):
    """Dialog showing available keyboard shortcuts"""

    SHORTCUTS = {
        "Navigation": [
            ("Tab", "Navigate through elements"),
            ("Shift+Tab", "Navigate backwards"),
            ("Arrow Keys", "Navigate categories/options"),
            ("Enter", "Activate/toggle selected item"),
            ("Escape", "Go back/cancel"),
        ],
        "Search": [
            ("/", "Focus search box"),
            ("Ctrl+F", "Focus search box"),
            ("Escape", "Clear search and unfocus"),
        ],
        "Actions": [
            ("Ctrl+S", "Save/Apply settings (Apply screen)"),
            ("Space", "Toggle checkbox/switch"),
        ],
        "Application": [
            ("F1", "Show this help"),
            ("Ctrl+Q", "Quit application"),
            ("Ctrl+W", "Close window"),
        ]
    }

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Keyboard Shortcuts")
        self.geometry("600x500")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build dialog UI"""
        # Header
        header = ctk.CTkLabel(
            self,
            text="⌨️ Keyboard Shortcuts",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=20)

        # Scrollable frame for shortcuts
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Display shortcuts by category
        for category, shortcuts in self.SHORTCUTS.items():
            # Category header
            cat_label = ctk.CTkLabel(
                scroll_frame,
                text=category,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            cat_label.pack(fill="x", pady=(10, 5))

            # Shortcuts in category
            for key, description in shortcuts:
                self._create_shortcut_row(scroll_frame, key, description)

            # Separator
            separator = ctk.CTkFrame(scroll_frame, height=1, fg_color="#3D3D3D")
            separator.pack(fill="x", pady=10)

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Close (Esc)",
            command=self.destroy,
            width=150
        )
        close_btn.pack(pady=(0, 20))

        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())

    def _create_shortcut_row(self, parent, key: str, description: str):
        """Create a row showing a shortcut"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2)
        frame.grid_columnconfigure(1, weight=1)

        # Key (in a styled frame)
        key_frame = ctk.CTkFrame(
            frame,
            fg_color="#2D2D2D",
            corner_radius=4
        )
        key_frame.grid(row=0, column=0, sticky="w", padx=(20, 15))

        key_label = ctk.CTkLabel(
            key_frame,
            text=key,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF"
        )
        key_label.pack(padx=10, pady=5)

        # Description
        desc_label = ctk.CTkLabel(
            frame,
            text=description,
            font=ctk.CTkFont(size=11),
            text_color="#9E9E9E",
            anchor="w"
        )
        desc_label.grid(row=0, column=1, sticky="w")


def bind_search_focus(widget: ctk.CTkEntry, parent_widget):
    """
    Bind '/' key to focus search entry.

    Args:
        widget: Search entry widget to focus
        parent_widget: Parent widget to bind event to
    """
    def focus_search(event):
        widget.focus_set()
        widget.delete(0, 'end')  # Clear on focus
        return "break"  # Prevent '/' from being typed

    parent_widget.bind('/', focus_search)
    parent_widget.bind('<Control-f>', focus_search)


def bind_escape_clear(widget: ctk.CTkEntry):
    """
    Bind Escape to clear search and unfocus.

    Args:
        widget: Search entry widget
    """
    def clear_and_unfocus(event):
        widget.delete(0, 'end')
        widget.master.focus_set()
        return "break"

    widget.bind('<Escape>', clear_and_unfocus)


def bind_navigation_keys(
    widget,
    on_up: Optional[Callable] = None,
    on_down: Optional[Callable] = None,
    on_left: Optional[Callable] = None,
    on_right: Optional[Callable] = None,
    on_enter: Optional[Callable] = None
):
    """
    Bind arrow keys and Enter for navigation.

    Args:
        widget: Widget to bind keys to
        on_up: Callback for Up arrow
        on_down: Callback for Down arrow
        on_left: Callback for Left arrow
        on_right: Callback for Right arrow
        on_enter: Callback for Enter key
    """
    if on_up:
        widget.bind('<Up>', lambda e: on_up())
    if on_down:
        widget.bind('<Down>', lambda e: on_down())
    if on_left:
        widget.bind('<Left>', lambda e: on_left())
    if on_right:
        widget.bind('<Right>', lambda e: on_right())
    if on_enter:
        widget.bind('<Return>', lambda e: on_enter())


def enable_tab_navigation(root: ctk.CTk):
    """
    Enable Tab key navigation through widgets.

    CustomTkinter handles this automatically, but this function
    can be used to customize tab order if needed.

    Args:
        root: Root window
    """
    # CustomTkinter handles tab navigation by default
    # This function is a placeholder for future customization
    pass
