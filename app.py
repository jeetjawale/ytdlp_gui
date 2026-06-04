import os
from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YT-DLP API</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>YT-DLP API</h1>
    <p>This is the lightweight web service for YT-DLP GUI.</p>
    <h3>Endpoints</h3>
    <ul>
        <li><code>/health</code> - Health check</li>
        <li><code>/download-info?url=&lt;youtube_url&gt;</code> - Get video metadata</li>
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/download-info")
def download_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
    }
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            sanitized = ydl.sanitize_info(info)
            
            return jsonify({
                "title": sanitized.get("title"),
                "uploader": sanitized.get("uploader") or sanitized.get("channel"),
                "duration": sanitized.get("duration")
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
