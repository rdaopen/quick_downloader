@echo off
echo Cleaning previous build files...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Output rmdir /s /q Output

REM Check if clean was successful
if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo  CLEAN SUCCESSFUL!
    echo ================================================
    echo.
) else (
    echo.
    echo ================================================
    echo  CLEAN FAILED!
    echo ================================================
    echo.
)

pause