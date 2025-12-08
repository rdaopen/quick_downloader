# Quick Media Downloader

A modern, feature-rich Windows application for downloading videos and audio using yt-dlp with a sleek CustomTkinter UI.

## Key highlights
- **High Quality Downloads**: Support for 4K, 1080p, and other resolutions.
- **Audio Extraction**: Convert videos to high-quality MP3s (up to 320 kbps) — requires ffmpeg.
- **Playlist Support**: Download entire playlists.
- **Chrome Extension**: Companion extension available at https://github.com/rdaopen/qmd_extension to send links from your browser to the app (uses local HTTP server).
- **Modern UI**: Dark-themed interface using CustomTkinter.
- **History Tracking**: Keep track of downloads, play them, open their location, select & delete multiple history items, or clear history.
- **Smart Clipboard**: Right-click to paste URLs into the Add Download dialog.
- **Partial-download cleanup**: The downloader tries to remove .part / temporary files on error or cancel.
- **System Tray**: Minimizes to tray (pystray + Pillow).

## Important prerequisites
- Python 3.8+ recommended.
- ffmpeg is required for audio extraction and some formats. The ffmpeg binaries are intentionally gitignored due to file size — you must download and place them yourself (see instructions below).

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/rdaopen/quick_downloader.git
    cd quick_downloader
    ```

2. **Create a virtual environment (optional but recommended)**
    - **Windows:**
      ```bash
      python -m venv env
      .\env\Scripts\activate
      ```
    - **macOS / Linux:**
      ```bash
      python3 -m venv env
      source env/bin/activate
      ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    requirements.txt includes customtkinter, yt-dlp, pystray, Pillow, etc.

### ffmpeg (manual step)
- Download ffmpeg from https://ffmpeg.org/ or a trusted build provider.
- Place the ffmpeg binary (or ffmpeg.exe on Windows) in one of:
  - The application folder so `resource_path("ffmpeg")` can find it, or
  - Any folder on your system PATH.
- Note: ffmpeg files are not included in this repo due to size; the app checks for ffmpeg at startup and will function with reduced capabilities if it is missing.

## Usage

Run the application:
```bash
python main.py
