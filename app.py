
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import re
import os
import subprocess

app = Flask(__name__)

def clean_youtube_url(url):
    """Extract video ID from YouTube URLs."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return f"https://www.youtube.com/watch?v={match.group(1)}" if match else None

def get_video_info(youtube_url):
    """ Fetch video qualities and separate audio URL """
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio,bestvideo',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)

        formats = []
        audio_url = None
        video_url = None

        for fmt in info['formats']:
            if fmt.get('format_note') and fmt.get('url'):
                formats.append({
                    'format_id': fmt['format_id'],
                    'format_note': fmt['format_note'],
                    'url': fmt['url']
                })
            
            # Pick the best audio stream
            if fmt.get('acodec') and fmt['acodec'] != 'none':
                audio_url = fmt['url']
            
            # Pick the best video stream
            if fmt.get('vcodec') and fmt['vcodec'] != 'none':
                video_url = fmt['url']

        return {
            'title': info['title'],
            'formats': formats,
            'video_url': video_url,
            'audio_url': audio_url
        }

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

@app.route('/download_video', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")

    if not video_url or not audio_url:
        return jsonify({'error': 'Missing video or audio URL'}), 400

    video_path = "static/video.mp4"
    audio_path = "static/audio.mp4"
    output_path = "static/final_video.mp4"

    # Download video and audio separately
    os.system(f'ffmpeg -i "{video_url}" -c:v copy -y {video_path}')
    os.system(f'ffmpeg -i "{audio_url}" -c:a aac -b:a 192k -y {audio_path}')

    # Merge video and audio
    os.system(f'ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental -y {output_path}')

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

ydl_opts = {
    'cookies': 'cookies.txt',  # Pass the cookies file
    'format': 'best',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=YOUR_VIDEO_ID"])
