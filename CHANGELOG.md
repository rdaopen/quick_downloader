# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Improved UI by replacing the direct URL input field with a dedicated "Add Download" button and dialog for better usability.

### Fixed

- Fixed persistence issue where history and settings were not saved in release builds by moving storage to `%LOCALAPPDATA%\QuickDownloader`.
- Fixed missing icons in release builds by including the `icons` folder in the PyInstaller spec.
