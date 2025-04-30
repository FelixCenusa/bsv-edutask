import pytest, pymongo

GOOD = {"email": "ann@example.com"}
MISSING = {}
EXTRA = {"email": "bob@example.com", "note": "hello"}
DUPE  = {"email": "ann@example.com"}

def test_create_ok(dao):
    _id = dao.create(GOOD)
    found = dao.collection.find_one({"_id": _id})
    assert found["email"] == GOOD["email"]

@pytest.mark.parametrize("bad", [MISSING])
def test_validator_blocks_bad_doc(dao, bad):
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(bad)

def test_optional_field_allowed(dao):
    _id = dao.create(EXTRA)
    found = dao.collection.find_one({"_id": _id})
    assert found["note"] == "hello"

def test_unique_index_violation(dao):
    dao.create(GOOD)
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        dao.create(DUPE)

def test_server_down_bubbles_up(dao, monkeypatch):
    monkeypatch.setattr(
        dao.collection, "insert_one",
        lambda *_: (_ for _ in ()).throw(
            pymongo.errors.ServerSelectionTimeoutError("down"))
    )
    with pytest.raises(pymongo.errors.ServerSelectionTimeoutError):
        dao.create(GOOD)
