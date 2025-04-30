# backend/conftest.py
"""
Global fixtures shared by both unit- and integration-tests.
Creates a DAO that talks to a throw-away Mongo instance and
guarantees the collection is empty after each session.
"""

import os
import pytest
import pymongo
from contextlib import contextmanager
from src.util.dao import DAO

TEST_URL = "mongodb://root:root@localhost:27017"   # docker-compose address
TEST_COLL = "user"


@contextmanager
def _temporary_mongo_url(url: str):
    """Temporarily override MONGO_URL in the environment."""
    original = os.environ.get("MONGO_URL")
    os.environ["MONGO_URL"] = url
    try:
        yield
    finally:
        # restore (or remove) the variable
        if original is None:
            os.environ.pop("MONGO_URL", None)
        else:
            os.environ["MONGO_URL"] = original


@pytest.fixture(scope="session")
def dao():
    """
    Session-scoped DAO fixture.

    * points DAO at a local Docker-Mongo via env var
    * drops the collection before and after the session so nothing
      touches production data
    """
    with _temporary_mongo_url(TEST_URL):
        client = pymongo.MongoClient(TEST_URL)
        client.edutask.drop_collection(TEST_COLL)

        # hand out the DAO wired to the test collection
        _dao = DAO(collection_name=TEST_COLL)
        yield _dao

        # final clean-up
        _dao.collection.drop()
        client.close()
