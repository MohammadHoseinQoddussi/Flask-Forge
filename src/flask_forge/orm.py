import os
from contextlib import contextmanager

import flask_sqlalchemy
from alembic.autogenerate import produce_migrations
from alembic.migration import MigrationContext
from alembic.operations import Operations

from .exceptions import ConnectDatabaseError


class Database:
    def __init__(self, app):
        self.app = app
        self.db = None
        self.app.database_function = self.auto_migrate

    @contextmanager
    def session_scope(self):
        if self.db is None:
            raise ConnectDatabaseError('the database is not connected')
        session = self.db.session
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def connect(self, url_connect: str = None, **setting_connect: dict) -> flask_sqlalchemy.SQLAlchemy:
        if url_connect:
            database_uri = url_connect
        else:
            match setting_connect.get('type'):
                case 'mysql':
                    database_uri = (
                        'mysql+mysqlconnector://'
                        '{username}:{password}@{host}/{database}'
                    ).format(
                        username=setting_connect.get('username'),
                        password=setting_connect.get('password'),
                        host=setting_connect.get('host', 'localhost'),
                        database=setting_connect.get('database'),
                    )
                case 'sqlite':
                    db_name = os.path.basename(setting_connect.get('name', 'database.db'))
                    database_uri = f'sqlite:///{db_name}'
                case _:
                    raise ConnectDatabaseError('the database type is not defined')

        self.app.app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        self.db = flask_sqlalchemy.SQLAlchemy(self.app.app)
        return self.db

    def create_all(self):
        self._require_connection()
        with self.app.app.app_context():
            self.db.create_all()

    def drop_all(self):
        self._require_connection()
        with self.app.app.app_context():
            self.db.drop_all()

    def auto_migrate(self):
        if self.db is None:
            return
        with self.app.app.app_context():
            with self.db.engine.begin() as connection:
                context = MigrationContext.configure(connection)
                migration = produce_migrations(context, self.db.metadata)
                operations = Operations(context)

                def execute_operations(operation_list):
                    for operation in operation_list:
                        if hasattr(operation, 'ops'):
                            execute_operations(operation.ops)
                        else:
                            operations.invoke(operation)

                execute_operations(migration.upgrade_ops.ops)

    def get(self, model, id):
        self._require_connection()
        return self.db.session.get(model, id)

    def get_first(self, model, **data):
        self._require_connection()
        return self.db.session.query(model).filter_by(**data).first()

    def get_all(self, model):
        self._require_connection()
        return self.db.session.query(model).all()

    def find(self, model, **data):
        self._require_connection()
        return self.db.session.query(model).filter_by(**data).all()

    def count(self, model, **data):
        self._require_connection()
        query = self.db.session.query(model)
        if data:
            query = query.filter_by(**data)
        return query.count()

    def exists(self, model, **data):
        self._require_connection()
        return self.db.session.query(model).filter_by(**data).limit(1).count() > 0

    def add(self, item, commit=True):
        self._require_connection()
        self.db.session.add(item)
        if commit:
            try:
                self.db.session.commit()
            except Exception:
                self.db.session.rollback()
                raise
        return item

    def add_all(self, items, commit=True):
        self._require_connection()
        try:
            self.db.session.add_all(items)
            if commit:
                self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise
        return items

    def update(self, model, id, **data):
        self._require_connection()
        try:
            item = self.db.session.get(model, id)
            if not item:
                return None
            for key, value in data.items():
                setattr(item, key, value)
            self.db.session.commit()
            return item
        except Exception:
            self.db.session.rollback()
            raise

    def delete(self, model, id):
        self._require_connection()
        try:
            item = self.db.session.get(model, id)
            if not item:
                return False
            self.db.session.delete(item)
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            raise

    def delete_all(self, model, **data):
        self._require_connection()
        try:
            query = self.db.session.query(model).filter_by(**data)
            items = query.all()
            for item in items:
                self.db.session.delete(item)
            self.db.session.commit()
            return len(items)
        except Exception:
            self.db.session.rollback()
            raise

    def add_relation(self, relation, item):
        self._require_connection()
        try:
            relation.append(item)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise

    def remove_relation(self, relation, item):
        self._require_connection()
        try:
            relation.remove(item)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise

    def select(self, model, *columns):
        self._require_connection()
        return self.db.session.query(*columns).select_from(model).all()

    def limit(self, model, number):
        self._require_connection()
        return self.db.session.query(model).limit(number).all()

    def order(self, model, column, descending=False):
        self._require_connection()
        query = self.db.session.query(model)
        query = query.order_by(column.desc() if descending else column)
        return query.all()

    def with_relation(self, model, relation):
        self._require_connection()
        from sqlalchemy.orm import selectinload
        return self.db.session.query(model).options(
            selectinload(getattr(model, relation))
        ).all()

    def commit(self):
        self._require_connection()
        self.db.session.commit()

    def rollback(self):
        self._require_connection()
        self.db.session.rollback()

    def _require_connection(self):
        if self.db is None:
            raise ConnectDatabaseError('the database is not connected')
