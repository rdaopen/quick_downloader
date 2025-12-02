@echo off
echo ================================================
echo  Bundling Quick Media Downloader Installer
echo ================================================
echo.

REM Check if build exists
if exist "dist\QuickDownloader\QuickDownloader.exe" goto BuildFound
echo Error: Build not found!
echo Please run build.bat first to create the executable.
pause
exit /b 1

:BuildFound
REM Check for Inno Setup Compiler
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" goto CompilerFound

echo Error: Inno Setup Compiler not found at:
echo %ISCC%
echo Please install Inno Setup 6 or update the path in this script.
pause
exit /b 1

:CompilerFound
echo Found Inno Setup Compiler.
echo Compiling QuickDownloader.iss...
"%ISCC%" QuickDownloader.iss

if %errorlevel% equ 0 goto BundleSuccess

echo.
echo ================================================
echo  BUNDLE FAILED!
echo ================================================
echo.
goto End

:BundleSuccess
echo.
echo ================================================
echo  BUNDLE SUCCESSFUL!
echo ================================================
echo.
echo Installer created successfully.

:End
pause
