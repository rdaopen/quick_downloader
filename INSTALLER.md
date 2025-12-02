# Creating a Windows Installer for Quick Media Downloader

## Prerequisites

1. **Build the executable first**
   ```batch
   build.bat
   ```
   This creates `dist\QuickDownloader\QuickDownloader.exe` and all dependencies.

2. **Download Inno Setup**
   - Visit: https://jrsoftware.org/isinfo.php
   - Download and install Inno Setup (free)
   - Use the latest stable version (currently 6.x)

## Building the Installer

### Method 1: Using Inno Setup GUI (Easiest)

1. **Open Inno Setup Compiler**
   - Launch "Inno Setup Compiler" from Start Menu

2. **Open the Script**
   - File → Open → Select `QuickDownloader.iss`

3. **Compile**
   - Build → Compile (or press Ctrl+F9)
   - Wait for compilation to complete

4. **Find Your Installer**
   - The installer will be created in `installer_output\`
   - Filename: `QuickDownloader_Setup_v1.0.0.exe`

### Method 2: Command Line

```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" QuickDownloader.iss
```

## What the Installer Does

When users run the installer, it will:
- ✅ Install to `C:\Program Files\Quick Media Downloader`
- ✅ Create a Start Menu shortcut
- ✅ Create a Desktop shortcut (checked by default)
- ✅ Add uninstall entry in Windows Settings
- ✅ Use your app icon throughout
- ✅ Optionally launch the app after installation

## Customizing the Installer

### Change App Information

Edit `QuickDownloader.iss` and modify these lines:

```iss
#define MyAppPublisher "Your Name"
#define MyAppURL "https://yourwebsite.com"
```

### Change Version

Update the version number:
```iss
#define MyAppVersion "1.0.0"
```

### Add License Agreement

Add a license file section:
```iss
[Setup]
LicenseFile=LICENSE.txt
```

Then create a `LICENSE.txt` file in the project root.

## Distribution

After building the installer:

1. **Single File Distribution**
   - Share `QuickDownloader_Setup_v1.0.0.exe`
   - Users download and run it
   - That's it!

2. **Installer Size**
   - Approximately 50-60 MB (includes all dependencies)
   - Compressed with LZMA2 for smaller size

## Troubleshooting

### Compilation Errors

**Error: Cannot find file**
- Make sure you've built the executable first (`build.bat`)
- Check that `dist\QuickDownloader\` exists

**Error: Icon file not found**
- Verify `icon.ico` exists in the project root

### Installer Won't Run

**SmartScreen Warning**
- Normal for unsigned apps
- Click "More info" → "Run anyway"
- To avoid: Code sign your installer (requires certificate)

## Advanced: Code Signing (Optional)

To remove SmartScreen warnings:

1. Purchase a code signing certificate (~$100-300/year)
2. Add to Inno Setup script:
   ```iss
   SignTool=signtool sign /f "path\to\certificate.pfx" /p "password" $f
   ```

This is optional but recommended for professional distribution.

## Building from Scratch

Complete build process:
```batch
# 1. Build the executable
build.bat

# 2. Build the installer (in Inno Setup)
# Or use command line:
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" QuickDownloader.iss
```

Your installer is ready in `installer_output\QuickDownloader_Setup_v1.0.0.exe`!
