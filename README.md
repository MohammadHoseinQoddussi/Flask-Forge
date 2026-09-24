# Flask-Forge

Flask-Forge is an experimental **Barsa** toolkit that builds higher-level application, database, authentication, validation, caching, security, HTTP, state, admin, and testing utilities on top of Flask.

> Status: **0.1.0 alpha**. The API is still evolving and should be tested carefully before production use.

## Installation

Once the package is published on PyPI:

```bash
pip install flask-forge
```

For MySQL support:

```bash
pip install "flask-forge[mysql]"
```

For local development from this repository:

```bash
python -m pip install -e ".[test]"
```

## Quick start

```python
from flask_forge import Forge

app = Forge(__name__)

@app.route("/")
def home(request):
    return "Hello from Flask-Forge"

if __name__ == "__main__":
    app.run(debug=True)
```

## Public API

The top-level package currently exposes:

```python
from flask_forge import (
    Admin,
    Auth,
    Cache,
    Database,
    Forge,
    Form,
    TestClient,
)
```

## Core application: `Forge`

`Forge` owns an underlying `flask.Flask` application and provides convenience behavior around routing, CSRF protection, request hooks, rate limiting, and startup.

```python
app = Forge(
    name="my-app",
    secret_key="optional-secret",
)
```

### Routing

```python
@app.route("/users", methods=["GET"])
def users(request):
    return "users"
```

API routes can be registered with `route_api(...)`; these routes are exempted from CSRF protection.

```python
@app.route_api("/api/status")
def status(request):
    return {"status": "ok"}
```

## Database / ORM

`Database` wraps Flask-SQLAlchemy and includes helpers for common data operations.

```python
from flask_forge import Database, Forge

app = Forge(__name__)
database = Database(app)
db = database.connect(type="sqlite", name="database.db")
```

Supported connection approaches include:

- SQLite
- MySQL via the optional `mysql` extra
- direct SQLAlchemy connection URLs

Current convenience methods include:

- `create_all()` / `drop_all()`
- `get()` / `get_first()` / `get_all()`
- `find()` / `count()` / `exists()`
- `add()` / `add_all()`
- `update()` / `delete()` / `delete_all()`
- `select()` / `limit()` / `order()`
- relationship helpers
- `commit()` / `rollback()`
- transactional `session_scope()`

The current automatic migration helper uses Alembic APIs and remains experimental.

## Authentication

`Auth` provides lightweight registration, login, logout, session-based authentication, and in-memory role helpers.

```python
from flask_forge import Auth

auth = Auth(database)
```

Role storage is currently in-memory and is not intended as a persistent production authorization backend.

## Form validation

`Form` supports required data, type, length, and number checks.

```python
from flask_forge import Form

form = Form({"username": "ali", "age": 20})

valid = form.validate(
    minimum={"string": 2, "number": 1},
    maximum={"string": 30, "number": 120},
    types={"username": str, "age": int},
    datas=("username", "age"),
)
```

## Cache

`Cache` is an in-memory cache with optional TTL and LRU eviction.

```python
from flask_forge import Cache

cache = Cache(max_size=100)
cache.set("key", "value", ttl=60)
value = cache.get("key")
```

This cache is process-local and should not be treated as a shared production cache in multi-process deployments.

## Security utilities

The package includes helpers for:

- HTML escaping
- Werkzeug password hashing and verification
- simple JSON validation
- in-memory rate limiting
- sanitized file uploads with extension and size limits

## HTTP and response helpers

Flask-Forge includes small wrappers for outbound HTTP requests and common Flask responses such as redirects, JSON responses, file serving, URL generation, and template rendering.

## State helpers

Session, cookie, and email helpers are available inside the package. Email credentials should be supplied through secure application configuration and should never be committed to source control.

## Admin helpers

`Admin` provides small helpers for pagination and common database operations.

## Test client

`TestClient` wraps Flask's built-in test client for common request, cookie, session, and request-context operations.

## Development

Install the project with development dependencies:

```bash
python -m pip install -e ".[test]"
```

Run tests:

```bash
pytest -q
```

Build the package:

```bash
python -m pip install --upgrade build
python -m build
```

Successful builds produce a wheel and source distribution under `dist/`.

## Release process

The repository includes GitHub Actions workflows for:

1. running tests on supported Python versions,
2. validating the package build,
3. publishing manually to TestPyPI,
4. publishing GitHub Releases to PyPI through Trusted Publishing.

Before using either publishing workflow, configure the corresponding **Trusted Publisher** on TestPyPI/PyPI for this repository and workflow environment.

## Project structure

```text
Flask-Forge/
├── src/
│   └── flask_forge/
│       ├── __init__.py
│       ├── core.py
│       ├── auth.py
│       ├── orm.py
│       ├── form.py
│       ├── cache.py
│       ├── admin.py
│       ├── security.py
│       ├── state.py
│       ├── responses.py
│       ├── http_request.py
│       ├── test_client.py
│       └── exceptions.py
├── tests/
├── .github/workflows/
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

## Versioning

The first packaged release is planned as `0.1.0`. Flask-Forge follows semantic-style versioning during its alpha development, with breaking API changes possible before `1.0.0`.

## License

No open-source license has been selected yet. A license should be chosen before the first public PyPI release if redistribution and reuse terms are intended to be granted.
