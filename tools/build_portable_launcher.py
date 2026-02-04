"""
Build FirefoxPortable.exe from portable_launcher.py.

Extracts the Firefox icon from firefox.exe and compiles the launcher
with PyInstaller as a single-file windowed executable.

Usage:
    python tools/build_portable_launcher.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LAUNCHER_SCRIPT = SCRIPT_DIR / "portable_launcher.py"
OUTPUT_DIR = PROJECT_ROOT / "dist"


def extract_firefox_icon(output_ico: Path) -> bool:
    """Extract icon from firefox.exe using ctypes Win32 API."""
    try:
        import ctypes
        import ctypes.wintypes
        from PIL import Image

        # Find firefox.exe
        ff_paths = [
            Path(r"C:\Program Files\Mozilla Firefox\firefox.exe"),
            Path(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"),
        ]
        ff_exe = None
        for p in ff_paths:
            if p.exists():
                ff_exe = str(p)
                break

        if not ff_exe:
            print("Firefox not found, trying VisualElements PNG fallback...")
            return _icon_from_png(output_ico)

        # Use PowerShell to extract icon (most reliable on Windows)
        return _extract_icon_powershell(ff_exe, output_ico)

    except Exception as e:
        print(f"Icon extraction failed: {e}")
        return _icon_from_png(output_ico)


def _extract_icon_powershell(exe_path: str, output_ico: Path) -> bool:
    """Extract icon from exe using PowerShell with encoded command to avoid injection."""
    import base64

    with tempfile.TemporaryDirectory() as tmpdir:
        png_path = Path(tmpdir) / "icon.png"
        # Use forward slashes to avoid PowerShell escape issues
        exe_path_safe = exe_path.replace("\\", "/")
        png_path_safe = str(png_path).replace("\\", "/")
        ps_script = (
            "Add-Type -AssemblyName System.Drawing\n"
            f"$icon = [System.Drawing.Icon]::ExtractAssociatedIcon('{exe_path_safe}')\n"
            "$bmp = $icon.ToBitmap()\n"
            f"$bmp.Save('{png_path_safe}', [System.Drawing.Imaging.ImageFormat]::Png)\n"
        )
        # Encode as UTF-16LE for PowerShell -EncodedCommand
        encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
        result = subprocess.run(
            ["powershell", "-NoProfile", "-EncodedCommand", encoded],
            capture_output=True, text=True
        )
        if result.returncode != 0 or not png_path.exists():
            print(f"PowerShell icon extraction failed: {result.stderr}")
            return _icon_from_png(output_ico)

        return _png_to_ico(png_path, output_ico)


def _icon_from_png(output_ico: Path) -> bool:
    """Create icon from Firefox VisualElements PNG."""
    png_path = Path(r"C:\Program Files\Mozilla Firefox\browser\VisualElements\VisualElements_150.png")
    if not png_path.exists():
        print(f"PNG fallback not found at {png_path}")
        return False
    return _png_to_ico(png_path, output_ico)


def _png_to_ico(png_path: Path, output_ico: Path) -> bool:
    """Convert a PNG to a multi-size ICO file."""
    try:
        from PIL import Image
        img = Image.open(png_path)
        # Convert to RGBA if needed
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        # Create multi-size ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        output_ico.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_ico), format="ICO", sizes=sizes)
        print(f"Icon saved: {output_ico}")
        return True
    except Exception as e:
        print(f"PNG to ICO conversion failed: {e}")
        return False


def build_exe(icon_path: Path = None):
    """Build FirefoxPortable.exe with PyInstaller."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "MyFox",
        "--distpath", str(OUTPUT_DIR),
        "--workpath", str(PROJECT_ROOT / "build" / "portable_launcher"),
        "--specpath", str(PROJECT_ROOT / "build"),
    ]

    if icon_path and icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])

    cmd.append(str(LAUNCHER_SCRIPT))

    print(f"Building FirefoxPortable.exe...")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    exe_path = OUTPUT_DIR / "MyFox.exe"
    if exe_path.exists():
        print(f"\nBuild successful: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("Build completed but exe not found!")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  Building MyFox.exe")
    print("=" * 60)

    # Step 1: Extract icon
    icon_path = SCRIPT_DIR / "firefox.ico"
    print("\n[1/2] Extracting Firefox icon...")
    if not extract_firefox_icon(icon_path):
        print("Warning: Could not extract icon, building without icon.")
        icon_path = None

    # Step 2: Build exe
    print("\n[2/2] Compiling launcher...")
    build_exe(icon_path)

    # Cleanup build artifacts
    build_dir = PROJECT_ROOT / "build" / "portable_launcher"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    spec_file = PROJECT_ROOT / "build" / "MyFox.spec"
    if spec_file.exists():
        spec_file.unlink()

    print("\nDone!")


if __name__ == "__main__":
    main()
