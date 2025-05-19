# backend/conftest.py
"""
Global fixtures shared by both unit- and integration-tests.

* Uses Docker-Mongo at  mongodb://root:root@localhost:27017
* Gives every **test function** its own clean collection **user_test**
* Attaches the UNIQUE index on `email` so DuplicateKeyError is raised
* Drops the collection after each test → never touches production data
"""
import os
import pytest
import pymongo
from contextlib import contextmanager
from src.util.dao import DAO

TEST_URL  = "mongodb://root:root@localhost:27017"   # docker-compose Mongo
TEST_COLL = "user"                             # test-only collection


@contextmanager
def _temporary_mongo_url(url: str):
    """Temporarily override MONGO_URL in the environment."""
    original = os.environ.get("MONGO_URL")
    os.environ["MONGO_URL"] = url
    try:
        yield
    finally:
        if original is None:
            os.environ.pop("MONGO_URL", None)
        else:
            os.environ["MONGO_URL"] = original


@pytest.fixture  # default scope = *function*  → fresh DAO per test
def dao():
    with _temporary_mongo_url(TEST_URL):
        client = pymongo.MongoClient(TEST_URL)
        db = client.edutask

        #  clean start for *this* test 
        db.drop_collection(TEST_COLL)

        # hand out the DAO wired to the test collection
        _dao = DAO(collection_name=TEST_COLL)

        # add the uniqueness constraint the assignment asks for
        _dao.collection.create_index("email", unique=True)

        yield _dao

        # final cleanup
        _dao.collection.drop()
        client.close()
