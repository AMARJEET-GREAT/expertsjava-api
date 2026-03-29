@app.route('/fetch', methods=['GET'])
def fetch():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    # --- Dynamic Referer & User-Agent Logic ---
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    
    referer = "https://www.google.com/"
    if "pinterest" in video_url:
        referer = "https://www.pinterest.com/"
    elif "instagram" in video_url:
        referer = "https://www.instagram.com/"
    elif "tiktok" in video_url:
        referer = "https://www.tiktok.com/"
    elif "facebook" in video_url or "fb.watch" in video_url:
        referer = "https://www.facebook.com/"
    elif "moj" in video_url:
        referer = "https://mojapp.in/"
    elif "youtube" in video_url or "youtu.be" in video_url:
        referer = "https://www.youtube.com/"
    elif "twitter" in video_url or "x.com" in video_url:
        referer = "https://twitter.com/"

    ydl_opts = {
        # Format selection optimized for both quality and speed
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'force_generic_extractor': False,
        'nocheckcertificate': True,
        'user_agent': user_agent,
        'referer': referer,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # Compatibility settings for tough sites like Moj/Josh/TikTok
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web']},
            'instagram': {'check_version': False},
        },
        # Ignore errors to try and get at least something
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info calls the scrapers
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({"status": "error", "message": "Could not extract info"}), 404

            # Best download URL dhoondhne ka logic
            download_url = None
            
            # 1. Direct URL check
            if 'url' in info:
                download_url = info['url']
            # 2. Formats list check (sabse best quality wala format)
            elif 'formats' in info:
                # Filter for formats that have a direct URL and are likely MP4
                valid_formats = [f for f in info['formats'] if f.get('url')]
                if valid_formats:
                    # Last format usually best quality
                    download_url = valid_formats[-1]['url']

            title = info.get('title', 'Video Downloader')
            thumbnail = info.get('thumbnail', '')

            if not download_url:
                return jsonify({"status": "error", "message": "Direct download link missing"}), 404

            return jsonify({
                "status": "success",
                "title": title,
                "download_url": download_url,
                "thumbnail": thumbnail,
                "platform": info.get('extractor_key', 'Generic')
            })
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500
