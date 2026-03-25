@app.route('/fetch', methods=['GET'])
def fetch():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    # Dynamic Referer Logic
    referer = "https://www.google.com/" # Default
    if "pinterest" in video_url:
        referer = "https://www.pinterest.com/"
    elif "instagram" in video_url:
        referer = "https://www.instagram.com/"
    elif "tiktok" in video_url:
        referer = "https://www.tiktok.com/"
    elif "facebook" in video_url:
        referer = "https://www.facebook.com/"
    elif "moj" in video_url:
        referer = "https://mojapp.in/"

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'force_generic_extractor': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'referer': referer, # Ab ye apne aap change hoga
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url', '')
            title = info.get('title', 'Video Downloader')

            return jsonify({
                "status": "success",
                "title": title,
                "download_url": download_url
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
