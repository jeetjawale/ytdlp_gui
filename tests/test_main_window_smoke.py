import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from src.main_window import MainWindow


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_window_constructs_without_debug_prints_or_missing_browse_button(self):
        with patch.object(MainWindow, "_ffmpeg_installed", return_value=True):
            with patch("builtins.print") as mock_print:
                window = MainWindow()

        self.assertIsNotNone(window.format_panel.browse_btn)
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
