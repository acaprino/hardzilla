"""
Extension row widget for extension selection UI.
"""
import customtkinter as ctk
from typing import Callable

from hardfox.domain.entities.extension import Extension


class ExtensionRow(ctk.CTkFrame):
    """
    Checkbox widget for a single extension.

    Layout: [✓] 🛡️ uBlock Origin - Efficient content blocker (3.2 MB)
    """

    def __init__(
        self,
        parent,
        extension: Extension,
        on_toggle: Callable[[str, bool], None],
        initial_checked: bool = True
    ):
        super().__init__(parent)

        self.extension = extension
        self.on_toggle = on_toggle

        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Checkbox
        self.grid_columnconfigure(1, weight=1)  # Content

        # Checkbox
        self.checkbox_var = ctk.BooleanVar(value=initial_checked)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.checkbox_var,
            command=self._handle_toggle,
            width=30
        )
        self.checkbox.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        # Content frame (icon + name + description + size)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        # Build content text
        content_text = f"{extension.icon} {extension.name} - {extension.description}"
        if extension.size_mb:
            content_text += f" ({extension.size_mb} MB)"

        # Label
        self.label = ctk.CTkLabel(
            content_frame,
            text=content_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.pack(fill="x", pady=5)

        # Trigger initial state callback
        if initial_checked:
            self.on_toggle(self.extension.extension_id, True)

    def _handle_toggle(self):
        """Handle checkbox toggle event."""
        is_checked = self.checkbox_var.get()
        self.on_toggle(self.extension.extension_id, is_checked)

    def get_checked(self) -> bool:
        """Get current checkbox state."""
        return self.checkbox_var.get()

    def set_checked(self, checked: bool):
        """Set checkbox state programmatically."""
        self.checkbox_var.set(checked)
