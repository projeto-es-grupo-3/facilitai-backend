import pytest
# from helpers import Helpers
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from testcontainers.postgres import PostgresContainer

from main.main import create_app
from models.model import db
from helpers import Helpers


@pytest.fixture
def app(postgres):
    app = create_app({"SQLALCHEMY_DATABASE_URI": postgres.get_connection_url()})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def db_session(postgres):
    engine = create_engine(postgres.get_connection_url())
    session = scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False)
    )
    # db.session = session

    db.metadata.create_all(engine)

    yield session
    session.close()
    db.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def postgres(request):
    postgres = PostgresContainer("postgres:15")
    postgres.start()

    def stop_db():
        postgres.stop()

    request.addfinalizer(stop_db)

    return postgres


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def json_headers():
    return {'Content-Type': 'application/json'}