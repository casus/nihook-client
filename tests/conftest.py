import os
import pytest
from nocodb_client import Nocodb

@pytest.fixture(scope="session")
def nocodb():
    """
    Shared NocoDB client instance for all tests.
    Uses environment variables NOCODB_HOST and NOCODB_TOKEN.
    """
    host = os.getenv("NOCODB_HOST", "http://localhost:8080")
    token = os.getenv("NOCODB_TOKEN")

    if not token:
        raise RuntimeError("NOCODB_TOKEN is not set. Make sure CI or setup script exports it.")

    client = Nocodb(host=host, auth_token=token)
    yield client

    # optional teardown (e.g., cleanup test bases)
    # client.delete_base("test_base")  # if your wrapper supports it
