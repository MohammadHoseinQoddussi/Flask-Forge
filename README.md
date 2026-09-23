# Flask-Forge

> An experimental Barsa Tose'e toolkit that builds higher-level application, database, authentication, validation, caching, security, HTTP, state, admin, and testing utilities on top of Flask.

## Overview

**Flask-Forge** is a **Barsa Tose'e (برسا توسعه)** project designed to extend Flask with a set of reusable higher-level utilities. Instead of replacing Flask, the project wraps and organizes common web-development tasks around Flask so a developer can create routes, connect a database, handle authentication, validate input, manage sessions and cookies, cache data, perform HTTP requests, work with common responses, upload files, and test an application with a smaller custom API.

The current repository is an **experimental library/code toolkit**, not yet a packaged stable Python distribution. Its public API is still evolving, and the repository currently consists of standalone Python modules rather than a conventional installable package structure with `pyproject.toml` or `setup.py`.

## Role inside Barsa

Flask-Forge belongs to **Barsa Tose'e (برسا توسعه)** because it is a reusable software-development toolkit intended to support Flask-based application development.

## Core Application Class: `Forge`

`Flask_Forge.py` exposes the main `Forge` class. It creates and owns an underlying `flask.Flask` application and adds convenience behavior around it.

### Application initialization

`Forge(...)` currently accepts:

- `name` — required application name.
- `secret_key` — optional; a random 32-byte hex token is generated when omitted.
- `database_function` — optional database initialization callback.
- `before_request` — optional request hook.
- `after_request` — optional response hook.
- `rate_limit_func` — optional custom rate-limit callback.

A Flask-WTF `CSRFProtect` instance is initialized automatically.

### Routing

`Forge.route(...)` wraps Flask routing and supports the common HTTP methods:

- `GET`
- `POST`
- `PUT`
- `DELETE`
- `PATCH`
- `OPTIONS`
- `HEAD`

The wrapped route function receives the current Flask request object as its first argument.

`Forge.route_api(...)` provides a similar route registration flow for API endpoints and exempts the wrapped handler from CSRF protection.

### Application execution

`Forge.run(...)` starts the Flask development server and, when a database initialization function is registered, invokes it before starting the server. Server startup errors are wrapped in the project's `RunBarsaFlaskKitError` exception.

## Database / ORM Layer

`ORM.py` provides the `Database` wrapper around Flask-SQLAlchemy.

### Connections

The current implementation supports:

- direct SQLAlchemy connection URLs,
- MySQL connection settings,
- SQLite connection settings.

For SQLite, the database name is reduced to a basename before building the URI to avoid path traversal through the database-name setting.

### Schema handling

`Database` assigns its `auto_migrate` method as the Forge application's database initialization callback. The auto-migration implementation uses Alembic's migration/autogeneration APIs to compare the current database schema with SQLAlchemy metadata and invoke generated upgrade operations.

The wrapper also exposes:

- `create_all()`
- `drop_all()`
- `session_scope()` transactional context manager

### Data operations

Current convenience methods include:

- `get(model, id)`
- `get_first(model, **data)`
- `get_all(model)`
- `find(model, **data)`
- `count(model, **data)`
- `exists(model, **data)`
- `add(item, commit=True)`
- `add_all(items, commit=True)`
- `update(model, id, **data)`
- `delete(model, id)`
- `delete_all(model, **data)`
- `add_relation(relation, item)`
- `remove_relation(relation, item)`
- `select(model, *columns)`
- `limit(model, number)`
- `order(model, column, descending=False)`
- `with_relation(model, relation)`
- `commit()`
- `rollback()`

Mutating helpers generally commit their transaction and roll back when an exception occurs.

## Authentication and Authorization

`Auth.py` provides an `Auth` class built on the database wrapper, Werkzeug password hashing, and Flask session helpers.

Current functionality includes:

- setting a username and password for registration,
- password hashing,
- user registration,
- user login,
- logout,
- retrieving the currently authenticated user from the session,
- `require_login(...)` protection,
- in-memory role assignment,
- `require_role(...)` authorization checks,
- a small callback/signal helper class.

The current role mapping is stored in the `Auth` instance rather than persisted in the database, so role state should be treated as experimental in the present implementation.

## Form Validation

`Form.py` provides a lightweight form validation helper.

It can currently validate:

