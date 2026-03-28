@app.route('/fetch', methods=['GET'])
def fetch():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    # --- Dynamic Referer Logic (Updated for YouTube) ---
    referer = "https://www.google.com/"
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
    elif "youtube" in video_url or "youtu.be" in video_url:
        referer = "https://www.youtube.com/"

    ydl_opts = {
        # 'best' ki jagah YouTube ke liye specific format behtar hota hai
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'force_generic_extractor': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'referer': referer,
        'nocheckcertificate': True, # Certificate errors se bachne ke liye
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        # AGAR YOUTUBE BLOCK KARE, TOH YE LINE UNCOMMENT KAREIN:
        # 'cookiefile': 'cookies.txt', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Kuch YouTube videos mein 'url' ki jagah formats ke andar link hota hai
            download_url = info.get('url') or (info.get('formats')[-1].get('url') if info.get('formats') else None)
            title = info.get('title', 'Video Downloader')

            if not download_url:
                return jsonify({"status": "error", "message": "Could not find a direct download link"}), 404

            return jsonify({
                "status": "success",
                "title": title,
                "download_url": download_url,
                "thumbnail": info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({"status": "error", "message": f"yt-dlp error: {str(e)}"}), 500
