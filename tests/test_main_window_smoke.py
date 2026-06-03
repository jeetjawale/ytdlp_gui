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

    def test_toolbar_uses_stable_text_labels(self):
        with patch.object(MainWindow, "_ffmpeg_installed", return_value=True):
            window = MainWindow()

        self.assertEqual(window.paste_btn.text(), "Paste")
        self.assertEqual(window.fetch_btn.text(), "Fetch Info")
        self.assertEqual(window.batch_btn.text(), "Batch")
        self.assertIn(window.theme_btn.text(), {"Dark", "Light"})
        self.assertEqual(window.add_queue_btn.text(), "Add to Queue")
        self.assertEqual(window.tabs.tabText(0), "Downloads (0)")
        self.assertEqual(window.tabs.tabText(1), "History (0)")


if __name__ == "__main__":
    unittest.main()
