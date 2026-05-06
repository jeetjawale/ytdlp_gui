import unittest


class ErrorUtilsTests(unittest.TestCase):
    def test_ffmpeg_error_is_classified(self):
        from src.error_utils import classify_error

        kind, message = classify_error("ffmpeg not found")

        self.assertEqual(kind, "ffmpeg")
        self.assertIn("FFmpeg", message)

    def test_network_error_is_classified(self):
        from src.error_utils import classify_error

        kind, message = classify_error("Temporary failure in name resolution")

        self.assertEqual(kind, "network")
        self.assertIn("Network", message)


if __name__ == "__main__":
    unittest.main()
