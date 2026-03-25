from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "ExpertsJava API is Live!"

@app.route('/fetch', methods=['GET'])
def fetch():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Video link nikalna
            download_url = info.get('url', '')
            title = info.get('title', 'Snack Video')

            return jsonify({
                "status": "success",
                "title": title,
                "download_url": download_url
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