- required keys,
- Python value types,
- string/sequence length ranges,
- numeric value ranges.

Validation errors are separated into:

- `data_errors`
- `type_errors`
- `length_errors`
- `number_errors`

`validate(...)` combines the checks and `get_errors()` exposes the collected validation result.

## Cache

`cache.py` contains an in-memory cache implementation based on `OrderedDict` and `CacheItem`.

Its implemented concepts include:

- optional TTL expiration,
- maximum cache size,
- least-recently-used eviction behavior,
- `get(...)`,
- `get_or_raise(...)`,
- `delete(...)`,
- `delete_many(...)`,
- `has(...)`,
- `clear()`,
- `size()`,
- `keys()`.

The cache module is still experimental and should be tested carefully before being relied upon as a production cache API.

## Security Utilities

`security.py` currently provides:

- `escape_data(...)` for HTML escaping,
- `hashing(...)` for password/data hashing through Werkzeug,
- `check_hashing(...)` for hash verification,
- `validate_json(...)` for simple key/type validation,
- an in-memory `rate_limit(...)` helper,
- `upload_file(...)` with filename sanitization, extension allow-listing, optional size limits, directory creation, and file saving.

The default rate limiter stores counters in process memory, so a multi-process production deployment would require a shared rate-limit backend.

## HTTP Utilities

`HTTPRequest.py` provides outbound HTTP helpers:

- `request_data(...)` supporting `GET`, `POST`, `PUT`, and `DELETE`,
- `to_json(...)`,
- `to_text(...)`.

Outbound request errors are wrapped as project-specific request exceptions.

## Response Helpers

`responses.py` contains wrappers around common Flask response functions:

- redirect responses,
- JSON responses,
- file serving through `send_from_directory`,
- URL generation,
- template rendering.

## Session, Cookie, and Email State Helpers

`state.py` currently provides helpers for:

- creating/updating Flask session values,
- reading session values,
- removing or clearing sessions,
- checking session keys,
- creating cookies,
- reading cookies,
- deleting cookies,
- sending a text email through Gmail SMTP using STARTTLS.

Email credentials are supplied directly to `send_email(...)`; applications should provide secrets securely through their own configuration rather than hard-code them.

## Test Client Wrapper

`TestClient.py` wraps Flask's built-in test client and currently exposes helpers for:

- `GET`
- `POST`
- `PUT`
- `DELETE`
- cookie operations,
- session transactions,
- request-context inspection.

## Admin Utilities

`admin.py` contains an `Admin` helper using the database wrapper. Current functionality includes basic pagination and convenience methods for reading, creating, updating, deleting, selecting, ordering, and accessing model data.

This module is present in the repository but is not currently re-exported from the top-level `Flask_Forge.py` module.

## Module Map

```text
Flask-Forge/
├── Flask_Forge.py     # Main Forge application wrapper
├── ORM.py             # Flask-SQLAlchemy + database helpers
├── Auth.py            # Authentication and authorization
├── Form.py            # Input/form validation
├── cache.py           # In-memory TTL/LRU cache logic
├── security.py        # Hashing, escaping, rate limit, uploads
├── HTTPRequest.py     # Outbound HTTP helpers
├── responses.py       # Flask response helpers
├── state.py           # Session, cookie, and email helpers
├── TestClient.py      # Flask test-client wrapper
├── admin.py           # Admin/data-management utilities
├── exceptions.py      # Project-specific exceptions
└── README.md
```

## Verified Runtime Dependencies

Based on imports in the current codebase, Flask-Forge uses:

- Flask
- Flask-WTF
- Flask-SQLAlchemy
- SQLAlchemy
- Alembic
- Requests
- Werkzeug

The repository currently does **not** include `requirements.txt`, `pyproject.toml`, or other package metadata, so dependency and package installation are not yet formalized.

For development, the required external packages can be installed manually:

```bash
pip install Flask Flask-WTF Flask-SQLAlchemy SQLAlchemy alembic requests Werkzeug
```

## Minimal Application Example

A minimal Forge application can be structured like this:

```python
from Flask_Forge import Forge

app = Forge(name=__name__)

@app.route('/')
def home(request):
    return 'Hello from Flask-Forge'

if __name__ == '__main__':
    app.run(debug=True)
```

The route callback receives Flask's request object automatically.

## Database Example

