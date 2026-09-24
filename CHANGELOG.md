# Changelog

All notable changes to Flask-Forge will be documented in this file.

## 0.1.0 - Alpha

### Added

- Standard installable Python package under `src/flask_forge`.
- `Forge` application wrapper.
- Database/ORM helpers.
- Authentication and authorization helpers.
- Form validation.
- In-memory cache with TTL and LRU behavior.
- Security, HTTP, response, session/cookie, admin, and testing utilities.
- Automated tests on Python 3.10, 3.11, and 3.12.
- Package build validation in GitHub Actions.
- TestPyPI and PyPI Trusted Publishing workflows.

### Fixed

- Package-relative imports for installed use.
- Cache `setting`/`set` alias behavior.
- Default GET behavior for `route_api`.
- Several small packaging/runtime issues discovered while preparing the first distribution.
