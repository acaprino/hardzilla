#!/usr/bin/env python3
"""
Profile Entity
Represents a complete Firefox hardening configuration profile
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from .setting import Setting
from ..enums import SettingLevel


@dataclass
class Profile:
    """
    Represents a complete Firefox configuration profile.

    Attributes:
        name: Profile name (e.g., "Balanced Privacy Pro", "Developer")
        settings: Dictionary of setting key -> Setting entity
        metadata: Additional profile metadata (description, tags, etc.)
        created_at: Timestamp when profile was created
        modified_at: Timestamp of last modification
        generated_by: How profile was created ("user", "IntentAnalyzer", "preset")
    """
    name: str
    settings: Dict[str, Setting] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    generated_by: str = "user"

    def apply_setting(self, setting: Setting) -> None:
        """
        Add or update a setting in this profile.

        Args:
            setting: Setting to apply
        """
        self.settings[setting.key] = setting
        self.modified_at = datetime.now()

    def get_setting(self, key: str) -> Optional[Setting]:
        """
        Get a setting by key.

        Args:
            key: Setting key to retrieve

        Returns:
            Setting if found, None otherwise
        """
        return self.settings.get(key)

    def remove_setting(self, key: str) -> bool:
        """
        Remove a setting from this profile.

        Args:
            key: Setting key to remove

        Returns:
            True if setting was removed, False if not found
        """
        if key in self.settings:
            del self.settings[key]
            self.modified_at = datetime.now()
            return True
        return False

    def get_settings_by_level(self, level: SettingLevel) -> List[Setting]:
        """
        Get all settings for a specific level.

        Args:
            level: SettingLevel to filter by (BASE or ADVANCED)

        Returns:
            List of settings matching the level
        """
        return [s for s in self.settings.values() if s.level == level]

    def get_settings_by_category(self, category: str) -> List[Setting]:
        """
        Get all settings in a category.

        Args:
            category: Category name to filter by

        Returns:
            List of settings in the category
        """
        return [s for s in self.settings.values() if s.category == category]

    def get_base_settings_count(self) -> int:
        """Get count of BASE level settings"""
        return len(self.get_settings_by_level(SettingLevel.BASE))

    def get_advanced_settings_count(self) -> int:
        """Get count of ADVANCED level settings"""
        return len(self.get_settings_by_level(SettingLevel.ADVANCED))

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize profile to dictionary for JSON export.

        Returns:
            Dictionary representation of profile
        """
        return {
            "name": self.name,
            "settings": {
                key: {
                    "value": setting.value,
                    "level": str(setting.level),
                }
                for key, setting in self.settings.items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "generated_by": self.generated_by
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], settings_metadata: Dict[str, Setting]) -> 'Profile':
        """
        Deserialize profile from dictionary.

        Args:
            data: Dictionary representation of profile
            settings_metadata: Metadata for all available settings

        Returns:
            Profile instance

        Raises:
            ValueError: If required fields are missing or have invalid types
        """
        # Validate required fields
        if not isinstance(data, dict):
            raise ValueError("Profile data must be a dictionary")

        if "name" not in data:
            raise ValueError("Profile data missing required field: 'name'")

        if not isinstance(data["name"], str):
            raise ValueError("Profile 'name' must be a string")

        if data["name"].strip() == "":
            raise ValueError("Profile 'name' cannot be empty")

        # Validate settings field if present
        if "settings" in data:
            if not isinstance(data["settings"], dict):
                raise ValueError("Profile 'settings' must be a dictionary")

            # Validate each setting entry
            for key, setting_data in data["settings"].items():
                if not isinstance(setting_data, dict):
                    raise ValueError(f"Setting '{key}' must be a dictionary")

                if "value" not in setting_data:
                    raise ValueError(f"Setting '{key}' missing required field: 'value'")

                if "level" not in setting_data:
                    raise ValueError(f"Setting '{key}' missing required field: 'level'")

        # Validate optional fields have correct types
        if "metadata" in data and not isinstance(data["metadata"], dict):
            raise ValueError("Profile 'metadata' must be a dictionary")

        if "generated_by" in data and not isinstance(data["generated_by"], str):
            raise ValueError("Profile 'generated_by' must be a string")

        # Create profile instance
        profile = cls(
            name=data["name"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get("modified_at", datetime.now().isoformat())),
            generated_by=data.get("generated_by", "user")
        )

        # Reconstruct settings from saved values + metadata
        for key, saved_setting in data.get("settings", {}).items():
            if key in settings_metadata:
                # Clone metadata setting with saved value
                base_setting = settings_metadata[key]
                setting = base_setting.clone_with_value(saved_setting["value"])
                profile.settings[key] = setting

        return profile

    def validate(self) -> List[str]:
        """
        Validate all settings in profile.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        for key, setting in self.settings.items():
            try:
                # Re-run validation by creating a new instance
                Setting(**setting.__dict__)
            except ValueError as e:
                errors.append(f"Setting '{key}': {str(e)}")

        return errors

    def merge(self, other: 'Profile') -> 'Profile':
        """
        Merge another profile into this one.
        Settings from 'other' overwrite settings in 'self'.

        Args:
            other: Profile to merge into this one

        Returns:
            New Profile with merged settings
        """
        merged = Profile(
            name=f"{self.name} (merged with {other.name})",
            metadata={**self.metadata, **other.metadata},
            generated_by="merge"
        )

        # Add all settings from self
        merged.settings.update(self.settings)

        # Overwrite with settings from other
        merged.settings.update(other.settings)

        return merged
