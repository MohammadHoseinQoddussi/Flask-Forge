from exceptions import (
    MissingDataError,
    RunBarsaFlaskKitError,
    MethodNotAllowedError
)
from flask_wtf.csrf import CSRFProtect
from ORM import Database
from Auth import Auth
from TestClient import TestClient
from Form import Form
from cache import Cache
from functools import wraps

from responses import (
    redirect,
    json_data,
    send_from_directory,
    url_for
)

from state import (
    make_session,
    get_session,
    remove_session,
    clear_session,
    return_session,
    make_cookie,
    get_cookie,
    delete_cookie
)

from security import (
    hashing,
    check_hashing,
    escape_data,
    validate_json,
    upload_file,
    rate_limit
)

from HTTPRequest import request_data, to_json, to_text
import secrets
import flask

class Forge:
    """
    Flask_Forge main application class.
    A wrapper around Flask with built-in security, ORM, auth, and caching features.
    """
    
    def __init__(
        self,
        name: str = None,
        secret_key: str = None,
        database_function: callable = None,
        before_request: callable = None,
        after_request: callable = None,
        rate_limit_func: callable = None
    ):
        """
        Initialize the Flask_Forge application.
        
        Args:
            name: Application name (required)
            secret_key: Secret key for session management (auto-generated if not provided)
            database_function: Optional function to initialize database connection
            before_request: Optional callback function to run before each request
            after_request: Optional callback function to run after each request
            rate_limit_func: Optional custom rate limit function (default: rate_limit with 120 req/120s)
        """
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
        
        # Setup before request handler
        @self.app.before_request
        def before():
            if self.rate_limit_func:
                if not self.rate_limit_func(ip=flask.request.remote_addr):
                    flask.abort(429)
            else:
                if not rate_limit(
                    ip=flask.request.remote_addr,
                    limit=120,
                    limit_time=120
                ):
                    flask.abort(429)

            if before_request:
                return before_request(flask.request)

        # Setup after request handler
        @self.app.after_request
        def after(response):
            if after_request:
                if (after := after_request(response)) is not None:
                    return after
                else:
                    return response

            return response

    def route(
        self,
        url: str,
        methods: list = None,
        function: callable = None,
        status_code: int = 200
    ):
        """
        Register a route handler for the application.
        
        Args:
            url: The URL pattern to match
            methods: List of HTTP methods (default: ['GET'])
            function: The view function to handle requests
            status_code: HTTP status code to return (default: 200)
        
        Returns:
            Decorator function or None if function is provided directly
        """
        if methods is None:
            methods = ['GET']
            
        if not url:
            raise MissingDataError('The URL is not defined')
        
        if not methods:
            raise MissingDataError('The methods list is not defined')

        for method in methods:
            if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'):
                raise MethodNotAllowedError(f'The method {method} is not allowed')
        
        def decorator(func: callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(flask.request, *args, **kwargs)

                if isinstance(result, tuple) and len(result) == 2:
                    return result

                return result, status_code

            self.app.route(url, methods=methods)(wrapper)
            return wrapper
        
        if function:
            return decorator(function)
        return decorator
    
    def route_api(
        self,
        url: str,
        methods: list = None,
        function: callable = None,
        status_code: int = 200
    ):
        """
        Register an API route handler (CSRF exempted).
        
        Args:
            url: The URL pattern to match
            methods: List of HTTP methods (default: ['GET'])
            function: The view function to handle requests
            status_code: HTTP status code to return (default: 200)
        
        Returns:
            Decorator function or None if function is provided directly
        """
            
        if not url:
            raise MissingDataError('The URL is not defined')
        
        if not methods:
            raise MissingDataError('The methods list is not defined')
    
        for method in methods:
            if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'):
                raise MethodNotAllowedError(f'The method {method} is not allowed')
        
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

        
        if function:
            return decorator(function)
        return decorator

    def run(
        self,
        port: int = 5000,
        host: str = '127.0.0.1',
        debug: bool = False,
        **options
    ) -> None:
        """
        Start the Flask application server.
        
        Args:
            port: Port number to listen on (default: 5000)
            host: Host address to bind to (default: '127.0.0.1')
            debug: Enable debug mode (default: False)
            **options: Additional options passed to Flask app.run()
        
        Raises:
            RunBarsaFlaskKitError: If the server fails to start
        """
        try:
            # Initialize database connection if a function is provided
            if self.database_function:
                self.database_function()

            # Start the Flask development server with provided configurations
            self.app.run(
                port=port,
                host=host,
                debug=debug,
                **options
            )
        except Exception as error:
            # Wrap and re-raise the exception to maintain clear error context
            raise RunBarsaFlaskKitError(f"Server failed to start: {error}") from error

    @staticmethod
    def get_option(
        key: str,
        data: dict,
        default=None
    ):
        """
        Safely get a value from a dictionary.
        
        Args:
            key: The key to look up in the dictionary
            data: The dictionary to search
            default: Default value if key is not found
        
        Returns:
            The value associated with the key, or the default value
        
        Raises:
            MissingDataError: If data is not a dictionary
        """
        if not isinstance(data, dict):
            raise MissingDataError('The data must be a dictionary')

        return data.get(key, default)
