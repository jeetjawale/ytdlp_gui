import unittest

from src.models import DownloadItem


class HistoryServiceTests(unittest.TestCase):
    def test_history_entry_contains_operational_fields(self):
        from src.history_service import download_item_to_history_entry

        item = DownloadItem(
            title="Video",
            url="https://example.com",
            audio_only=True,
            audio_format="mp3",
            output_dir="/tmp/out",
            output_path="/tmp/out/file.mp3",
            quality="best",
        )

        entry = download_item_to_history_entry(item)

        self.assertEqual(entry["output_path"], "/tmp/out/file.mp3")
        self.assertEqual(entry["url"], "https://example.com")

    def test_history_is_capped_to_latest_200_entries(self):
        from src.history_service import clamp_history

        entries = [{"title": str(i)} for i in range(250)]

        clamped = clamp_history(entries, limit=200)

        self.assertEqual(len(clamped), 200)
        self.assertEqual(clamped[0]["title"], "50")


if __name__ == "__main__":
    unittest.main()
