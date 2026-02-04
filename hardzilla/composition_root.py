#!/usr/bin/env python3
"""
Composition Root
Centralizes dependency injection configuration for the entire application
"""

from pathlib import Path

from hardzilla.infrastructure.parsers import PrefsParser
from hardzilla.infrastructure.persistence import (
    MetadataSettingsRepository,
    FirefoxFileRepository,
    JsonProfileRepository
)
from hardzilla.infrastructure.persistence.firefox_extension_repository import FirefoxExtensionRepository
from hardzilla.infrastructure.persistence.portable_conversion_repository import PortableConversionRepository
from hardzilla.application.mappers import SettingToPrefMapper, PrefToSettingMapper
from hardzilla.application.services import IntentAnalyzer
from hardzilla.application.use_cases import (
    GenerateRecommendationUseCase,
    ApplySettingsUseCase,
    SaveProfileUseCase,
    LoadProfileUseCase,
    ImportFromFirefoxUseCase,
    LoadPresetUseCase
)
from hardzilla.application.use_cases.install_extensions_use_case import InstallExtensionsUseCase
from hardzilla.application.use_cases.convert_to_portable_use_case import ConvertToPortableUseCase


class CompositionRoot:
    """
    Composition Root for dependency injection.

    Wires up all dependencies for the application.
    Used by both CLI and GUI entry points to avoid duplication.
    """

    def __init__(self, app_dir: Path = None):
        """
        Initialize composition root with all dependencies.

        Args:
            app_dir: Application directory (defaults to parent of this file)
        """
        # Configure paths
        self.app_dir = app_dir or Path(__file__).parent.parent
        self.profiles_dir = self.app_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        # Initialize infrastructure layer
        self.parser = PrefsParser()
        self.settings_repo = MetadataSettingsRepository()
        self.firefox_repo = FirefoxFileRepository(self.parser)
        self.profile_repo = JsonProfileRepository(self.profiles_dir, self.settings_repo)
        self.extension_repo = FirefoxExtensionRepository()
        self.portable_repo = PortableConversionRepository()

        # Initialize application layer (mappers and services)
        self.setting_mapper = SettingToPrefMapper()
        self.pref_mapper = PrefToSettingMapper(self.settings_repo)
        self.intent_analyzer = IntentAnalyzer(self.settings_repo)

        # Initialize use cases
        self.generate_recommendation = GenerateRecommendationUseCase(self.intent_analyzer)
        self.apply_settings = ApplySettingsUseCase(self.firefox_repo, self.setting_mapper)
        self.save_profile = SaveProfileUseCase(self.profile_repo)
        self.load_profile = LoadProfileUseCase(self.profile_repo)
        self.import_from_firefox = ImportFromFirefoxUseCase(self.firefox_repo, self.pref_mapper)
        self.load_preset = LoadPresetUseCase(self.settings_repo)
        self.install_extensions = InstallExtensionsUseCase(self.extension_repo)
        self.convert_to_portable = ConvertToPortableUseCase(self.portable_repo)