```python
from Flask_Forge import Forge
from ORM import Database

app = Forge(name=__name__)
database = Database(app)
db = database.connect(type='sqlite', name='app.db')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

if __name__ == '__main__':
    app.run(debug=True)
```

Because `Database` installs its auto-migration callback on the Forge application, the current design attempts schema synchronization before the development server starts.

## Current Development Status

Flask-Forge is a **development-stage framework extension/toolkit**. It already contains a broad set of reusable components, but its API should not yet be treated as stable.

Important repository-level work still includes:

- packaging the project as a standard Python package,
- adding a pinned dependency file or `pyproject.toml`,
- adding automated tests for all modules,
- documenting API compatibility and versioning,
- removing generated `__pycache__` files from version control,
- validating experimental helpers before production use,
- reviewing the automatic schema-migration approach for production databases.

## Project Direction

The goal of Flask-Forge is to give Barsa Tose'e a reusable Flask development layer that reduces repeated boilerplate while keeping direct access to Flask and SQLAlchemy concepts available to developers.

---

# Flask-Forge — مستندات فارسی

> ابزار آزمایشی برسا توسعه برای افزودن لایه‌ای سطح‌بالاتر از امکانات برنامه، دیتابیس، احراز هویت، اعتبارسنجی، Cache، امنیت، HTTP، State، Admin و Test روی Flask.

## معرفی

**Flask-Forge** یکی از پروژه‌های **برسا توسعه** است که برای افزایش قابلیت‌های Flask و کاهش کدهای تکراری در پروژه‌های وب ساخته می‌شود. هدف آن جایگزین کردن Flask نیست؛ بلکه مجموعه‌ای از Wrapperها و Utilityها را روی Flask ارائه می‌دهد تا کارهایی مانند تعریف Route، اتصال پایگاه داده، احراز هویت، اعتبارسنجی ورودی، Session و Cookie، Cache، درخواست HTTP، Responseها، آپلود فایل و تست برنامه با API اختصاصی و ساده‌تری انجام شوند.

مخزن فعلی هنوز یک **کتابخانه/Toolkit آزمایشی و در حال توسعه** است و هنوز به شکل یک Python Package پایدار منتشر نشده است. API پروژه نیز هنوز می‌تواند تغییر کند و ساختار مخزن فعلاً از چند ماژول مستقل Python تشکیل شده و فایل‌هایی مانند `pyproject.toml` یا `setup.py` ندارد.

## جایگاه در برسا

Flask-Forge زیرمجموعه **برسا توسعه** است، زیرا یک ابزار توسعه نرم‌افزار قابل استفاده مجدد برای پروژه‌های Flask محسوب می‌شود.

## کلاس اصلی `Forge`

فایل `Flask_Forge.py` کلاس اصلی `Forge` را ارائه می‌کند. این کلاس یک برنامه `flask.Flask` داخلی می‌سازد و قابلیت‌های کمکی را پیرامون آن قرار می‌دهد.

### ساخت برنامه

`Forge(...)` در وضعیت فعلی این ورودی‌ها را می‌پذیرد:

- `name` — نام برنامه و اجباری.
- `secret_key` — اختیاری؛ در صورت نبود یک Token تصادفی تولید می‌شود.
- `database_function` — Callback اختیاری برای آماده‌سازی دیتابیس.
- `before_request` — Hook اختیاری قبل از Request.
- `after_request` — Hook اختیاری بعد از Request.
- `rate_limit_func` — Rate Limiter سفارشی اختیاری.

همچنین `CSRFProtect` از Flask-WTF به‌صورت خودکار ساخته می‌شود.

### Routeها

`Forge.route(...)` تعریف Route در Flask را Wrap می‌کند و متدهای زیر را می‌پذیرد:

- `GET`
- `POST`
- `PUT`
- `DELETE`
- `PATCH`
- `OPTIONS`
- `HEAD`

تابع Route در این مدل، Request فعلی Flask را به‌عنوان اولین Argument دریافت می‌کند.

`Forge.route_api(...)` جریان مشابهی برای APIها دارد و Handler ثبت‌شده را از CSRF Exempt می‌کند.

### اجرای برنامه

`Forge.run(...)` سرور توسعه Flask را اجرا می‌کند و در صورت وجود Database Function، ابتدا آن را اجرا می‌کند. خطاهای شروع سرور با Exception اختصاصی `RunBarsaFlaskKitError` Wrap می‌شوند.

