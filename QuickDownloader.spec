# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define all data files to include
added_files = [
    ('icon.ico', '.'),  # Include icon in root of dist folder
    ('ffmpeg', 'ffmpeg'),  # Include entire ffmpeg folder
]

# Analysis: specify all imports and data files
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        'mutagen',
        'brotli',
        'websockets',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ: create compressed archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE: create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QuickDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Set app icon
)

# COLLECT: gather all files into dist folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QuickDownloader',
)
