# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-07-05

### Added
- Added an authentication and authorization system for JSON-RPC controllers.
- Added new authorization modules in `jsonrpc_framework/controller/auth/`.
- Added authentication documentation in `docs/docs/authentication.md`.
- Added a CI checks workflow in `.github/workflows/checks.yml`.
- Added unit tests for auth scenarios in `tests/unit/auth/`.
- Added Read the Docs configuration (`.readthedocs.yaml`).

### Changed
- Extended decorators and base controller logic to support access mode and auth runtime.
- Updated OpenRPC collector integration to include method metadata.
- Updated documentation, `README.md`, and `mkdocs` configuration.
- Updated dependencies and tooling (`pyproject.toml`, `uv.lock`, `Makefile`).

### Fixed
- Fixed typing issues and `mypy` compatibility in the auth branch before release.
- Resolved merge-related conflicts and documentation/type inconsistencies.

## [0.1.0] - 2026-06-03

### Added
- First stable package release for publishing to PyPI.
- Basic JSON-RPC controller and routing infrastructure.

### Changed
- Updated and clarified the `README` and usage examples.
- Improved typing and the `jsonrpc_framework/controller/decor.py` decorator.

### Fixed
- Fixed issues in `urlpatterns` and `return` statements in early patches.

