import os
import tempfile
import unittest

from src.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_corrupt_json_resets_data_and_sets_error_flag(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            with open(settings_path, "w", encoding="utf-8") as handle:
                handle.write("{bad json")

            settings = Settings(path=settings_path)

            self.assertIsNone(settings.get("missing"))
            self.assertIsNotNone(settings.last_error)


if __name__ == "__main__":
    unittest.main()
