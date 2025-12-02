# Quick Media Downloader

A modern, feature-rich Windows application for downloading videos and audio from YouTube and other platforms. Built with Python, CustomTkinter, and yt-dlp.

## Features

- **High Quality Downloads**: Support for 4K, 1080p, and other resolutions.
- **Audio Extraction**: Convert videos to high-quality MP3s (up to 320kbps).
- **Playlist Support**: Download entire playlists with a single click.
- **Modern UI**: Sleek, dark-themed interface using CustomTkinter.
- **History Tracking**: Keep track of your downloads, play them, or open their location directly from the app.
- **Smart Clipboard**: Right-click to paste URLs instantly.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/quick_downloader.git
    cd quick_downloader
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv env
    .\env\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **FFmpeg Setup:**
    - Ensure `ffmpeg` is installed and added to your system PATH, or place the `ffmpeg.exe` and `ffprobe.exe` binaries in an `ffmpeg` folder within the project directory.

## Usage

Run the application:
```bash
python main.py
```

1.  Paste a media URL (YouTube, etc.).
2.  Select your desired format (Video/Audio) and quality.
3.  Choose a download location (defaults to `Downloads/quick_downloader`).
4.  Click **START DOWNLOAD**.

## Building the Executable

To create a standalone `.exe` file:

1.  Ensure `pyinstaller` is installed (`pip install pyinstaller`).
2.  Run the build script:
    ```bash
    build.bat
    ```
    Or manually:
    ```bash
    pyinstaller QuickDownloader.spec
    ```
3.  The executable will be in the `dist` folder.

## License

This project is released under the [Unlicense](LICENSE). Public Domain.