## لایه دیتابیس و ORM

`ORM.py` کلاس `Database` را به‌عنوان Wrapper روی Flask-SQLAlchemy ارائه می‌کند.

### اتصال

پیاده‌سازی فعلی از این حالت‌ها پشتیبانی می‌کند:

- SQLAlchemy Connection URL مستقیم،
- تنظیمات MySQL،
- تنظیمات SQLite.

در SQLite، نام دیتابیس با `os.path.basename` محدود می‌شود تا از Path Traversal از طریق نام فایل دیتابیس جلوگیری شود.

### Schema

کلاس `Database` تابع `auto_migrate` خود را به‌عنوان Database Initialization Callback برنامه Forge ثبت می‌کند. این بخش با APIهای Alembic تفاوت Metadata SQLAlchemy و Schema فعلی دیتابیس را محاسبه می‌کند و عملیات Upgrade تولیدشده را اجرا می‌کند.

متدهای زیر نیز وجود دارند:

- `create_all()`
- `drop_all()`
- `session_scope()` برای Transaction Context

### عملیات داده

متدهای فعلی شامل موارد زیر هستند:

- `get`
- `get_first`
- `get_all`
- `find`
- `count`
- `exists`
- `add`
- `add_all`
- `update`
- `delete`
- `delete_all`
- `add_relation`
- `remove_relation`
- `select`
- `limit`
- `order`
- `with_relation`
- `commit`
- `rollback`

متدهای تغییردهنده داده معمولاً Transaction را Commit می‌کنند و در صورت Exception عملیات Rollback انجام می‌شود.

## احراز هویت و دسترسی

فایل `Auth.py` کلاس `Auth` را بر پایه Database، Password Hashing در Werkzeug و Sessionهای Flask ارائه می‌کند.

قابلیت‌های فعلی:

- تنظیم Username و Password برای ثبت‌نام،
- Hash کردن Password،
- ثبت‌نام کاربر،
- Login،
- Logout،
- دریافت User فعلی از Session،
- `require_login(...)`،
- تعیین Role در حافظه،
- `require_role(...)`،
- Helper ساده Callback/Signal.

Roleها در وضعیت فعلی داخل Instance کلاس `Auth` نگهداری می‌شوند و در دیتابیس Persist نمی‌شوند؛ بنابراین سیستم Role فعلی هنوز آزمایشی است.

## اعتبارسنجی فرم

`Form.py` یک Validator سبک برای داده‌ها ارائه می‌دهد.

در حال حاضر می‌تواند این موارد را بررسی کند:

- وجود فیلدهای لازم،
- Type مقدارها،
- حداقل و حداکثر طول String/Sequence،
- حداقل و حداکثر مقدارهای عددی.

خطاها در چهار گروه نگهداری می‌شوند:

- `data_errors`
- `type_errors`
- `length_errors`
- `number_errors`

## Cache

`cache.py` منطق Cache درون‌حافظه‌ای را با `OrderedDict` و `CacheItem` پیاده‌سازی می‌کند.

مفاهیم فعلی آن شامل:

- TTL اختیاری،
- حداکثر تعداد Item،
- حذف بر اساس Least Recently Used،
- دریافت داده،
- حذف یک یا چند Key،
- بررسی وجود،
- پاک‌سازی کامل،
- مشاهده Size و Keyها.

این ماژول هنوز آزمایشی است و پیش از استفاده Production باید به‌طور کامل تست شود.

## ابزارهای امنیتی

`security.py` شامل این قابلیت‌ها است:

- `escape_data(...)` برای HTML Escape،
- `hashing(...)` برای Hash با Werkzeug،
- `check_hashing(...)` برای بررسی Hash،
- `validate_json(...)` برای بررسی ساده Key و Type،
- `rate_limit(...)` در حافظه،
- `upload_file(...)` همراه با Secure Filename، Allow-list پسوند، محدودیت اختیاری حجم، ساخت پوشه و ذخیره فایل.

Rate Limiter فعلی داخل حافظه Process قرار دارد و برای Deployment چند Process باید Backend مشترک داشته باشد.

## ابزارهای HTTP

`HTTPRequest.py` این موارد را ارائه می‌کند:

- `request_data(...)` برای `GET`، `POST`، `PUT` و `DELETE`،
- `to_json(...)`،
- `to_text(...)`.

