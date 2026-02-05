"""
Install extensions use case.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any

from hardfox.domain.repositories.i_extension_repository import IExtensionRepository
from hardfox.domain.enums.extension_status import InstallationStatus
from hardfox.metadata.extensions_metadata import EXTENSIONS_METADATA

logger = logging.getLogger(__name__)


class InstallExtensionsUseCase:
    """Business logic for installing Firefox extensions."""

    def __init__(self, extension_repo: IExtensionRepository):
        self.extension_repo = extension_repo

    def execute(
        self,
        profile_path: Path,
        extension_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Install selected extensions to Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            extension_ids: List of extension IDs to install

        Returns:
            Dictionary with installation results:
            {
                "installed": ["ext1", "ext2"],
                "failed": {"ext3": "error_message"},
                "total": 7
            }
        """
        # Validate inputs
        if not extension_ids:
            logger.warning("No extensions selected for installation")
            return {
                "installed": [],
                "failed": {},
                "total": 0
            }

        if not profile_path or not profile_path.exists():
            logger.error(f"Invalid profile path: {profile_path}")
            return {
                "installed": [],
                "failed": {ext_id: "Invalid profile path" for ext_id in extension_ids},
                "total": len(extension_ids)
            }

        # Install extensions
        logger.info(f"Installing {len(extension_ids)} extensions to {profile_path}")
        status_map = self.extension_repo.install_extensions(
            profile_path=profile_path,
            extension_ids=extension_ids
        )

        # Build result dictionary
        installed = []
        failed = {}

        for ext_id, status in status_map.items():
            if status == InstallationStatus.INSTALLED:
                installed.append(ext_id)
                logger.info(f"Successfully installed: {EXTENSIONS_METADATA[ext_id]['name']}")
            else:
                ext_name = EXTENSIONS_METADATA.get(ext_id, {}).get('name', ext_id)
                error_msg = "Installation failed"
                failed[ext_name] = error_msg
                logger.error(f"Failed to install: {ext_name}")

        results = {
            "installed": installed,
            "failed": failed,
            "total": len(extension_ids)
        }

        logger.info(f"Installation complete: {len(installed)}/{len(extension_ids)} successful")
        return results
