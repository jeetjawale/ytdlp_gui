import os
import tempfile
import unittest

from src.download_options import build_ydl_opts
from src.models import DownloadItem


class DownloadOptionsTests(unittest.TestCase):
    def test_video_download_uses_item_quality_ext_and_codec(self):
        item = DownloadItem(quality="1080p", ext="webm", codec="vp9")

        opts = build_ydl_opts(item, "/tmp/downloads")

        self.assertEqual(
            opts["format"],
            "bestvideo[ext=webm][vcodec=vp9][height<=1080]+bestaudio[ext=webm]/best[height<=1080]/best",
        )
        self.assertEqual(opts["merge_output_format"], "webm")

    def test_audio_download_adds_extract_audio_postprocessor(self):
        item = DownloadItem(
            audio_only=True,
            ext="m4a",
            audio_format="mp3",
            audio_quality="192",
        )

        opts = build_ydl_opts(item, "/tmp/downloads")

        self.assertEqual(opts["format"], "bestaudio[ext=m4a]/bestaudio/best")
        self.assertEqual(
            opts["postprocessors"][0],
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
        )

    def test_manual_format_overrides_auto_filters(self):
        item = DownloadItem(
            format_id="137+140",
            quality="720p",
            ext="mp4",
            codec="h264",
        )

        opts = build_ydl_opts(item, "/tmp/downloads")

        self.assertEqual(opts["format"], "137+140")

    def test_build_ydl_opts_does_not_create_output_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "downloads")
            item = DownloadItem(output_dir=output_dir)

            opts = build_ydl_opts(item, "/tmp/downloads")

            self.assertEqual(opts["outtmpl"], os.path.join(output_dir, "%(title)s.%(ext)s"))
            self.assertFalse(os.path.exists(output_dir))

    def test_subtitles_cookie_browser_and_sponsorblock_are_preserved(self):
        item = DownloadItem(
            write_subs=True,
            embed_subs=True,
            subtitle_langs="en,fr",
            cookie_browser="firefox",
            sponsorblock=True,
        )

        opts = build_ydl_opts(item, "/tmp/downloads")

        self.assertTrue(opts["writesubtitles"])
        self.assertEqual(opts["subtitleslangs"], ["en", "fr"])
        self.assertEqual(opts["cookiesfrombrowser"], ("firefox",))
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertIn("FFmpegEmbedSubtitle", keys)
        self.assertIn("SponsorBlock", keys)
        self.assertIn("ModifyChapters", keys)

    def test_speed_limit_sets_ratelimit(self):
        item = DownloadItem(speed_limit=1024)

        opts = build_ydl_opts(item, "/tmp/downloads")

        self.assertEqual(opts["ratelimit"], 1024)


if __name__ == "__main__":
    unittest.main()
