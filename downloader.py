import yt_dlp
import os
import threading
import re

class MediaDownloader:
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg_path = ffmpeg_path
        self._cancel_requested = False
        self.download_thread = None

    def cancel(self):
        self._cancel_requested = True

    def _progress_hook(self, d, progress_callback):
        if self._cancel_requested:
            raise Exception("Download cancelled by user")
        
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                
                if total:
                    progress = downloaded / total
                else:
                    progress = 0
                
                def strip_ansi(text):
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    return ansi_escape.sub('', text)

                # Use yt-dlp's formatted strings if available, otherwise fallback
                speed = d.get('_speed_str', 'N/A')
                if speed == 'N/A' and d.get('speed'):
                    speed = f"{d['speed'] / 1024 / 1024:.2f} MiB/s"
                else:
                    speed = strip_ansi(speed)

                eta = d.get('_eta_str', 'N/A')
                if eta == 'N/A' and d.get('eta'):
                    eta = f"{d['eta']}s"
                else:
                    eta = strip_ansi(eta)
                
                if progress_callback:
                    progress_callback(progress, speed, eta)
            except Exception as e:
                print(f"Progress Error: {e}")
                pass

    def download(self, url, options, output_path, quality, format_type, progress_callback=None, completion_callback=None, error_callback=None):
        self._cancel_requested = False
        
        def run():
            ydl_opts = options.copy()
            
            # Configure ffmpeg location if provided
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            
            # Output Path
            if output_path:
                ydl_opts['paths'] = {'home': output_path}
            
            # Quality Configuration
            if format_type == "Video":
                if quality == "Best":
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                elif quality == "4K":
                    ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best'
                elif quality == "1080p":
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
                elif quality == "720p":
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
                elif quality == "480p":
                    ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'
                ydl_opts['merge_output_format'] = 'mp4'
            
            elif format_type == "Audio":
                ydl_opts['format'] = 'bestaudio/best'
                audio_quality = '192' # Default
                if quality == "Best":
                    audio_quality = '320'
                elif quality == "High (320kbps)":
                    audio_quality = '320'
                elif quality == "Medium (192kbps)":
                    audio_quality = '192'
                elif quality == "Low (128kbps)":
                    audio_quality = '128'
                
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality,
                }]

            # Add progress hook
            ydl_opts['progress_hooks'] = [lambda d: self._progress_hook(d, progress_callback)]
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'Unknown Title')
                    
                if completion_callback:
                    completion_callback(title)
            except Exception as e:
                if "Download cancelled by user" in str(e):
                    if error_callback:
                        error_callback("Cancelled")
                else:
                    if error_callback:
                        error_callback(str(e))

        self.download_thread = threading.Thread(target=run)
        self.download_thread.start()
