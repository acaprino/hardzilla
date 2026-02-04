"""
MyFox portable launcher - launches Firefox with a portable profile.

Compiled to MyFox.exe with PyInstaller.

Security note: This launcher executes whatever firefox.exe it finds at
App/Firefox64/firefox.exe (or App/Firefox/firefox.exe). It does NOT verify
the binary's Authenticode signature or hash. This is the same trust model
used by PortableApps.com and similar portable launchers. Users should ensure
the portable installation directory is not on a shared/untrusted drive, as
a replaced firefox.exe binary would be executed without verification.
"""
import os
import sys
import subprocess


def main():
    base = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Find Firefox binary
    ff_dir = os.path.join(base, "App", "Firefox64")
    ff_exe = os.path.join(ff_dir, "firefox.exe")
    if not os.path.isfile(ff_exe):
        ff_dir = os.path.join(base, "App", "Firefox")
        ff_exe = os.path.join(ff_dir, "firefox.exe")
    if not os.path.isfile(ff_exe):
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Firefox not found.\n\nExpected at:\n{ff_exe}",
            "MyFox - Error",
            0x10,
        )
        sys.exit(1)

    # Ensure profile directory exists
    profile = os.path.join(base, "Data", "profile")
    os.makedirs(profile, exist_ok=True)

    # Launch Firefox
    subprocess.Popen(
        [ff_exe, "-profile", profile, "-no-remote"],
        cwd=ff_dir,
        close_fds=True,
    )


if __name__ == "__main__":
    main()
