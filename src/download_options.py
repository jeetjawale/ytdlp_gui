import os


def build_ydl_opts(item, default_output_dir: str) -> dict:
    output_dir = item.output_dir or default_output_dir

    template = item.filename_template or "%(title)s.%(ext)s"
    opts = {
        "outtmpl": os.path.join(output_dir, template),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": False,
    }

    ext = item.ext
    codec = item.codec

    if item.format_id:
        opts["format"] = item.format_id
    elif item.audio_only:
        opts["format"] = f"bestaudio[ext={ext}]/bestaudio/best" if ext else "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": item.audio_format,
                "preferredquality": item.audio_quality,
            }
        ]
    else:
        video_filter = "bestvideo"
        if ext:
            video_filter += f"[ext={ext}]"
        if codec:
            video_filter += f"[vcodec={codec}]"

        audio_filter = f"bestaudio[ext={ext}]" if ext else "bestaudio"

        if item.quality == "best":
            opts["format"] = f"{video_filter}+{audio_filter}/best"
        elif item.quality == "worst":
            opts["format"] = "worst"
        else:
            height = item.quality.replace("p", "")
            opts["format"] = (
                f"{video_filter}[height<={height}]+{audio_filter}"
                f"/best[height<={height}]/best"
            )

        opts["merge_output_format"] = ext if ext else "mp4"

    if item.write_subs:
        opts["writesubtitles"] = True
        opts["subtitleslangs"] = [lang.strip() for lang in item.subtitle_langs.split(",")]
        if item.embed_subs:
            pps = opts.get("postprocessors", [])
            pps.append({"key": "FFmpegEmbedSubtitle"})
            opts["postprocessors"] = pps

    if item.speed_limit > 0:
        opts["ratelimit"] = item.speed_limit

    if item.cookie_browser:
        opts["cookiesfrombrowser"] = (item.cookie_browser,)

    if item.sponsorblock:
        pps = opts.get("postprocessors", [])
        pps.append(
            {
                "key": "SponsorBlock",
                "categories": ["sponsor", "intro", "outro", "selfpromo", "interaction"],
            }
        )
        pps.append(
            {
                "key": "ModifyChapters",
                "remove_sponsor_segments": ["sponsor", "intro", "outro", "selfpromo", "interaction"],
            }
        )
        opts["postprocessors"] = pps

    return opts
