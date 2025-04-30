import re
from unittest.mock import patch, MagicMock

import pytest


#  Fixtures
@pytest.fixture
def fake_dao():
    """Give every test a fresh DAO mock."""
    with patch("src.controllers.usercontroller.DAO") as dao_cls:
        yield dao_cls.return_value            # <- the DAO instance


@pytest.fixture
def controller(fake_dao):
    """Create the controller *after* DAO is patched."""
    from src.controllers.usercontroller import UserController
    return UserController(dao=fake_dao)


#  Some helper data
USER_OK = {"_id": "abc123", "email": "john@example.com"}



#  Happy path — exactly one match
def test_one_user_found(controller, fake_dao):
    fake_dao.find.return_value = [USER_OK]

    user = controller.get_user_by_email("john@example.com")

    assert user == USER_OK



#  Zero matches  ->  should return None   (known defect => xfail)
@pytest.mark.xfail(reason="returns users[0] even when list empty",
                   raises=IndexError)
def test_no_user_returns_none(controller, fake_dao):
    fake_dao.find.return_value = []

    assert controller.get_user_by_email("ghost@nowhere.net") is None


#  More than one match  ->  prints warning, returns first
def test_two_users_prints_warning_and_returns_first(controller, fake_dao, capsys):
    fake_dao.find.return_value = [
        {"_id": "id1", "email": "dupe@example.com"},
        {"_id": "id2", "email": "dupe@example.com"},
    ]

    first = controller.get_user_by_email("dupe@example.com")
    out = capsys.readouterr().out

    assert re.search(r"more than one user.*dupe@example\.com", out, re.I)
    assert first["_id"] == "id1"


#  Bad e-mail formats  ->  should raise ValueError   (validator too weak => xfail)
BAD_MAILS = ["", "no-at-sign", "two@@example.com", "white space@ex.com"]

@pytest.mark.parametrize("addr", BAD_MAILS)
@pytest.mark.xfail(reason="regex in emailValidator accepts these",
                   raises=ValueError)
def test_bad_email_raises_value_error(controller, addr):
    controller.get_user_by_email(addr)


#  DAO throws  ->  error must bubble up
def test_dao_error_is_propagated(controller, fake_dao):
    fake_dao.find.side_effect = RuntimeError("database down")

    with pytest.raises(RuntimeError, match="database down"):
        controller.get_user_by_email("john@example.com")


#  Case-insensitive & whitespace tolerant look-ups
@pytest.mark.parametrize(
    "supplied, stored",
    [
        ("John@Example.com", "john@example.com"),      # upper/lower case
        ("  john@example.com  ", "john@example.com"),  # leading / trailing blanks
    ],
)
def test_case_and_space_dont_matter(controller, fake_dao, supplied, stored):
    fake_dao.find.return_value = [{"_id": "abc123", "email": stored}]

    user = controller.get_user_by_email(supplied)

    assert user["_id"] == "abc123"
