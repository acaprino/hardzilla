#!/usr/bin/env python3
"""
Generate Recommendation Use Case
Business logic for generating AI-driven configuration recommendations
"""

import logging
from typing import List

from hardzilla.domain.entities import Profile
from hardzilla.application.services import IntentAnalyzer

logger = logging.getLogger(__name__)


class GenerateRecommendationUseCase:
    """
    Use case for generating configuration recommendations based on user intent.

    This orchestrates the IntentAnalyzer to produce a complete profile
    from user answers to intent questions.
    """

    def __init__(self, intent_analyzer: IntentAnalyzer):
        """
        Initialize use case.

        Args:
            intent_analyzer: Service for analyzing user intent
        """
        self.intent_analyzer = intent_analyzer

    def execute(
        self,
        use_cases: List[str],
        privacy_level: str,
        breakage_tolerance: int
    ) -> Profile:
        """
        Generate recommended profile from user intent.

        Args:
            use_cases: List of use case selections
            privacy_level: "basic", "moderate", "strong", or "maximum"
            breakage_tolerance: 0-100 scale of willingness to troubleshoot

        Returns:
            Complete Profile with all settings configured

        Raises:
            ValueError: If invalid parameters provided
        """
        # Validate inputs
        self._validate_inputs(use_cases, privacy_level, breakage_tolerance)

        # Generate recommendation
        profile = self.intent_analyzer.analyze(
            use_cases=use_cases,
            privacy_level=privacy_level,
            breakage_tolerance=breakage_tolerance
        )

        logger.info(f"Generated recommendation: {profile.name}")

        return profile

    def _validate_inputs(
        self,
        use_cases: List[str],
        privacy_level: str,
        breakage_tolerance: int
    ) -> None:
        """
        Validate input parameters.

        Args:
            use_cases: List of use cases
            privacy_level: Privacy level string
            breakage_tolerance: Tolerance value

        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate use cases
        if not use_cases or not isinstance(use_cases, list):
            raise ValueError("use_cases must be a non-empty list")

        # Validate privacy level
        valid_privacy_levels = ["basic", "moderate", "strong", "maximum"]
        if privacy_level not in valid_privacy_levels:
            raise ValueError(
                f"privacy_level must be one of {valid_privacy_levels}, got '{privacy_level}'"
            )

        # Validate breakage tolerance
        if not isinstance(breakage_tolerance, int):
            raise ValueError(
                f"breakage_tolerance must be an integer, got {type(breakage_tolerance)}"
            )
        if not (0 <= breakage_tolerance <= 100):
            raise ValueError(
                f"breakage_tolerance must be 0-100, got {breakage_tolerance}"
            )
