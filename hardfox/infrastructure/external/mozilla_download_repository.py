#!/usr/bin/env python3
"""
Mozilla Download Repository

Downloads and extracts Firefox installers from Mozilla's CDN.
Uses only stdlib (urllib, hashlib) to avoid extra dependencies.

Security:
- Downloads over HTTPS from Mozilla's official CDN
- Verifies SHA-512 hash against Mozilla's published checksums
- Validates version strings with strict regex before use
"""

import hashlib
import json
import logging
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

VERSIONS_URL = "https://product-details.mozilla.org/1.0/firefox_versions.json"
DOWNLOAD_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/firefox/releases/"
    "{version}/win64/en-US/Firefox%20Setup%20{version}.exe"
)
SHA512_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/firefox/releases/"
    "{version}/SHA512SUMS"
)

# Channel-specific URL templates
DEVEDITION_DOWNLOAD_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/devedition/releases/"
    "{version}/win64/en-US/Firefox%20Setup%20{version}.exe"
)
DEVEDITION_SHA512_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/devedition/releases/"
    "{version}/SHA512SUMS"
)

# Mapping from channel name to Mozilla API version key
CHANNEL_VERSION_KEYS = {
    "stable": "LATEST_FIREFOX_VERSION",
    "beta": "LATEST_FIREFOX_DEVEL_VERSION",
    "devedition": "FIREFOX_DEVEDITION",
}

# Strict version format: digits.digits with optional .digits patch and optional beta suffix
VERSION_RE = re.compile(r'^\d+\.\d+(\.\d+)?(b\d+)?$')


def validate_version(version: str) -> None:
    """
    Validate a Firefox version string.

    Raises:
        ValueError: If the version doesn't match expected format
    """
    if not version or not VERSION_RE.match(version):
        raise ValueError(f"Invalid Firefox version format: {version!r}")


