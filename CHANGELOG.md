# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow for HACS validation
- GitHub Actions workflow for hassfest validation
- GitHub Actions workflow for release automation
- bump2version configuration for version management
- Comprehensive development and release documentation in README
- Code quality checks now run on pushes to master branch

### Changed
- Synced version numbers across pyproject.toml and manifest.json (1.0.1)

## [1.0.1] - 2024-XX-XX

### Added
- Initial HACS-compatible release
- Water consumption monitoring for City4U municipalities
- Support for multiple verified municipalities
- Historical data import functionality
- Force update service
- Multi-language support (Hebrew/English)

### Fixed
- Proper handling of delayed meter reading timestamps

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Basic water consumption monitoring
- Config flow setup
- Municipality selector

[Unreleased]: https://github.com/tsvi/city4u_water_meter/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/tsvi/city4u_water_meter/releases/tag/v1.0.1
[1.0.0]: https://github.com/tsvi/city4u_water_meter/releases/tag/v1.0.0
