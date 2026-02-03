#!/usr/bin/env python3
"""
Intent Analyzer Service
Core innovation: Analyzes user intent and generates optimal configuration
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from hardzilla.domain.entities import Profile, Setting
from hardzilla.domain.repositories import ISettingsRepository

logger = logging.getLogger(__name__)


class IntentAnalyzer:
    """
    Analyzes user intent and generates smart Firefox configuration.

    This is the core innovation of Hardzilla v4.0 - converting user goals
    into technical settings through rule-based analysis.
    """

    # Mapping of use cases to preset profiles
    USE_CASE_TO_PRESET = {
        "development": "developer",
        "banking": "office",
        "shopping": "office",
        "social_media": "casual",
        "work": "office",
        "streaming": "gaming",
        "anonymous": "privacy_enthusiast",
        "general": "casual"
    }

    # Privacy level to aggressiveness mapping
    PRIVACY_LEVELS = {
        "basic": 1,          # Just want better defaults
        "moderate": 3,       # Block ads and trackers
        "strong": 6,         # Strong privacy (some sites may break)
        "maximum": 9         # Maximum privacy (will troubleshoot)
    }

    def __init__(self, settings_repo: ISettingsRepository):
        """
        Initialize analyzer.

        Args:
            settings_repo: Repository for accessing setting metadata
        """
        self.settings_repo = settings_repo

    def analyze(
        self,
        use_cases: List[str],
        privacy_level: str,
        breakage_tolerance: int
    ) -> Profile:
        """
        Analyze user intent and generate recommended profile.

        Args:
            use_cases: List of use case tags (e.g., ["banking", "shopping"])
            privacy_level: "basic", "moderate", "strong", or "maximum"
            breakage_tolerance: 0-100 scale (0=can't tolerate, 100=will troubleshoot)

        Returns:
            Complete Profile with all settings configured

        Example:
            >>> analyzer.analyze(
            ...     use_cases=["banking", "shopping"],
            ...     privacy_level="strong",
            ...     breakage_tolerance=40
            ... )
        """
        logger.info(
            f"Analyzing intent: use_cases={use_cases}, "
            f"privacy_level={privacy_level}, "
            f"breakage_tolerance={breakage_tolerance}"
        )

        # Step 1: Select base preset
        preset_name = self._select_base_preset(use_cases)
        logger.info(f"Selected base preset: {preset_name}")

        # Step 2: Load all settings
        all_settings = self.settings_repo.get_all()

        # Step 3: Apply rule-based adjustments
        configured_settings = self._configure_settings(
            all_settings,
            use_cases,
            privacy_level,
            breakage_tolerance,
            preset_name
        )

        # Step 4: Create profile
        profile_name = self._generate_profile_name(use_cases, privacy_level)

        profile = Profile(
            name=profile_name,
            settings=configured_settings,
            metadata={
                "use_cases": use_cases,
                "privacy_level": privacy_level,
                "breakage_tolerance": breakage_tolerance,
                "base_preset": preset_name,
                "analysis_timestamp": datetime.now().isoformat()
            },
            generated_by="IntentAnalyzer"
        )

        logger.info(
            f"Generated profile '{profile_name}' with {len(configured_settings)} settings"
        )

        return profile

    def _select_base_preset(self, use_cases: List[str]) -> str:
        """
        Select base preset from use cases.

        Priority order:
        1. Privacy/anonymous → privacy_enthusiast
        2. Development → developer
        3. Banking/work/shopping → office
        4. Gaming/streaming → gaming
        5. Default → casual
        """
        # Priority matching
        for use_case in use_cases:
            use_case_lower = use_case.lower()
            if use_case_lower in self.USE_CASE_TO_PRESET:
                return self.USE_CASE_TO_PRESET[use_case_lower]

        # Default to casual
        return "casual"

    def _configure_settings(
        self,
        all_settings: Dict[str, Setting],
        use_cases: List[str],
        privacy_level: str,
        breakage_tolerance: int,
        preset_name: str
    ) -> Dict[str, Setting]:
        """
        Configure each setting based on intent.

        This is where the magic happens - translating user intent into
        concrete setting values.
        """
        configured = {}
        privacy_score = self.PRIVACY_LEVELS.get(privacy_level, 1)

        for key, setting in all_settings.items():
            # Start with default value
            value = setting.value

            # Apply privacy-based rules
            value = self._apply_privacy_rules(
                setting,
                value,
                privacy_score,
                breakage_tolerance
            )

            # Apply use-case-specific rules
            value = self._apply_use_case_rules(
                setting,
                value,
                use_cases
            )

            # Create configured setting
            configured_setting = setting.clone_with_value(value)
            configured[key] = configured_setting

        return configured

    def _apply_privacy_rules(
        self,
        setting: Setting,
        current_value: Any,
        privacy_score: int,
        breakage_tolerance: int
    ) -> Any:
        """
        Apply privacy-based rules to a setting.

        Uses intent tags for smarter matching.
        Higher privacy_score → more aggressive privacy protection
        Higher breakage_tolerance → willing to accept more breakage
        """
        # Skip if breakage score is too high for user's tolerance
        # Convert tolerance (0-100) to comparable scale (0-10)
        max_breakage = int((breakage_tolerance / 100) * 10)

        if setting.breakage_score > max_breakage:
            # User can't tolerate this much breakage, use safer default
            return current_value

        # Use intent tags for matching (NEW - Task 18)
        tags = setting.intent_tags

        # Telemetry - disable for moderate+ privacy
        if 'telemetry' in tags and privacy_score >= 3:
            if isinstance(current_value, bool):
                return False

        # Tracking protection - enable for moderate+ privacy
        if 'anti-tracking' in tags and privacy_score >= 3:
            if isinstance(current_value, bool) and "enabled" in setting.key:
                return True

        # Fingerprinting - enable for strong+ privacy
        if 'anti-fingerprinting' in tags and privacy_score >= 6:
            if isinstance(current_value, bool):
                return True

        # DNS security - enable for strong+ privacy
        if 'dns-security' in tags and privacy_score >= 6:
            if "mode" in setting.key or "enabled" in setting.key:
                if isinstance(current_value, int):
                    return 2  # TRR mode 2 (DoH preferred)
                elif isinstance(current_value, bool):
                    return True

        # Privacy tag - general privacy settings
        if 'privacy' in tags and privacy_score >= 3:
            if "enabled" in setting.key and isinstance(current_value, bool):
                return True

        return current_value

    def _apply_use_case_rules(
        self,
        setting: Setting,
        current_value: Any,
        use_cases: List[str]
    ) -> Any:
        """
        Apply use-case-specific rules.

        Uses intent tags for smarter matching (Task 18).
        Different use cases need different settings optimized.
        """
        use_cases_lower = [uc.lower() for uc in use_cases]
        tags = setting.intent_tags

        # Banking use case: Extra security
        if "banking" in use_cases_lower:
            if 'banking' in tags or 'anti-fingerprinting' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

            # Disable WebRTC (privacy leak)
            if 'webrtc' in tags and "enabled" in setting.key:
                if isinstance(current_value, bool):
                    return False

        # Development use case: Enable dev tools, relax restrictions
        if "development" in use_cases_lower:
            if 'development' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

            # Don't break dev workflow with fingerprinting
            if 'anti-fingerprinting' in tags:
                return False  # Keep default (less restrictive)

        # Shopping use case: Allow necessary features
        if "shopping" in use_cases_lower:
            if 'shopping' in tags or 'cookies' in tags:
                # Allow third-party cookies for payment
                if "thirdparty" in setting.key.lower():
                    if isinstance(current_value, bool):
                        return True

        # Streaming use case: Performance & media
        if "streaming" in use_cases_lower or "gaming" in use_cases_lower:
            if 'streaming' in tags or 'gpu-acceleration' in tags or 'media' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

        # Anonymous/Research: Maximum privacy
        if "anonymous" in use_cases_lower:
            if 'anti-fingerprinting' in tags or 'privacy' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

            # Block third-party cookies
            if 'cookies' in tags and "thirdparty" in setting.key.lower():
                if isinstance(current_value, bool):
                    return False

        # Social media: Enable sharing features
        if "social_media" in use_cases_lower:
            if 'social-media' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

        # Work/Productivity: Balance features and security
        if "work" in use_cases_lower:
            # Enable autofill for forms
            if 'autofill' in tags:
                if isinstance(current_value, bool) and "enabled" in setting.key:
                    return True

        return current_value

    def _generate_profile_name(
        self,
        use_cases: List[str],
        privacy_level: str
    ) -> str:
        """Generate descriptive profile name from intent"""
        # Map privacy level to descriptive term
        privacy_terms = {
            "basic": "Standard",
            "moderate": "Balanced",
            "strong": "Privacy Pro",
            "maximum": "Maximum Privacy"
        }

        privacy_term = privacy_terms.get(privacy_level, "Custom")

        # Add primary use case if available
        if use_cases:
            primary = use_cases[0].title()
            return f"{primary} - {privacy_term}"

        return f"{privacy_term} Profile"
