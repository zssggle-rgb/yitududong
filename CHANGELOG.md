# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0.1] - 2026-05-02

### Added

- First release: complete document-to-image pipeline (PDF/DOCX upload, text extraction, policy long-image rendering)

## [0.1.0.0] - 2026-05-02

### Added

- Document upload and text extraction module supporting PDF and DOCX formats
- PNG preview and download support for rendered documents
- Document validation with safe filename generation
- CI/CD pipeline for automated testing (GitHub Actions)
- Comprehensive test suite for core modules (extract, validate, render, main)

### Changed

- Font fallback chain improved for Linux environments
- PDF extraction accuracy for titles and key points
- CSS hex color handling in static frontend

### Fixed

- Empty PDF handling in text extraction
- Missing parenthesis in index.html JavaScript
- Empty stripped line guards in extractors
- Reference PDF tests skipped gracefully in CI with 404 handling
- httpx added to test dependencies for starlette testclient

### Infrastructure

- Project requirements documentation (requirements.md)
- pytest configuration with proper test discovery
- .gitignore for Python and Node artifacts
