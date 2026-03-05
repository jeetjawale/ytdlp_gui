#!/usr/bin/env python3
"""Build standalone executables using PyInstaller.

Usage:
    python build.py          # Build for current platform
    python build.py --onefile # Single-file executable
"""

import argparse
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Build YT-DLP GUI")
    parser.add_argument(
        "--onefile", action="store_true",
        help="Build as a single executable file",
    )
    parser.add_argument(
        "--name", default="YT-DLP-GUI",
        help="Name of the output executable (default: YT-DLP-GUI)",
    )
    parser.add_argument(
        "--console", action="store_true",
        help="Show console window (useful for debugging)",
    )
    args = parser.parse_args()

    # Ensure PyInstaller is available
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", args.name,
        "--noconfirm",
        "--clean",
    ]

    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if not args.console:
        cmd.append("--noconsole")

    # Collect hidden imports that PyInstaller may miss
    hidden_imports = [
        "yt_dlp",
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Include our source package
    cmd.extend(["--add-data", "src:src"])

    # Platform-specific icon (add your own icon files)
    system = platform.system()
    if system == "Windows":
        # cmd.extend(["--icon", "assets/icon.ico"])
        pass
    elif system == "Darwin":
        # cmd.extend(["--icon", "assets/icon.icns"])
        pass

    cmd.append("main.py")

    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}\n")

    subprocess.check_call(cmd)

    print(f"\nBuild complete! Output in dist/{args.name}")


if __name__ == "__main__":
    main()
