# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project uses SemVer.

## [Unreleased]

## [0.1.4] - 2026-05-15

### Added

- Explicit support for `shipping.email`, `shipping.company`,
  `shipping.entrance`, and `shipping.floor`
- `extra_fields` pass-through support on `ShippingDetails`, `Order`, and
  `Origin`

### Changed

- README and SDK docs now document broader field coverage based on the
  Datalogics WooCommerce plugin behavior
- Integration test script and example env now support the new optional shipping
  fields and JSON extra-field payloads

## [0.1.3] - 2026-05-15

### Added

- `LICENSE`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- package metadata for GitHub URLs

### Changed

- README now states this is an independent/community SDK, not an official
  Datalogics SDK
- `release.yml` now publishes only on pushed `v*` tags
- CI now uses concurrency, timeouts, and builds the package once on Python 3.13
- security guidance now points upstream Datalogics platform/account issues to
  the Datalogics support ticket page

## [0.1.2] - 2026-05-14

### Added

- Local integration test flow using `scripts/integration_test.env`
- `scripts/integration_test.env.example`
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
