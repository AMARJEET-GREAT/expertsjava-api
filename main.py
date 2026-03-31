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
        # Moj ke liye 'best' zyada stable hai
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': user_agent,
        'referer': referer,
        'follow_redirects': True, # Moj short links ke liye zaroori hai
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web']},
            'instagram': {'check_version': False},
        },
        'ignoreerrors': False, # Isse error ka sahi pata chalega
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({"status": "error", "message": "Could not extract info"}), 404

            # Agar link playlist ya multiple entries wala hai (aksar Moj mein hota hai)
            if 'entries' in info:
                info = info['entries'][0]

            download_url = None
            
            # 1. Sabse pehle direct 'url' check karein
            if info.get('url'):
                download_url = info['url']
            
            # 2. Agar nahi mila, toh best format dhoondhein
            elif 'formats' in info:
                # Reverse check (best quality piche hoti hai)
                for f in reversed(info['formats']):
                    if f.get('url') and (f.get('ext') == 'mp4' or 'mp4' in f.get('format', '')):
                        download_url = f['url']
                        break
                
                # Agar tab bhi nahi mila toh jo bhi best hai wo le lo
                if not download_url:
                    download_url = info['formats'][-1].get('url')

            if not download_url:
                return jsonify({"status": "error", "message": "Direct download link missing"}), 404

            return jsonify({
                "status": "success",
                "title": info.get('title', 'Video Downloader'),
                "download_url": download_url,
                "thumbnail": info.get('thumbnail', ''),
                "platform": info.get('extractor_key', 'Generic')
            })
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500
