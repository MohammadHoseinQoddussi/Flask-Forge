from functools import wraps
import secrets

import flask
from flask_wtf.csrf import CSRFProtect

from .auth import Auth
from .cache import Cache
from .exceptions import MissingDataError, MethodNotAllowedError, RunBarsaFlaskKitError
from .form import Form
from .http_request import request_data, to_json, to_text
from .orm import Database
from .responses import redirect, json_data, send_from_directory, url_for
from .security import hashing, check_hashing, escape_data, validate_json, upload_file, rate_limit
from .state import (
    make_session,
    get_session,
    remove_session,
    clear_session,
    return_session,
    make_cookie,
    get_cookie,
    delete_cookie,
)
from .test_client import TestClient


class Forge:
    """Main Flask-Forge application wrapper."""

    def __init__(
        self,
        name: str = None,
        secret_key: str = None,
        database_function: callable = None,
        before_request: callable = None,
        after_request: callable = None,
        rate_limit_func: callable = None,
    ):
        if not name:
            raise MissingDataError('The name is not defined')
        if not isinstance(name, str):
            raise MissingDataError('The name must be a string')

        self.name = name
        self.app = flask.Flask(name)
        self.app.secret_key = secret_key if secret_key else secrets.token_hex(32)

        if database_function is not None and not callable(database_function):
            raise MissingDataError('database_function must be callable')
        self.database_function = database_function

        if rate_limit_func is not None and not callable(rate_limit_func):
            raise MissingDataError('rate_limit_func must be callable')
        self.rate_limit_func = rate_limit_func

        self.csrf = CSRFProtect(self.app)

        @self.app.before_request
        def before():
            limiter = self.rate_limit_func
            allowed = limiter(ip=flask.request.remote_addr) if limiter else rate_limit(
                ip=flask.request.remote_addr,
                limit=120,
                limit_time=120,
            )
            if not allowed:
                flask.abort(429)
            if before_request:
                return before_request(flask.request)
            return None

        @self.app.after_request
        def after(response):
            if after_request:
                result = after_request(response)
                if result is not None:
                    return result
            return response

    @staticmethod
    def _validate_methods(methods):
        allowed = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD')
        for method in methods:
            if method not in allowed:
                raise MethodNotAllowedError(f'The method {method} is not allowed')

    def route(self, url: str, methods: list = None, function: callable = None, status_code: int = 200):
        methods = methods or ['GET']
        if not url:
            raise MissingDataError('The URL is not defined')
        self._validate_methods(methods)

        def decorator(func: callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(flask.request, *args, **kwargs)
                if isinstance(result, tuple) and len(result) == 2:
                    return result
                return result, status_code

            self.app.route(url, methods=methods)(wrapper)
            return wrapper

        return decorator(function) if function else decorator

    def route_api(self, url: str, methods: list = None, function: callable = None, status_code: int = 200):
        methods = methods or ['GET']
        if not url:
            raise MissingDataError('The URL is not defined')
        self._validate_methods(methods)

        def decorator(func: callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(flask.request, *args, **kwargs)
                if isinstance(result, tuple) and len(result) == 2:
                    return result
                return result, status_code

            self.csrf.exempt(wrapper)
            self.app.route(url, methods=methods)(wrapper)
            return wrapper

        return decorator(function) if function else decorator

    def run(self, port: int = 5000, host: str = '127.0.0.1', debug: bool = False, **options) -> None:
        try:
            if self.database_function:
                self.database_function()
            self.app.run(port=port, host=host, debug=debug, **options)
        except Exception as error:
            raise RunBarsaFlaskKitError(f'Server failed to start: {error}') from error

    @staticmethod
    def get_option(key: str, data: dict, default=None):
        if not isinstance(data, dict):
            raise MissingDataError('The data must be a dictionary')
        return data.get(key, default)
