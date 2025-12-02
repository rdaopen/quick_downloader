# Quick Media Downloader - Build Instructions

## Overview
This document explains how to build the Quick Media Downloader as a standalone Windows executable using PyInstaller.

## Prerequisites
- Python 3.x installed
- Virtual environment activated (`env\Scripts\activate`)
- All dependencies installed (see `requirements.txt` if available)

## Building the Executable

### Option 1: Using the Build Script (Recommended)
Simply run the build script:
```batch
build.bat
```

This script will:
1. Activate the virtual environment
2. Clean any previous builds
3. Run PyInstaller with the spec file
4. Display the results

### Option 2: Manual Build
1. Activate the virtual environment:
   ```batch
   env\Scripts\activate
   ```

2. Run PyInstaller:
   ```batch
   pyinstaller QuickDownloader.spec --clean
   ```

## Output Location
After a successful build, the executable and all dependencies will be in:
```
dist\QuickDownloader\QuickDownloader.exe
```

## Distribution
To distribute the application:
1. Copy the entire `dist\QuickDownloader` folder
2. Users can run `QuickDownloader.exe` directly
3. No Python installation required!

## File Structure
```
dist/QuickDownloader/
├── QuickDownloader.exe    (Main executable - 11.6 MB)
├── icon.ico               (App icon)
├── ffmpeg/                (FFmpeg binaries for media conversion)
│   ├── ffmpeg.exe
│   ├── ffprobe.exe
│   └── LICENSE
└── _internal/             (Python runtime and dependencies)
    ├── customtkinter/
    ├── yt_dlp/
    └── [other libraries]
```

## Troubleshooting

### Build Fails
- Ensure virtual environment is activated
- Check that PyInstaller is installed: `pip install pyinstaller`
- Clear build cache: delete `build/` and `dist/` folders

### Executable Won't Run
- Check antivirus isn't blocking it
- Ensure the entire `dist\QuickDownloader` folder is intact
- Run from command prompt to see error messages

### Missing Dependencies
If the app crashes on launch, add missing modules to the `hiddenimports` list in `QuickDownloader.spec`

## Spec File Configuration
The `QuickDownloader.spec` file contains:
- **Hidden imports**: customtkinter, yt_dlp, mutagen, etc.
- **Data files**: icon.ico, ffmpeg binaries
- **Console mode**: Disabled (windowed app)
- **Icon**: icon.ico

To modify the build, edit `QuickDownloader.spec` and rebuild.
