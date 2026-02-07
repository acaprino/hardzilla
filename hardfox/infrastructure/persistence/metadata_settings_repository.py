#!/usr/bin/env python3
"""
Metadata Settings Repository
Loads settings from SETTINGS_METADATA definitions
"""

import logging
from typing import Dict, List, Optional

from hardfox.domain.repositories import ISettingsRepository
from hardfox.domain.entities import Setting
from hardfox.domain.enums import SettingLevel, SettingType

# Import metadata from package (FIX [MED-001]: No more sys.path manipulation)
from hardfox.metadata.settings_metadata import SETTINGS_METADATA

logger = logging.getLogger(__name__)


class MetadataSettingsRepository(ISettingsRepository):
    """
    Repository that loads settings from the existing SETTINGS_METADATA.

    Converts old metadata format to new Setting entities.
    """

    def __init__(self):
        """Initialize repository and load settings"""
        self._settings_cache: Optional[Dict[str, Setting]] = None

    def get_all(self) -> Dict[str, Setting]:
        """Get all available settings"""
        if self._settings_cache is None:
            self._settings_cache = self._load_settings_from_metadata()
        return self._settings_cache.copy()

    def get_by_key(self, key: str) -> Optional[Setting]:
        """Get a setting by its key"""
        all_settings = self.get_all()
        return all_settings.get(key)

    def get_by_category(self, category: str) -> List[Setting]:
        """Get all settings in a category"""
        all_settings = self.get_all()
        return [s for s in all_settings.values() if s.category == category]

    def get_by_level(self, level: str) -> List[Setting]:
        """Get all settings at a specific level"""
        all_settings = self.get_all()
        level_enum = SettingLevel[level] if isinstance(level, str) else level
        return [s for s in all_settings.values() if s.level == level_enum]

    def _load_settings_from_metadata(self) -> Dict[str, Setting]:
        """
        Load settings from SETTINGS_METADATA and convert to Setting entities.

        The existing metadata has a different structure, so we need to map:
        - 'pref' -> key
        - 'level' ('base'/'advanced') -> SettingLevel
        - 'type' ('toggle'/'choice'/'number') -> SettingType
        - 'default' -> value
        """
        settings = {}

        for setting_id, metadata in SETTINGS_METADATA.items():
            try:
                setting = self._convert_metadata_to_setting(setting_id, metadata)
                # Use the Firefox pref key as the dictionary key
                settings[setting.key] = setting
            except Exception as e:
                logger.warning(f"Failed to convert setting '{setting_id}': {e}")

        logger.info(f"Loaded {len(settings)} settings from metadata")
        return settings

    def _convert_metadata_to_setting(
        self,
        setting_id: str,
        metadata: Dict
    ) -> Setting:
        """
        Convert old metadata format to Setting entity.

        Args:
            setting_id: Setting identifier in SETTINGS_METADATA
            metadata: Setting metadata dictionary

        Returns:
            Setting entity
        """
        # Extract Firefox preference key
        pref_key = metadata.get('pref', setting_id)

        # Map level (base/advanced -> BASE/ADVANCED)
        level_str = metadata.get('level', 'base').upper()
        level = SettingLevel[level_str] if level_str in ['BASE', 'ADVANCED'] else SettingLevel.BASE

        # Map type (toggle/choice/number -> enum)
        old_type = metadata.get('type', 'toggle')
        setting_type = self._map_type(old_type)

        # Get default value
        value = metadata.get('default')

        # Get category and subcategory
        category = metadata.get('category', 'other')
        subcategory = metadata.get('subcategory')

        # Get descriptions
        description = metadata.get('short', metadata.get('full', ''))
        if not description:
            description = metadata.get('name', setting_id)

        # Map warning/impact
        impact = metadata.get('impact', 'low')
        compatibility = metadata.get('compatibility', 'none')
        warning = None
        if impact == 'high' or compatibility != 'none':
            warning = f"Impact: {impact}, Compatibility: {compatibility}"

        # Get slider/dropdown options
        min_value = None
        max_value = None
        step = None
        options = None
        firefox_values = None
        toggle_values = None

        if setting_type == SettingType.TOGGLE:
            # For toggles with non-boolean values (e.g., browser.startup.page: [3, 1])
            values_list = metadata.get('values', [])
            if len(values_list) == 2 and not all(isinstance(v, bool) for v in values_list):
                toggle_values = values_list  # [on_value, off_value]

        elif setting_type == SettingType.SLIDER:
            # For sliders, use values list
            values_list = metadata.get('values', [])
            if values_list:
                min_value = min(values_list)
                max_value = max(values_list)
                # Calculate step from values
                if len(values_list) > 1:
                    step = values_list[1] - values_list[0]
            else:
                # Fallback defaults
                min_value = 0
                max_value = 100
                step = 1

        elif setting_type == SettingType.DROPDOWN:
            # For dropdowns, use labels if available, else values
            values_list = metadata.get('values', [])
            labels_list = metadata.get('labels', [])

            # If both values and labels exist, use labels for UI (options)
            # and keep values for Firefox mapping (firefox_values)
            if labels_list:
                options = [str(opt) for opt in labels_list]
                firefox_values = values_list if values_list else None
            else:
                # No labels, use values for both
                options = [str(opt) for opt in values_list]
                firefox_values = None

            # For dropdowns, ensure the default value is in the correct format
            # If it's a Firefox value (URL), convert to label
            if value not in options:
                if firefox_values and value in firefox_values:
                    # Find index and use corresponding label
                    idx = firefox_values.index(value)
                    if idx < len(options):
                        value = options[idx]
                else:
                    # Value not found, use first option as default
                    if options:
                        value = options[0]

        # Determine visibility (core vs advanced)
        # Settings with 'advanced' level are less visible
        visibility = "advanced" if level == SettingLevel.ADVANCED else "core"

        # FIX [Task 18]: Add intent tags and accurate breakage scores
        intent_tags, breakage_score = self._analyze_setting_intent(pref_key, metadata)

        # Create Setting entity
        return Setting(
            key=pref_key,
            value=value,
            level=level,
            setting_type=setting_type,
            category=category,
            subcategory=subcategory,
            description=description,
            warning=warning,
            min_value=min_value,
            max_value=max_value,
            step=step,
            options=options,
            firefox_values=firefox_values,
            toggle_values=toggle_values,
            intent_tags=intent_tags,
            breakage_score=breakage_score,
            visibility=visibility
        )

    def _map_type(self, old_type: str) -> SettingType:
        """Map old type names to SettingType enum"""
        mapping = {
            'toggle': SettingType.TOGGLE,
            'choice': SettingType.DROPDOWN,
            'number': SettingType.SLIDER,
            'slider': SettingType.SLIDER,
            'dropdown': SettingType.DROPDOWN,
            'input': SettingType.INPUT,
        }
        return mapping.get(old_type.lower(), SettingType.TOGGLE)

    def _analyze_setting_intent(self, pref_key: str, metadata: Dict) -> tuple[list[str], int]:
        """
        Analyze setting to determine intent tags and breakage score.

        Args:
            pref_key: Firefox preference key
            metadata: Setting metadata

        Returns:
            Tuple of (intent_tags, breakage_score)
        """
        tags = []
        breakage_score = 0

        # Get metadata fields for analysis
        category = metadata.get('category', '').lower()
        name = metadata.get('name', '').lower()
        short = metadata.get('short', '').lower()
        full = metadata.get('full', '').lower()
        impact = metadata.get('impact', 'low')
        compatibility = metadata.get('compatibility', 'none')

        # Combine text for keyword analysis
        text = f"{name} {short} {full} {pref_key}"

        # === Intent Tags Analysis ===

        # Privacy & Security
        if any(word in text for word in ['privacy', 'tracking', 'telemetry', 'fingerprint']):
            tags.append('privacy')
        if 'tracking' in text or 'tracker' in text:
            tags.append('anti-tracking')
        if 'fingerprint' in text:
            tags.append('anti-fingerprinting')
        if 'telemetry' in text or 'reporting' in text or 'beacon' in text:
            tags.append('telemetry')
        if category == 'security' or 'security' in text or 'https' in text:
            tags.append('security')
        if 'dns' in text or 'doh' in text:
            tags.append('dns-security')
        if 'webrtc' in text:
            tags.append('webrtc')

        # Performance
        if category == 'performance':
            tags.append('performance')
        if 'cache' in text or 'memory' in text:
            tags.append('caching')
        if 'gpu' in text or 'acceleration' in text or 'webrender' in text:
            tags.append('gpu-acceleration')
        if 'battery' in text or 'power' in text:
            tags.append('battery')

        # Features
        if 'cookie' in text:
            tags.append('cookies')
        if 'history' in text or 'session' in text:
            tags.append('history')
        if 'autofill' in text or 'form' in text:
            tags.append('autofill')
        if 'media' in text or 'video' in text or 'audio' in text:
            tags.append('media')
        if 'notification' in text or 'permission' in text or 'geolocation' in text:
            tags.append('permissions')

        # Use Cases
        if 'banking' in text or 'financial' in text:
            tags.append('banking')
        if 'shopping' in text or 'ecommerce' in text:
            tags.append('shopping')
        if 'social' in text or 'share' in text:
            tags.append('social-media')
        if 'streaming' in text:
            tags.append('streaming')
        if 'developer' in text or 'devtools' in text or 'debug' in text:
            tags.append('development')

        # === Breakage Score Calculation ===

        # Base score from impact
        impact_scores = {'low': 1, 'medium': 3, 'high': 5}
        breakage_score = impact_scores.get(impact, 1)

        # Add compatibility penalty
        compat_scores = {'none': 0, 'minor': 2, 'major': 4, 'critical': 6}
        breakage_score += compat_scores.get(compatibility, 0)

        # Specific high-breakage scenarios
        if 'resist' in text and 'fingerprint' in text:
            breakage_score += 2
        if 'webrtc' in text and 'disable' in text:
            breakage_score += 2
        if 'third' in text and 'party' in text and 'cookie' in text:
            breakage_score += 2
        if 'javascript' in text and 'disable' in text:
            breakage_score += 5

        # Cap at 10
        breakage_score = min(breakage_score, 10)

        # Remove duplicates
        tags = sorted(list(set(tags)))

        return tags, breakage_score
