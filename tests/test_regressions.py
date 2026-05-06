import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from src.main_window import MainWindow
from src.models import DownloadItem
from src.widgets import FormatPanel


class FormatPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_manual_format_id_defaults_to_empty_string(self):
        panel = FormatPanel()
        self.assertEqual(panel.get_selected_format_id(), "")

class MainWindowIntegrationTests(unittest.TestCase):
    def test_build_ydl_opts_delegates_to_helper_with_item_and_default_downloads_dir(self):
        window = MainWindow.__new__(MainWindow)
        item = DownloadItem(output_dir="", quality="1080p", ext="webm", codec="vp9")
        expected = {"format": "delegated"}

        with patch("src.main_window.build_ydl_opts", return_value=expected) as mock_build:
            opts = MainWindow._build_ydl_opts(window, item)

        self.assertIs(opts, expected)
        mock_build.assert_called_once_with(
            item,
            os.path.expanduser("~/Downloads"),
        )


if __name__ == "__main__":
    unittest.main()
