import flask

from .exceptions import MissingDataError, VaildDataError
from .orm import Database
from .security import hashing, check_hashing
from .state import make_session, remove_session, check_session, get_session


class Auth:
    def __init__(self, db: Database):
        self.db = db
        self._password = None
        self._username = None
        self.role = {}

    def setting(self, password: str = None, username: str = None):
        if not password or not username:
            raise MissingDataError('the password or username is not defined')
        if not isinstance(password, str) or not isinstance(username, str):
            raise VaildDataError('the password or username is not valid')
        self._password = hashing(password)
        self._username = username

    def register(self, model=None, **data: dict):
        if not model:
            raise MissingDataError('the model is not defined')
        if self.db.exists(model=model, username=self._username):
            raise VaildDataError('the username is already exist')

        user = model(username=self._username, password=self._password, **data)
        self.db.add(user)
        make_session(id=user.id)
        return user

    def login(self, model=None, username: str = None, password: str = None):
        if not model or not username or not password:
            raise MissingDataError('the model or username or password is not defined')
        if not isinstance(username, str) or not isinstance(password, str):
            raise VaildDataError('the model or username or password is not valid')

        user = self.db.get_first(model=model, username=username)
        if not user or not check_hashing(password, user.password):
            raise VaildDataError('the username or password is not valid')

        make_session(id=user.id)
        return user

    def logout(self):
        remove_session('id')

    def get_user(self, model=None):
        if not model:
            raise MissingDataError('the model is not defined')
        if not check_session('id'):
            raise MissingDataError('the session is not defined')
        return self.db.get(model, get_session('id'))

    def require_login(self, function: callable):
        def wrapper(*args, **kwargs):
            if not check_session('id'):
                flask.abort(401)
            return function(*args, **kwargs)
        return wrapper

    def add_role(self, model=None, id: int = None, role: str = None):
        if not model or not id or not role:
            raise MissingDataError('the model, id or role is not defined')
        if not isinstance(id, int) or not isinstance(role, str):
            raise VaildDataError('the id or role is not valid')

        user = self.db.get(model, id)
        if not user:
            raise VaildDataError('the user is not found')
        self.role[str(user.id)] = role
        return user

    def require_role(self, function: callable, model=None, role: str = None):
        if not model or not role:
            raise MissingDataError('the model or role is not defined')
        if not isinstance(role, str):
            raise VaildDataError('the role is not valid')

        def wrapper(*args, **kwargs):
            if not check_session('id'):
                flask.abort(401)
            user = self.db.get(model, get_session('id'))
            if not user or self.role.get(str(user.id)) != role:
                flask.abort(403)
            return function(*args, **kwargs)
        return wrapper

    class Signal:
        def __init__(self):
            self.before = lambda: None
            self.after = lambda: None

        def Performance(self, before: dict = None, after: dict = None):
            self.before(**before) if before else self.before()
            self.after(**after) if after else self.after()

        def set_name_after(self, function: callable):
            self.before = function

        def set_name_before(self, function: callable):
            self.after = function