class MozillaDownloadRepository:
    """
    Repository for downloading and extracting Firefox from Mozilla CDN.
    """

    def get_latest_version(self) -> Dict[str, str]:
        """
        Fetch the latest Firefox release version from Mozilla's API.

        Returns:
            Dict with 'version' and 'channel' keys.

        Raises:
            ConnectionError: If the API is unreachable or returns bad data
        """
        try:
            req = urllib.request.Request(
                VERSIONS_URL,
                headers={"User-Agent": "Hardfox/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            version = data.get("LATEST_FIREFOX_VERSION", "")
            if not version:
                raise ValueError("LATEST_FIREFOX_VERSION not found in API response")

            validate_version(version)

            logger.info(f"Latest Firefox version from API: {version}")
            return {"version": version, "channel": "release"}

        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to reach Mozilla API: {e}") from e
        except (json.JSONDecodeError, ValueError) as e:
            raise ConnectionError(f"Invalid API response: {e}") from e

    def get_latest_version_for_channel(self, channel: str) -> Dict[str, str]:
        """
        Fetch the latest Firefox version for a specific channel.

        Args:
            channel: One of "stable", "beta", "devedition"

        Returns:
            Dict with 'version' and 'channel' keys.

        Raises:
            ValueError: If channel is not recognized
            ConnectionError: If the API is unreachable or returns bad data
        """
        version_key = CHANNEL_VERSION_KEYS.get(channel)
        if not version_key:
            raise ValueError(f"Unknown channel: {channel!r}. Must be one of: {list(CHANNEL_VERSION_KEYS.keys())}")

        try:
            req = urllib.request.Request(
                VERSIONS_URL,
                headers={"User-Agent": "Hardfox/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            version = data.get(version_key, "")
            if not version:
                raise ValueError(f"{version_key} not found in API response")

            validate_version(version)

            logger.info(f"Latest Firefox version for {channel}: {version}")
            return {"version": version, "channel": channel}

        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to reach Mozilla API: {e}") from e
        except (json.JSONDecodeError, ValueError) as e:
            raise ConnectionError(f"Invalid API response: {e}") from e

    def _get_urls_for_channel(self, version: str, channel: str) -> tuple:
        """
        Get download and SHA-512 URLs for a given channel.

        Args:
            version: Firefox version string
            channel: One of "stable", "beta", "devedition"

        Returns:
            Tuple of (download_url, sha512_url, installer_filename_in_sums)
        """
        if channel == "devedition":
            download_url = DEVEDITION_DOWNLOAD_URL_TEMPLATE.format(version=version)
            sha512_url = DEVEDITION_SHA512_URL_TEMPLATE.format(version=version)
        else:
            # Both stable and beta use the same /pub/firefox/releases/ path
            download_url = DOWNLOAD_URL_TEMPLATE.format(version=version)
            sha512_url = SHA512_URL_TEMPLATE.format(version=version)

        installer_filename = f"win64/en-US/Firefox Setup {version}.exe"
        return download_url, sha512_url, installer_filename

    def download_installer_for_channel(
        self,
        version: str,
        channel: str,
        dest_path: Path,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Path:
        """
        Download the Firefox installer for a specific channel.

        Reports raw progress in [0.0, 1.0] range:
        - 0.0-0.90: Download progress
        - 0.95: Hash verification
        - 1.0: Complete

        Args:
            version: Firefox version string
            channel: One of "stable", "beta", "devedition"
            dest_path: Directory to save the installer in
            progress_cb: Progress callback(status, progress_0_to_1)
            cancel_event: Threading event to signal cancellation

        Returns:
            Path to the downloaded and verified installer exe

        Raises:
            ConnectionError: If download fails
            RuntimeError: If cancelled or hash verification fails
        """
        validate_version(version)

        download_url, sha512_url, installer_filename = self._get_urls_for_channel(version, channel)
        dest_path.mkdir(parents=True, exist_ok=True)
        installer_path = dest_path / f"Firefox_Setup_{version}.exe"

        logger.info(f"Downloading Firefox {version} ({channel}) from: {download_url}")

        # Fetch expected hash
        expected_hash = self._fetch_expected_hash_from_url(sha512_url, installer_filename)

        if progress_cb:
            progress_cb(f"Downloading Firefox {version} ({channel})...", 0.0)

        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": "Hardfox/1.0"}
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    total_size = int(resp.headers.get("Content-Length", 0))
                    downloaded = 0
                    chunk_size = 64 * 1024

                    with open(installer_path, "wb") as f:
                        while True:
                            if cancel_event and cancel_event.is_set():
                                installer_path.unlink(missing_ok=True)
                                raise RuntimeError("Download cancelled by user")

                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break

                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_cb and total_size > 0:
                                pct = downloaded / total_size
                                size_mb = downloaded / (1024 * 1024)
                                total_mb = total_size / (1024 * 1024)
                                progress_cb(
                                    f"Downloading: {size_mb:.1f} / {total_mb:.1f} MB",
                                    pct * 0.90
                                )

                logger.info(f"Downloaded installer: {installer_path} ({downloaded} bytes)")
                break

            except urllib.error.URLError as e:
                installer_path.unlink(missing_ok=True)
                if attempt < max_retries:
                    logger.warning(f"Download attempt {attempt} failed: {e}, retrying...")
                    if progress_cb:
                        progress_cb(f"Retrying download (attempt {attempt + 1})...", 0.0)
                    continue
                raise ConnectionError(f"Download failed after {max_retries} attempts: {e}") from e

        # Verify SHA-512 hash
        if expected_hash:
            if progress_cb:
                progress_cb("Verifying download integrity...", 0.95)

            if not self._verify_hash(installer_path, expected_hash):
                installer_path.unlink(missing_ok=True)
                raise RuntimeError(
                    "Download integrity check failed: SHA-512 hash mismatch.\n"
                    "The downloaded file may be corrupted or tampered with.\n"
                    "Please try again."
                )
        else:
            logger.warning(
                "SHA-512 checksum not available from Mozilla. "
                "Proceeding without integrity verification."
            )

        return installer_path

    def _fetch_expected_hash_from_url(self, sha512_url: str, installer_filename: str) -> Optional[str]:
        """
        Fetch the expected SHA-512 hash from a specific URL.

        Args:
            sha512_url: URL to SHA512SUMS file
            installer_filename: Relative path of installer in the sums file

        Returns:
            Hex-encoded SHA-512 hash, or None if not available
        """
        try:
            req = urllib.request.Request(
                sha512_url,
                headers={"User-Agent": "Hardfox/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")

            for line in content.splitlines():
                parts = line.split("  ", 1)
                if len(parts) == 2 and parts[1].strip() == installer_filename:
                    expected_hash = parts[0].strip().lower()
                    if len(expected_hash) == 128:
                        logger.info(f"Found SHA-512 hash for {installer_filename}")
                        return expected_hash

            logger.warning(f"SHA-512 hash not found for {installer_filename}")
            return None

        except (urllib.error.URLError, OSError) as e:
            logger.warning(f"Could not fetch SHA512SUMS: {e}")
            return None

    def _fetch_expected_hash(self, version: str) -> Optional[str]:
        """
        Fetch the expected SHA-512 hash for the win64 en-US stable installer.

        Delegates to _fetch_expected_hash_from_url with the stable release URL.

        Args:
            version: Firefox version string

        Returns:
            Hex-encoded SHA-512 hash, or None if not available
        """
        url = SHA512_URL_TEMPLATE.format(version=version)
        installer_filename = f"win64/en-US/Firefox Setup {version}.exe"
        return self._fetch_expected_hash_from_url(url, installer_filename)

    def _verify_hash(self, file_path: Path, expected_hash: str) -> bool:
        """
        Verify SHA-512 hash of a downloaded file.

        Args:
            file_path: Path to file to verify
            expected_hash: Expected hex-encoded SHA-512 hash

        Returns:
            True if hash matches
        """
        sha512 = hashlib.sha512()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(64 * 1024)
                if not chunk:
                    break
                sha512.update(chunk)

        actual_hash = sha512.hexdigest().lower()
        if actual_hash == expected_hash:
            logger.info(f"SHA-512 verification passed for {file_path.name}")
            return True

        logger.error(
            f"SHA-512 mismatch for {file_path.name}!\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}"
        )
        return False

    def download_installer(
        self,
        version: str,
        dest_path: Path,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Path:
        """
        Download the Firefox stable installer for the given version.

        Delegates to download_installer_for_channel with a progress wrapper
        that scales raw [0, 1] progress to [0, 0.6] for backward compatibility
        with the update use case (download is 60% of overall update progress).

        Args:
            version: Firefox version string (e.g. "133.0")
            dest_path: Directory to save the installer in
            progress_cb: Progress callback(status, progress_0_to_1)
            cancel_event: Threading event to signal cancellation

        Returns:
            Path to the downloaded and verified installer exe

        Raises:
            ConnectionError: If download fails
            RuntimeError: If cancelled or hash verification fails
        """
        # Wrap progress to scale raw [0, 1] -> [0, 0.6] for update use case compat
        wrapped_cb = None
        if progress_cb:
            def wrapped_cb(status, progress):
                progress_cb(status, progress * 0.6)

        return self.download_installer_for_channel(
            version=version,
            channel="stable",
            dest_path=dest_path,
            progress_cb=wrapped_cb,
            cancel_event=cancel_event
        )

    def extract_installer(
        self,
        installer_path: Path,
        extract_dir: Path,
        progress_cb: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Path:
        """
        Extract Firefox files from the installer using its built-in /ExtractDir flag.

        The Firefox NSIS installer supports /ExtractDir=<path> which extracts
        all files without running the installer UI.

        Handles nested extraction (some versions extract into a subfolder) by
        moving contents up to the expected directory.

        Note: Cancellation during extraction is not possible because the
        subprocess blocks. The cancel_event is checked after extraction completes.

        Args:
            installer_path: Path to Firefox Setup exe
            extract_dir: Directory to extract into
            progress_cb: Optional progress callback
            cancel_event: Optional cancellation event (checked after extraction)

        Returns:
            Path to the directory containing firefox.exe

        Raises:
            RuntimeError: If extraction fails or firefox.exe not found
        """
        extract_dir.mkdir(parents=True, exist_ok=True)

        if progress_cb:
            progress_cb("Extracting Firefox files (this may take a moment)...", 0.65)

        logger.info(f"Extracting {installer_path} to {extract_dir}")

        try:
            result = subprocess.run(
                [str(installer_path), f"/ExtractDir={extract_dir}"],
                capture_output=True,
                timeout=300  # 5 minutes max
            )

            if result.returncode != 0:
                stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
                raise RuntimeError(
                    f"Extraction failed (exit code {result.returncode}): {stderr}"
                )

        except subprocess.TimeoutExpired:
            raise RuntimeError("Extraction timed out after 5 minutes")

        # Check cancellation after extraction completes
        if cancel_event and cancel_event.is_set():
            shutil.rmtree(str(extract_dir), ignore_errors=True)
            raise RuntimeError("Update cancelled by user")

        # Handle nested extraction: some versions extract into a subfolder
        firefox_exe = extract_dir / "firefox.exe"
        if not firefox_exe.exists():
            for child in extract_dir.iterdir():
                if child.is_dir() and (child / "firefox.exe").exists():
                    # Move contents up one level via staging dir
                    staging = extract_dir.parent / f"{extract_dir.name}.staging"
                    try:
                        child.rename(staging)
                        shutil.rmtree(str(extract_dir))
                        staging.rename(extract_dir)
                    except OSError:
                        # Clean up staging on failure
                        if staging.exists():
                            shutil.rmtree(str(staging), ignore_errors=True)
                        raise
                    break

        firefox_exe = extract_dir / "firefox.exe"
        if not firefox_exe.exists():
            raise RuntimeError(
                f"Extraction completed but firefox.exe not found in {extract_dir}"
            )

        if progress_cb:
            progress_cb("Extraction complete", 0.75)

        logger.info(f"Extraction successful, firefox.exe at: {extract_dir}")
        return extract_dir
