#!/usr/bin/env python3
"""YT-DLP GUI — A cross-platform desktop GUI for yt-dlp."""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YT-DLP GUI")
    app.setOrganizationName("ytdlp-gui")

    # Keep app alive when window is hidden to tray
    app.setQuitOnLastWindowClosed(False)

    # Use a clean sans-serif font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
