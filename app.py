from flask import Flask, render_template, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

def clean_youtube_url(url):
    """Extract video ID from YouTube URLs."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return f"https://www.youtube.com/watch?v={match.group(1)}" if match else None

def get_video_info(youtube_url):
    """ Fetch video and audio URLs """
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio,bestvideo',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

            video_url = None
            audio_url = None

            for fmt in info['formats']:
                if fmt.get('vcodec') and fmt['vcodec'] != 'none':
                    video_url = fmt['url']
                if fmt.get('acodec') and fmt['acodec'] != 'none':
                    audio_url = fmt['url']

            return {
                'title': info.get('title', 'Unknown Title'),
                'video_url': video_url,
                'audio_url': audio_url
            }
    except yt_dlp.utils.DownloadError as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video():
    data = request.json
    youtube_url = clean_youtube_url(data.get("url"))

    if not youtube_url:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        video_info = get_video_info(youtube_url)
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