خطاهای Request در Exception اختصاصی پروژه Wrap می‌شوند.

## Responseها

`responses.py` Wrapperهایی برای قابلیت‌های متداول Flask دارد:

- Redirect،
- JSON Response،
- ارسال فایل از Directory،
- ساخت URL،
- Render Template.

## Session، Cookie و Email

`state.py` در وضعیت فعلی Helperهایی برای موارد زیر دارد:

- ساخت/تغییر Session،
- خواندن Session،
- حذف یا Clear کردن Session،
- بررسی وجود Session Key،
- ساخت Cookie،
- خواندن Cookie،
- حذف Cookie،
- ارسال Email متنی با Gmail SMTP و STARTTLS.

اطلاعات ورود ایمیل باید توسط برنامه مصرف‌کننده به‌صورت امن مدیریت شوند و نباید داخل کد Hard-code شوند.

## Test Client

`TestClient.py` روی Test Client داخلی Flask Wrapper ایجاد می‌کند و Helperهایی برای این موارد دارد:

- GET
- POST
- PUT
- DELETE
- عملیات Cookie
- Session Transaction
- Request Context

## ابزارهای Admin

`admin.py` کلاس `Admin` را برای عملیات مدیریتی ساده روی Database ارائه می‌کند. امکانات فعلی شامل Pagination و Helperهایی برای خواندن، ساخت، Update، Delete، Select و Order داده‌ها است.

این ماژول در مخزن وجود دارد اما در حال حاضر از فایل اصلی `Flask_Forge.py` Re-export نشده است.

## نقشه ماژول‌ها

```text
Flask-Forge/
├── Flask_Forge.py
├── ORM.py
├── Auth.py
├── Form.py
├── cache.py
├── security.py
├── HTTPRequest.py
├── responses.py
├── state.py
├── TestClient.py
├── admin.py
├── exceptions.py
└── README.md
```

## وابستگی‌های تأییدشده

براساس Importهای کد فعلی:

- Flask
- Flask-WTF
- Flask-SQLAlchemy
- SQLAlchemy
- Alembic
- Requests
- Werkzeug

در حال حاضر `requirements.txt` یا `pyproject.toml` وجود ندارد و Packaging رسمی پروژه هنوز انجام نشده است.

برای توسعه می‌توان وابستگی‌ها را به‌صورت دستی نصب کرد:

```bash
pip install Flask Flask-WTF Flask-SQLAlchemy SQLAlchemy alembic requests Werkzeug
```

## نمونه برنامه ساده

```python
from Flask_Forge import Forge

app = Forge(name=__name__)

@app.route('/')
def home(request):
    return 'Hello from Flask-Forge'

if __name__ == '__main__':
    app.run(debug=True)
```

در این ساختار، Request فعلی Flask به‌صورت خودکار به تابع Route داده می‌شود.

## نمونه اتصال دیتابیس

```python
from Flask_Forge import Forge
from ORM import Database

app = Forge(name=__name__)
database = Database(app)
db = database.connect(type='sqlite', name='app.db')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

if __name__ == '__main__':
    app.run(debug=True)
```

در طراحی فعلی، `Database` تابع Auto Migration خود را به Forge متصل می‌کند تا پیش از شروع Server تلاش شود Schema با Metadata هماهنگ شود.

## وضعیت توسعه

Flask-Forge در حال حاضر یک **Toolkit/Framework Extension در مرحله توسعه** است. پروژه مجموعه قابل توجهی از قابلیت‌ها دارد، اما API آن هنوز نباید Stable فرض شود.

کارهای مهم سطح مخزن که هنوز باقی مانده‌اند شامل:

- تبدیل پروژه به Python Package استاندارد،
- افزودن `requirements.txt` یا `pyproject.toml`،
- تست خودکار برای تمام ماژول‌ها،
- تعریف Versioning و API Compatibility،
- حذف `__pycache__` از Version Control،
- تست و تثبیت Helperهای آزمایشی،
- بازبینی روش Auto Migration برای دیتابیس‌های Production.

## مسیر کلی پروژه

هدف Flask-Forge این است که برای برسا توسعه یک لایه قابل استفاده مجدد روی Flask ایجاد کند تا Boilerplateهای تکراری کمتر شوند، در حالی که توسعه‌دهنده همچنان به مفاهیم اصلی Flask و SQLAlchemy دسترسی مستقیم داشته باشد.
