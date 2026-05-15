# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project uses SemVer.

## [Unreleased]

## [0.1.2] - 2026-05-14

### Added

- Local integration test flow using `scripts/integration_test.env`
- `make check`
- `make integration-test`

### Changed

- Integration test now validates required values, rejects placeholders, and
  requires explicit terminal confirmation before calling the real API
- `make package` now cleans first
- `make clean` also removes cache directories and `__pycache__`

## [0.1.1] - 2026-05-06

### Added

- Automated `make release` flow
- GitHub Actions CI and release workflows
- Project docs and OpenAPI contract

### Changed

- CI no longer runs redundantly on release pushes to `main`

## [0.1.0] - 2026-05-06

### Added

- Initial Python SDK for `w_create_shipping`
- Request models and validation
- Unit tests
- Packaging setup
