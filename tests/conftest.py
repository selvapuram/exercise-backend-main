import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.database import Base, engine, SessionLocal, get_db
from sqlalchemy.orm import sessionmaker

# Override the database for testing
Base.metadata.create_all(bind=engine)

# Session local for test database
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Override the get_db dependency for testing
app.dependency_overrides[get_db] = lambda: TestSessionLocal()


@pytest.fixture(scope="function")
def db():
    """Fixture to provide a clean session for each test"""
    db = TestSessionLocal()  # Create a new session for each test
    try:
        yield db  # Provide the session to the test
    finally:
        db.rollback()  # Rollback the session to avoid side effects between tests
        db.close()  # Close the session


@pytest.fixture
def client(db):
    """Fixture to provide a test client for FastAPI."""
    # Inject db session into the client
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)
