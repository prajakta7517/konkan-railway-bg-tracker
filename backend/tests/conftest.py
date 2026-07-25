import os

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("COOKIE_SECURE", "false")

import pytest
from mongomock_motor import AsyncMongoMockClient

import app.database as database_module


@pytest.fixture(autouse=True)
def mock_db():
    client = AsyncMongoMockClient()
    database_module._client = client
    database_module._db = client["test_db"]
    yield database_module._db
    database_module._client = None
    database_module._db = None
