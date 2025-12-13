import sys
import os
import mimetypes

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """Get the user data directory for the application"""
    app_data = os.getenv('LOCALAPPDATA')
    if not app_data:
        app_data = os.path.expanduser("~")
    
    data_dir = os.path.join(app_data, 'QuickDownloader')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def detect_download_type(url):
    """
    Intelligently detect if URL should be handled as Media (yt-dlp) or File (Generic).
    Returns: 'Media' or 'File'
    """
    url = url.lower()
    
    # Common File Extensions that are definitely NOT media streams usually
    file_exts = [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.iso', 
        '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
        '.jpg', '.png', '.gif', '.bmp', '.svg', '.webp' # Images are files
    ]
    
    # If URL ends with these, it's likely a direct file
    if any(url.split('?')[0].endswith(ext) for ext in file_exts):
        return 'File'
    
    # Verify if it's a known Media site (fast check)
    media_domains = ['youtube.com', 'youtu.be', 'twitch.tv', 'vimeo.com', 'dailymotion.com', 'soundcloud.com', 'tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com', 'x.com']
    if any(domain in url for domain in media_domains):
        return 'Media'

    # Fallback: Assume Media if it doesn't look like a file, as users likely use this for media.
    # However, if it's just a random URL, maybe 'File'? 
    # Let's stick to Media default as per previous behavior, but File if extension matches.
    return 'Media'

def detect_category(filename, media_type=None):
    """
    Categorize file based on extension and media context.
    Returns: 'Video', 'Audio', 'Playlist', 'Document', 'Program', 'Compressed', 'Other'
    """
    if media_type == 'Playlist':
        return 'Playlist'
        
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.mp4', '.mkv', '.webm', '.flv', '.avi', '.mov', '.wmv']:
        return 'Video'
    if ext in ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus']:
        return 'Audio'
    if ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.bz2']:
        return 'Compressed'
    if ext in ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.bat', '.sh']:
        return 'Program'
    if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.csv']:
        return 'Document'
        
    # Fallback based on media_type hint from downloader (e.g. forced Audio format)
    if media_type == 'Audio': return 'Audio'
    if media_type == 'Video': return 'Video'
    
    return 'Other'
