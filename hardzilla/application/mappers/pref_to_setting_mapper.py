#!/usr/bin/env python3
"""
Pref to Setting Mapper
Converts Firefox preferences to Setting entities
"""

import logging
from typing import Dict, Any, Optional
from hardzilla.domain.entities import Setting
from hardzilla.domain.repositories import ISettingsRepository

logger = logging.getLogger(__name__)


class PrefToSettingMapper:
    """Maps Firefox preferences to Setting entities"""

    def __init__(self, settings_repo: ISettingsRepository):
        """
        Initialize mapper.

        Args:
            settings_repo: Repository providing setting metadata
        """
        self.settings_repo = settings_repo

    def map(self, pref_key: str, pref_value: Any) -> Optional[Setting]:
        """
        Convert Firefox preference to Setting entity.

        Args:
            pref_key: Firefox preference key
            pref_value: Firefox preference value

        Returns:
            Setting entity if pref is known, None otherwise
        """
        # Get metadata for this preference
        metadata_setting = self.settings_repo.get_by_key(pref_key)

        if metadata_setting is None:
            logger.debug(f"Unknown preference '{pref_key}', skipping")
            return None

        # Create new setting with imported value
        return metadata_setting.clone_with_value(pref_value)

    def map_many(self, prefs: Dict[str, Any]) -> Dict[str, Setting]:
        """
        Convert multiple Firefox preferences to Settings.

        Args:
            prefs: Dictionary of pref_key -> pref_value

        Returns:
            Dictionary of pref_key -> Setting entity (only known prefs)
        """
        settings = {}

        for pref_key, pref_value in prefs.items():
            setting = self.map(pref_key, pref_value)
            if setting is not None:
                settings[pref_key] = setting

        logger.info(
            f"Mapped {len(settings)} known preferences out of {len(prefs)} total"
        )

        return settings
