@echo off
echo ================================================
echo  Building Quick Media Downloader
echo ================================================
echo.

REM Activate virtual environment
call env\Scripts\activate

REM Clean previous builds
echo Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo.
echo Building executable...
pyinstaller QuickDownloader.spec --clean

REM Check if build succeeded
if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo  BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your executable is located at:
    echo dist\QuickDownloader\QuickDownloader.exe
    echo.
) else (
    echo.
    echo ================================================
    echo  BUILD FAILED!
    echo ================================================
    echo.
)

pause
