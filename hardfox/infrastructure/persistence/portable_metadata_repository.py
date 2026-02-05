#!/usr/bin/env python3
"""
Portable Metadata Repository

Reads version info from Firefox's application.ini and manages
portable_metadata.json for tracking portable installation state.
"""

import configparser
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PortableMetadataRepository:
    """
    Repository for reading/writing portable Firefox metadata.

    Reads Firefox version from App/Firefox64/application.ini and manages
    portable_metadata.json in the portable root directory.
    """

    def read_version(self, firefox_dir: Path) -> Dict[str, str]:
        """
        Read Firefox version from application.ini.

        Args:
            firefox_dir: Path to Firefox directory (e.g. App/Firefox64)

        Returns:
            Dict with 'version' and 'build_id' keys, empty strings if not found
        """
        ini_path = firefox_dir / "application.ini"
        result = {"version": "", "build_id": ""}

        if not ini_path.exists():
            logger.warning(f"application.ini not found at: {ini_path}")
            return result

        try:
            config = configparser.ConfigParser()
            config.read(str(ini_path), encoding="utf-8")

            if config.has_section("App"):
                result["version"] = config.get("App", "Version", fallback="")
                result["build_id"] = config.get("App", "BuildID", fallback="")

            logger.info(f"Read Firefox version: {result['version']} (build {result['build_id']})")
        except Exception as e:
            logger.error(f"Failed to parse application.ini: {e}")

        return result

    def read_metadata(self, portable_root: Path) -> Dict:
        """
        Read portable_metadata.json from the portable root directory.

        Args:
            portable_root: Root of portable Firefox installation

        Returns:
            Dict with metadata, empty dict if file doesn't exist
        """
        meta_path = portable_root / "portable_metadata.json"

        if not meta_path.exists():
            return {}

        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to read portable_metadata.json: {e}")
            return {}

    def write_metadata(self, portable_root: Path, data: Dict) -> None:
        """
        Write portable_metadata.json to the portable root directory.

        Args:
            portable_root: Root of portable Firefox installation
            data: Metadata dict to write
        """
        meta_path = portable_root / "portable_metadata.json"

        try:
            meta_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            logger.info(f"Wrote portable_metadata.json at: {meta_path}")
        except OSError as e:
            logger.error(f"Failed to write portable_metadata.json: {e}")

    def find_firefox_dir(self, portable_root: Path) -> Optional[Path]:
        """
        Find the Firefox directory within a portable installation.

        Args:
            portable_root: Root of portable Firefox installation

        Returns:
            Path to Firefox directory, or None if not found
        """
        for subdir in ("App/Firefox64", "App/Firefox"):
            candidate = portable_root / subdir
            if (candidate / "firefox.exe").exists():
                return candidate
        return None

    @staticmethod
    def compare_versions(current: str, latest: str) -> bool:
        """
        Compare two version strings. Returns True if latest > current.

        Uses tuple-based comparison on integer version segments.

        Args:
            current: Current version string (e.g. "132.0")
            latest: Latest version string (e.g. "133.0")

        Returns:
            True if latest is newer than current
        """
        try:
            current_parts = tuple(int(x) for x in current.split("."))
            latest_parts = tuple(int(x) for x in latest.split("."))
            return latest_parts > current_parts
        except (ValueError, AttributeError):
            # If parsing fails, treat as different (allow update)
            return current != latest
