from alembic.migration import MigrationContext
from alembic.autogenerate import produce_migrations
from alembic.operations import Operations
import flask_sqlalchemy
import sqlalchemy
import os
from contextlib import contextmanager
from exceptions import ConnectDatabaseError, MissingDataError

class Database:
    def __init__(self, app):
        self.app = app
        self.db = None

        self.app.database_function = self.auto_migrate

    #==============context manager for transaction==============
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.db.session
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    #==============connect==============
    def connect(
            self,
            url_connect: str = None,
            **setting_connect: dict
        )-> flask_sqlalchemy.SQLAlchemy:

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
                        database=setting_connect.get('database')
                    )

                case 'sqlite':
                    # Security fix: prevent path traversal attacks
                    db_name = os.path.basename(setting_connect.get('name', 'database.db'))
                    database_uri = f'sqlite:///{db_name}'

                case _:
                    raise ConnectDatabaseError(
                        'the database type is not defined'
                    )

        self.app.app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

        self.db = flask_sqlalchemy.SQLAlchemy(self.app.app)

        return self.db

    #==============create all==============
    def create_all(self):
        if self.db is None:
            raise ConnectDatabaseError(
                'the database is not connected'
            )

        with self.app.app.app_context():
            self.db.create_all()

    #==============drop all==============
    def drop_all(self):
        if self.db is None:
            raise ConnectDatabaseError(
                'the database is not connected'
            )

        with self.app.app.app_context():
            self.db.drop_all()
    #==============auto migrate==============
    def auto_migrate(self):

        if self.db is None:
            return

        with self.app.app.app_context():

            with self.db.engine.begin() as connection:

                context = MigrationContext.configure(connection)

                migration = produce_migrations(
                    context,
                    self.db.metadata
                )

                operations = Operations(context)

                def execute_operations(operation_list):

                    for operation in operation_list:

                        if hasattr(operation, 'ops'):
                            execute_operations(operation.ops)

                        else:
                            operations.invoke(operation)

                execute_operations(
                    migration.upgrade_ops.ops
                )

    #==============get==============
    # user = db.get(User, 10)

    def get(self, model, id):
        return self.db.session.get(model, id)


    #==============get first==============
    # user = db.get_first(User, username='ali')

    def get_first(self, model, **data):
        return self.db.session.query(model).filter_by(**data).first()


    #==============get all==============
    # users = db.get_all(User)

    def get_all(self, model):
        return self.db.session.query(model).all()


    #==============find==============
    # users = db.find(User, age=18)

    def find(self, model, **data):
        return self.db.session.query(model).filter_by(**data).all()


    #==============count==============
    # count = db.count(User, age=18)

    def count(self, model, **data):
        query = self.db.session.query(model)

        if data:
            query = query.filter_by(**data)

        return query.count()


    #==============exists==============
    # exists = db.exists(User, username='ali')

    def exists(self, model, **data):
        """Check if a record exists. Optimized to not fetch the entire record."""
        return self.db.session.query(model).filter_by(**data).limit(1).count() > 0


    #==============add==============
    # user = User(username='ali')
    # db.add(user)

    def add(self, item, commit=True):
        """Add an item to the database. Commit can be disabled for batch operations."""
        self.db.session.add(item)
        if commit:
            try:
                self.db.session.commit()
            except Exception:
                self.db.session.rollback()
                raise
        return item


    #==============add all==============
    # db.add_all([user1, user2, user3])

    def add_all(self, items, commit=True):
        """Add multiple items to the database. Single transaction for all items."""
        try:
            self.db.session.add_all(items)
            if commit:
                self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise
        return items


    #==============update==============
    # db.update(User, 10, username='ali')

    def update(self, model, id, **data):
        """Update a record by ID. Returns updated item or None if not found."""
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


    #==============delete==============
    # db.delete(User, 10)

    def delete(self, model, id):
        """Delete a record by ID. Returns True if deleted, False if not found."""
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


    #==============delete all==============
    # db.delete_all(User, age=18)

    def delete_all(self, model, **data):
        """Delete all records matching the filter. Returns count of deleted items."""
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


    #==============add relation==============
    # db.add_relation(user.posts, post)

    def add_relation(self, relation, item):
        """Add a relationship between two models."""
        try:
            relation.append(item)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise


    #==============remove relation==============
    # db.remove_relation(user.posts, post)

    def remove_relation(self, relation, item):
        """Remove a relationship between two models."""
        try:
            relation.remove(item)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise


    #==============select==============
    # users = db.select(User, User.id, User.username)

    def select(self, model, *columns):
        return self.db.session.query(*columns).select_from(model).all()


    #==============limit==============
    # users = db.limit(User, 10)

    def limit(self, model, number):
        return self.db.session.query(model).limit(number).all()


    #==============order==============
    # users = db.order(User, User.username)

    def order(self, model, column, descending=False):
        query = self.db.session.query(model)

        if descending:
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column)

        return query.all()


    #==============with relation==============
    # users = db.with_relation(User, 'posts')

    def with_relation(self, model, relation):
        from sqlalchemy.orm import selectinload

        return self.db.session.query(model).options(
            selectinload(getattr(model, relation))
        ).all()


    #==============commit==============
    # db.commit()

    def commit(self):
        self.db.session.commit()


    #==============rollback==============
    # db.rollback()

    def rollback(self):
        self.db.session.rollback()
