"""
Uninstall extensions use case.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any

from hardfox.domain.repositories.i_extension_repository import IExtensionRepository
from hardfox.domain.enums.extension_status import InstallationStatus
from hardfox.metadata.extensions_metadata import EXTENSIONS_METADATA

logger = logging.getLogger(__name__)


class UninstallExtensionsUseCase:
    """Business logic for uninstalling Firefox extensions."""

    def __init__(self, extension_repo: IExtensionRepository):
        self.extension_repo = extension_repo

    def execute(
        self,
        profile_path: Path,
        extension_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Uninstall selected extensions from Firefox profile.

        Args:
            profile_path: Path to Firefox profile directory
            extension_ids: List of extension IDs to uninstall

        Returns:
            Dictionary with uninstallation results:
            {
                "uninstalled": ["ext1", "ext2"],
                "failed": {"ext3": "error_message"},
                "total": N
            }
        """
        if not extension_ids:
            logger.warning("No extensions selected for uninstallation")
            return {
                "uninstalled": [],
                "failed": {},
                "total": 0
            }

        if not profile_path or not profile_path.exists():
            logger.error(f"Invalid profile path: {profile_path}")
            return {
                "uninstalled": [],
                "failed": {ext_id: "Invalid profile path" for ext_id in extension_ids},
                "total": len(extension_ids)
            }

        logger.info(f"Uninstalling {len(extension_ids)} extensions from {profile_path}")
        status_map = self.extension_repo.uninstall_extensions(
            profile_path=profile_path,
            extension_ids=extension_ids
        )

        uninstalled = []
        failed = {}

        for ext_id, status in status_map.items():
            if status == InstallationStatus.UNINSTALLED:
                uninstalled.append(ext_id)
                ext_name = EXTENSIONS_METADATA.get(ext_id, {}).get('name', ext_id)
                logger.info(f"Successfully uninstalled: {ext_name}")
            else:
                ext_name = EXTENSIONS_METADATA.get(ext_id, {}).get('name', ext_id)
                failed[ext_name] = "Not found in policies or removal failed"
                logger.error(f"Failed to uninstall: {ext_name}")

        results = {
            "uninstalled": uninstalled,
            "failed": failed,
            "total": len(extension_ids)
        }

        logger.info(f"Uninstallation complete: {len(uninstalled)}/{len(extension_ids)} successful")
        return results

    def get_installed(self, profile_path: Path) -> List[str]:
        """
        Get list of extension IDs currently installed via policies.json.

        Args:
            profile_path: Path to Firefox profile directory

        Returns:
            List of known extension IDs present in policies.json
        """
        return self.extension_repo.get_installed_extensions(profile_path)
