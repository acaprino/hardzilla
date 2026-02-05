#!/usr/bin/env python3
"""
Setting Entity
Core domain entity representing a Firefox configuration setting
"""

from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from ..enums import SettingLevel, SettingType


@dataclass
class Setting:
    """
    Represents a single Firefox configuration setting.

    Attributes:
        key: Firefox preference key (e.g., "privacy.trackingprotection.enabled")
        value: Current value of the setting
        level: Where to apply (BASE=prefs.js, ADVANCED=user.js)
        setting_type: UI control type (toggle, slider, dropdown, input)
        category: Primary category (e.g., "Privacy", "Performance")
        subcategory: Optional subcategory for organization
        description: Human-readable description
        warning: Optional warning about side effects
        min_value: Minimum value for sliders
        max_value: Maximum value for sliders
        step: Step increment for sliders
        options: Available choices for dropdowns (UI labels)
        firefox_values: For dropdowns - actual Firefox pref values (parallel to options)
        intent_tags: Tags for intent matching (e.g., ["banking", "privacy"])
        breakage_score: 0-10 scale of likelihood to break sites
        visibility: "core" (show by default) or "advanced" (progressive disclosure)
    """
    key: str
    value: Any
    level: SettingLevel
    setting_type: SettingType
    category: str
    subcategory: Optional[str] = None
    description: str = ""
    warning: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    step: Optional[int] = None
    options: Optional[List[str]] = None
    firefox_values: Optional[List[Any]] = None  # For dropdowns: actual Firefox pref values (parallel to options/labels)
    intent_tags: List[str] = field(default_factory=list)
    breakage_score: int = 0
    visibility: str = "core"

    def __post_init__(self):
        """Validate setting after initialization"""
        # Ensure level is SettingLevel enum
        if isinstance(self.level, str):
            self.level = SettingLevel[self.level]

        # Ensure setting_type is SettingType enum
        if isinstance(self.setting_type, str):
            self.setting_type = SettingType(self.setting_type)

        # Validate slider settings
        if self.setting_type == SettingType.SLIDER:
            if self.min_value is None or self.max_value is None:
                raise ValueError(f"Slider setting '{self.key}' must have min_value and max_value")
            if not isinstance(self.value, (int, float)):
                raise ValueError(f"Slider setting '{self.key}' value must be numeric")
            if not (self.min_value <= self.value <= self.max_value):
                raise ValueError(f"Slider value {self.value} out of range [{self.min_value}, {self.max_value}]")

        # Validate dropdown settings
        if self.setting_type == SettingType.DROPDOWN:
            if not self.options:
                raise ValueError(f"Dropdown setting '{self.key}' must have options")
            if self.value not in self.options:
                raise ValueError(f"Dropdown value '{self.value}' not in options {self.options}")

        # Validate breakage score
        if not (0 <= self.breakage_score <= 10):
            raise ValueError(f"Breakage score must be 0-10, got {self.breakage_score}")

        # Validate visibility
        if self.visibility not in ["core", "advanced"]:
            raise ValueError(f"Visibility must be 'core' or 'advanced', got '{self.visibility}'")

    def to_firefox_pref(self) -> str:
        """
        Convert setting to Firefox preference format.

        Returns:
            JavaScript preference line (e.g., 'user_pref("key", value);')
        """
        prefix = self.level.prefix
        formatted_value = self._format_value_for_firefox()
        return f'{prefix}("{self.key}", {formatted_value});'

    def _format_value_for_firefox(self) -> str:
        """Format value according to JavaScript syntax"""
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        elif isinstance(self.value, str):
            # Escape quotes and backslashes
            escaped = self.value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(self.value, (int, float)):
            return str(self.value)
        else:
            raise ValueError(f"Unsupported value type for Firefox: {type(self.value)}")

    def clone_with_value(self, new_value: Any) -> 'Setting':
        """
        Create a copy of this setting with a different value.

        Args:
            new_value: New value for the setting

        Returns:
            New Setting instance with updated value
        """
        return Setting(
            key=self.key,
            value=new_value,
            level=self.level,
            setting_type=self.setting_type,
            category=self.category,
            subcategory=self.subcategory,
            description=self.description,
            warning=self.warning,
            min_value=self.min_value,
            max_value=self.max_value,
            step=self.step,
            options=self.options,
            firefox_values=self.firefox_values,
            intent_tags=self.intent_tags.copy(),
            breakage_score=self.breakage_score,
            visibility=self.visibility
        )

    def matches_intent(self, intent_tags: List[str]) -> bool:
        """
        Check if this setting matches given intent tags.

        Args:
            intent_tags: List of intent tags to match against

        Returns:
            True if any tag matches
        """
        return bool(set(self.intent_tags) & set(intent_tags))

    def label_to_firefox_value(self, label: Any) -> Any:
        """
        Convert a UI label to its corresponding Firefox preference value.

        For dropdowns with separate labels and values (e.g., DNS providers),
        this maps 'Quad9 (9.9.9.9)' → 'https://dns.quad9.net/dns-query'.

        Args:
            label: The UI label value

        Returns:
            Corresponding Firefox preference value, or label if no mapping exists
        """
        if self.setting_type != SettingType.DROPDOWN or not self.firefox_values:
            return label

        # Try exact match
        if label in self.options:
            idx = self.options.index(label)
            if idx < len(self.firefox_values):
                return self.firefox_values[idx]

        # No mapping found, return original
        return label

    def firefox_value_to_label(self, firefox_value: Any) -> Any:
        """
        Convert a Firefox preference value to its corresponding UI label.

        For dropdowns with separate labels and values (e.g., DNS providers),
        this maps 'https://dns.quad9.net/dns-query' → 'Quad9 (9.9.9.9)'.

        Args:
            firefox_value: The Firefox preference value

        Returns:
            Corresponding UI label, or firefox_value if no mapping exists
        """
        if self.setting_type != SettingType.DROPDOWN or not self.firefox_values:
            return firefox_value

        # Try exact match
        if firefox_value in self.firefox_values:
            idx = self.firefox_values.index(firefox_value)
            if idx < len(self.options):
                return self.options[idx]

        # No mapping found, return original
        return firefox_value
