import os
import tempfile
import pytest

from armonaut import create_app
from armonaut import db as _db
from armonaut.models import Account, Project


TEST_DB_PATH = os.path.join(tempfile.gettempdir(), 'test.db')


@pytest.fixture
def vcr_config():
    return {
        'record_mode': 'once',
        'filter_headers': [('authorization', 'ACCESS_TOKEN')],
        'filter_query_parameters': [('client_secret', 'CLIENT_SECRET')]
    }


@pytest.fixture
def vcr_cassette_path(request, vcr_cassette_name):
    return os.path.join('tests', 'cassettes', request.module.__name__[6:], vcr_cassette_name)


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    def teardown():
        _db.drop_all()
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def account(session):
    account = Account()
    account.github_id = 12345
    account.github_login = 'SethMichaelLarson'
    account.github_email = 'sethmichaellarson@protonmail.com'
    account.github_access_token = ''

    session.add(account)
    session.commit()
    return account


@pytest.fixture(scope='function')
def project(account, session):
    project = Project()
    project.owner = 'armonaut'
    project.name = 'armonaut'
    project.remote_host = 'gh'
    project.remote_id = 123
    project.default_branch = 'master'
    project.private = False
    project.account = account

    session.add(project)
    session.commit()
    return project
