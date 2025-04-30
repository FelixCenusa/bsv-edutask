# backend/test/integration/test_dao_create.py
# Integration-level checks for DAO.create ↔ MongoDB validator

import pytest
import pymongo

# Test data ── matches the users collection validator

GOOD = {
    "firstName": "John",
    "lastName":  "Doe",
    "email":     "john@example.com",
}

EXTRA = {
    "firstName": "Jane",
    "lastName":  "Roe",
    "email":     "jane@example.com",
    "note":      "hello",           # optional field – should be accepted
}

# bad doc – missing mandatory first/last name
MISSING = {"email": "no_name@example.com"}

# duplicate of GOOD (violates unique-e-mail index)
DUPE = GOOD.copy()

# Happy path
def test_create_ok(dao):
    doc = dao.create(GOOD)                 # DAO returns the whole document
    assert doc["email"] == GOOD["email"]   # round-trip success


# Validator rejects incomplete data
@pytest.mark.parametrize("bad", [MISSING])
def test_validator_blocks_bad_doc(dao, bad):
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(bad)


# Optional properties are tolerated
def test_optional_field_allowed(dao):
    doc = dao.create(EXTRA)
    assert doc["note"] == "hello"


# Unique index enforced by MongoDB
def test_unique_index_violation(dao):
    dao.create(GOOD)                                         # first insert OK
    with pytest.raises(pymongo.errors.DuplicateKeyError):    # second fails
        dao.create(DUPE)


# Network / server error bubbles up unchanged
def test_server_down_bubbles_up(dao, monkeypatch):
    # monkey-patch insert_one to simulate a connection error
    monkeypatch.setattr(
        dao.collection,
        "insert_one",
        lambda *_: (_ for _ in ()).throw(
            pymongo.errors.ServerSelectionTimeoutError("down")
        ),
    )
    with pytest.raises(pymongo.errors.ServerSelectionTimeoutError):
        dao.create(GOOD)
