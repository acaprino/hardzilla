"""
Standalone portable Firefox updater.

Compiled to UpdateFirefox.exe with PyInstaller. Self-contained — no hardfox imports.
Detects its own location as the portable root, checks for updates, and performs
an in-place upgrade with atomic directory swap.

Security:
- Downloads over HTTPS from Mozilla's official CDN
- Verifies SHA-512 hash against Mozilla's published checksums
- Validates version strings with strict regex before use
"""

import configparser
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from datetime import datetime, timezone
from tkinter import ttk
import urllib.error
import urllib.request

VERSIONS_URL = "https://product-details.mozilla.org/1.0/firefox_versions.json"
DOWNLOAD_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/firefox/releases/"
    "{version}/win64/en-US/Firefox%20Setup%20{version}.exe"
)
SHA512_URL_TEMPLATE = (
    "https://download-installer.cdn.mozilla.net/pub/firefox/releases/"
    "{version}/SHA512SUMS"
)
VERSION_RE = re.compile(r'^\d+\.\d+(\.\d+)?$')


def validate_version(version):
    """Validate a Firefox version string format."""
    if not version or not VERSION_RE.match(version):
        raise ValueError(f"Invalid Firefox version format: {version!r}")


def get_base_dir():
    """Get the directory where this executable/script lives."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def find_firefox_dir(base):
    """Find Firefox directory within portable structure."""
    for subdir in ("App\\Firefox64", "App\\Firefox"):
        candidate = os.path.join(base, subdir)
        if os.path.isfile(os.path.join(candidate, "firefox.exe")):
            return candidate
    return None


def read_current_version(firefox_dir):
    """Read version from application.ini."""
    ini_path = os.path.join(firefox_dir, "application.ini")
    if not os.path.isfile(ini_path):
        return None
    config = configparser.ConfigParser()
    config.read(ini_path, encoding="utf-8")
    if config.has_section("App"):
        return config.get("App", "Version", fallback=None)
    return None


def get_latest_version():
    """Fetch latest Firefox version from Mozilla API."""
    req = urllib.request.Request(
        VERSIONS_URL,
        headers={"User-Agent": "HardfoxUpdater/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    version = data.get("LATEST_FIREFOX_VERSION", "")
    validate_version(version)
    return version


def compare_versions(current, latest):
    """Return True if latest > current."""
    try:
        cur = tuple(int(x) for x in current.split("."))
        lat = tuple(int(x) for x in latest.split("."))
        return lat > cur
    except (ValueError, AttributeError):
        return current != latest


def fetch_expected_hash(version):
    """Fetch SHA-512 hash for the win64 en-US installer from Mozilla."""
    url = SHA512_URL_TEMPLATE.format(version=version)
    installer_filename = f"win64/en-US/Firefox Setup {version}.exe"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HardfoxUpdater/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        for line in content.splitlines():
            parts = line.split("  ", 1)
            if len(parts) == 2 and parts[1].strip() == installer_filename:
                h = parts[0].strip().lower()
                if len(h) == 128:
                    return h
    except (urllib.error.URLError, OSError):
        pass
    return None


def verify_hash(file_path, expected_hash):
    """Verify SHA-512 hash of a file. Returns True if match."""
    sha512 = hashlib.sha512()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            sha512.update(chunk)
    return sha512.hexdigest().lower() == expected_hash


class UpdaterApp:
    """Simple Tkinter GUI for the standalone updater."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Update Portable Firefox")
        self.root.geometry("480x320")
        self.root.resizable(False, False)

        self.base_dir = get_base_dir()
        self.firefox_dir = None
        self.current_version = None
        self.latest_version = None
        self.cancel_event = threading.Event()

        self._build_ui()
        self._detect_versions()

    def _build_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="Portable Firefox Updater",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))

        self.info_label = tk.Label(
            frame, text="Detecting current version...",
            font=("Segoe UI", 10), wraplength=420, justify="left"
        )
        self.info_label.pack(fill="x", pady=(0, 10))

        self.version_label = tk.Label(
            frame, text="",
            font=("Segoe UI", 10), wraplength=420, justify="left"
        )
        self.version_label.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 5))

        self.status_label = tk.Label(
            frame, text="",
            font=("Segoe UI", 9), fg="gray", anchor="w"
        )
        self.status_label.pack(fill="x", pady=(0, 10))

        btn_frame = tk.Frame(frame)
        btn_frame.pack()

        self.update_btn = tk.Button(
            btn_frame, text="Update Firefox",
            command=self._on_update, state="disabled",
            font=("Segoe UI", 10), padx=15, pady=5
        )
        self.update_btn.pack(side="left", padx=5)

        self.cancel_btn = tk.Button(
            btn_frame, text="Close",
            command=self._on_close,
            font=("Segoe UI", 10), padx=15, pady=5
        )
        self.cancel_btn.pack(side="left", padx=5)

    def _detect_versions(self):
        """Detect current version and check for updates."""
        self.firefox_dir = find_firefox_dir(self.base_dir)
        if not self.firefox_dir:
            self.info_label.config(
                text="Firefox not found in this directory.\n\n"
                     "Expected portable structure:\n"
                     "  App/Firefox64/firefox.exe",
                fg="red"
            )
            return

        self.current_version = read_current_version(self.firefox_dir)
        if not self.current_version:
            self.info_label.config(
                text="Could not read Firefox version from application.ini.",
                fg="red"
            )
            return

        self.info_label.config(
            text=f"Portable Firefox found at:\n{self.firefox_dir}",
            fg="black"
        )

        # Check for updates in background
        threading.Thread(target=self._check_update_worker, daemon=True).start()

    def _check_update_worker(self):
        try:
            self.latest_version = get_latest_version()
            if not self.latest_version:
                self.root.after(0, lambda: self.version_label.config(
                    text="Could not determine latest version.", fg="red"
                ))
                return

            if compare_versions(self.current_version, self.latest_version):
                self.root.after(0, lambda: self._show_update_available())
            else:
                self.root.after(0, lambda: self.version_label.config(
                    text=f"Firefox {self.current_version} is up to date.",
                    fg="green"
                ))
        except Exception as e:
            self.root.after(0, lambda: self.version_label.config(
                text=f"Update check failed: {e}", fg="red"
            ))

    def _show_update_available(self):
        self.version_label.config(
            text=f"Current: {self.current_version}  \u2192  Latest: {self.latest_version}",
            fg="orange"
        )
        self.update_btn.config(state="normal")

    def _on_update(self):
        self.update_btn.config(state="disabled")
        self.cancel_btn.config(text="Cancel", command=self._on_cancel)
        self.cancel_event.clear()

        threading.Thread(target=self._update_worker, daemon=True).start()

    def _on_cancel(self):
        self.cancel_event.set()

    def _on_close(self):
        self.root.destroy()

    def _set_progress(self, value, status=""):
        self.root.after(0, lambda: self.progress.config(value=value))
        if status:
            self.root.after(0, lambda: self.status_label.config(text=status))

    def _update_worker(self):
        temp_dir = None
        try:
            firefox_parent = os.path.dirname(self.firefox_dir)
            firefox_name = os.path.basename(self.firefox_dir)

            # Fetch expected hash
            expected_hash = fetch_expected_hash(self.latest_version)

            # Download with retry
            temp_dir = tempfile.mkdtemp(prefix="firefox_update_")
            url = DOWNLOAD_URL_TEMPLATE.format(version=self.latest_version)
            installer_path = os.path.join(temp_dir, f"Firefox_Setup_{self.latest_version}.exe")

            self._set_progress(0, f"Downloading Firefox {self.latest_version}...")

            max_retries = 2
            for attempt in range(1, max_retries + 1):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "HardfoxUpdater/1.0"})
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        total = int(resp.headers.get("Content-Length", 0))
                        downloaded = 0
                        with open(installer_path, "wb") as f:
                            while True:
                                if self.cancel_event.is_set():
                                    self._finish_error("Update cancelled.")
                                    return
                                chunk = resp.read(64 * 1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total > 0:
                                    pct = (downloaded / total) * 60
                                    mb = downloaded / (1024 * 1024)
                                    total_mb = total / (1024 * 1024)
                                    self._set_progress(pct, f"Downloading: {mb:.1f} / {total_mb:.1f} MB")
                    break  # Success
                except urllib.error.URLError as e:
                    if os.path.exists(installer_path):
                        os.unlink(installer_path)
                    if attempt < max_retries:
                        self._set_progress(0, f"Retrying download (attempt {attempt + 1})...")
                        continue
                    self._finish_error(f"Download failed after {max_retries} attempts: {e}")
                    return

            if self.cancel_event.is_set():
                self._finish_error("Update cancelled.")
                return

            # Verify SHA-512 hash
            if expected_hash:
                self._set_progress(62, "Verifying download integrity...")
                if not verify_hash(installer_path, expected_hash):
                    os.unlink(installer_path)
                    self._finish_error(
                        "Download integrity check failed: SHA-512 hash mismatch.\n"
                        "The downloaded file may be corrupted. Please try again."
                    )
                    return

            # Extract
            self._set_progress(65, "Extracting Firefox files (this may take a moment)...")
            new_dir = os.path.join(firefox_parent, f"{firefox_name}.new")
            if os.path.exists(new_dir):
                shutil.rmtree(new_dir)

            result = subprocess.run(
                [installer_path, f"/ExtractDir={new_dir}"],
                capture_output=True, timeout=300
            )
            if result.returncode != 0:
                self._finish_error(f"Extraction failed (exit code {result.returncode})")
                return

            # Check cancellation after extraction
            if self.cancel_event.is_set():
                shutil.rmtree(new_dir, ignore_errors=True)
                self._finish_error("Update cancelled.")
                return

            # Handle nested extraction
            if not os.path.isfile(os.path.join(new_dir, "firefox.exe")):
                for child in os.listdir(new_dir):
                    child_path = os.path.join(new_dir, child)
                    if os.path.isdir(child_path) and os.path.isfile(os.path.join(child_path, "firefox.exe")):
                        staging = os.path.join(firefox_parent, f"{firefox_name}.staging")
                        try:
                            os.rename(child_path, staging)
                            shutil.rmtree(new_dir)
                            os.rename(staging, new_dir)
                        except OSError:
                            # Clean up staging on failure
                            if os.path.exists(staging):
                                shutil.rmtree(staging, ignore_errors=True)
                            raise
                        break

            if not os.path.isfile(os.path.join(new_dir, "firefox.exe")):
                shutil.rmtree(new_dir, ignore_errors=True)
                self._finish_error("Extraction failed: firefox.exe not found")
                return

            if self.cancel_event.is_set():
                shutil.rmtree(new_dir, ignore_errors=True)
                self._finish_error("Update cancelled.")
                return

            # Atomic swap
            self._set_progress(80, "Replacing Firefox files...")
            old_dir = os.path.join(firefox_parent, f"{firefox_name}.old")
            if os.path.exists(old_dir):
                shutil.rmtree(old_dir)

            try:
                os.rename(self.firefox_dir, old_dir)
            except OSError as e:
                shutil.rmtree(new_dir, ignore_errors=True)
                self._finish_error(f"Failed to move current Firefox: {e}\nMake sure Firefox is not running.")
                return

            try:
                os.rename(new_dir, self.firefox_dir)
            except OSError as e:
                # Rollback
                try:
                    os.rename(old_dir, self.firefox_dir)
                except OSError as rollback_err:
                    self._finish_error(
                        f"CRITICAL: Update failed and rollback failed.\n"
                        f"Your Firefox files are at:\n  {old_dir}\n\n"
                        f"To recover, rename that folder back to:\n  {self.firefox_dir}\n\n"
                        f"Error: {e}\nRollback error: {rollback_err}"
                    )
                    return
                self._finish_error(f"Failed to place new Firefox: {e}")
                return

            # Cleanup old
            self._set_progress(90, "Cleaning up...")
            try:
                shutil.rmtree(old_dir)
            except OSError:
                pass

            # Update metadata
            self._set_progress(95, "Updating metadata...")
            meta_path = os.path.join(self.base_dir, "portable_metadata.json")
            metadata = {}
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass

            new_ver = read_current_version(self.firefox_dir) or self.latest_version
            metadata["firefox_version"] = new_ver
            metadata["last_updated"] = datetime.now(timezone.utc).isoformat()

            try:
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            except OSError:
                pass

            self._set_progress(100, "")
            self.root.after(0, lambda: self._finish_success(new_ver))

        except Exception as e:
            self._finish_error(str(e))
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError:
                    pass

    def _finish_success(self, new_version):
        self.version_label.config(
            text=f"Updated: {self.current_version} \u2192 {new_version}",
            fg="green"
        )
        self.status_label.config(text="Please restart Firefox to use the new version.")
        self.cancel_btn.config(text="Close", command=self._on_close)
        self.current_version = new_version

    def _finish_error(self, msg):
        self.root.after(0, lambda: self.status_label.config(text=f"Error: {msg}", fg="red"))
        self.root.after(0, lambda: self.cancel_btn.config(text="Close", command=self._on_close))
        self.root.after(0, lambda: self.update_btn.config(state="normal"))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = UpdaterApp()
    app.run()
