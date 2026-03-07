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

    # Handle Ctrl+C (SIGINT) to quit app
    import signal
    signal.signal(signal.SIGINT, lambda *args: app.quit())

    # QTimer to allow Python signal handling (Ctrl+C)
    from PyQt6.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)

    # Quit app when window is closed
    app.setQuitOnLastWindowClosed(True)

    # Use a clean sans-serif font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
