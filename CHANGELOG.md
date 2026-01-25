# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-25

### Changed

- **BREAKING**: Minimum Python version is now 3.10 (previously 3.6)
- Migrated build system from `setup.py` to `pyproject.toml`
- Replaced Travis CI with GitHub Actions
- Replaced Black/Flake8 with Ruff for linting and formatting

### Added

- Full type annotations with `py.typed` marker (PEP 561)
- Support for Python 3.10, 3.11, 3.12, 3.13, and 3.14
- Dependabot configuration for automated dependency updates
- PyPI trusted publishing via OIDC

### Fixed

- Mutable default arguments in `GelfFormatter.__init__`
- Python 2 compatibility code removed
- `taskName` attribute (Python 3.12+) now properly excluded from output

### Removed

- Support for Python 2.7, 3.5, 3.6, 3.7, 3.8, 3.9
- Legacy `setup.py`, `setup.cfg`, `MANIFEST.in`, `Pipfile`, `tox.ini`

## [0.2.1] - 2021-06-03

### Added

- Support for Python 3.9

### Removed

- Support for Python 2.7 and 3.5

## [0.2.0] - 2019-05-09

### Added

- `ignored_attrs` parameter to filter out specific extra fields
- `allowed_reserved_attrs` parameter to include LogRecord attributes

## [0.1.0] - 2019-04-29

### Added

- Initial release
- GELF 1.1 compliant formatter
- Support for additional fields via `extra` keyword
- Exception traceback formatting
