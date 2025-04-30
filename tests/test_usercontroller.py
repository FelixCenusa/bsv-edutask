import pytest
from types import SimpleNamespace
from backend.src.controllers.usercontroller import get_user_by_email


def _make_user(i=0):
    return SimpleNamespace(id=i, email=f"user{i}@example.com")


def test_invalid_email_raises(force_email_valid):
    force_email_valid(False)
    with pytest.raises(ValueError):
        get_user_by_email("bad")


def test_db_exception_propagates(force_email_valid, fake_user_model):
    force_email_valid(True)
    fake_user_model([], explode=True)
    with pytest.raises(Exception):
        get_user_by_email("good@example.com")


def test_returns_none_when_zero_records(force_email_valid, fake_user_model):
    force_email_valid(True)
    fake_user_model([])
    assert get_user_by_email("none@example.com") is None


def test_returns_single_user(force_email_valid, fake_user_model):
    u = _make_user()
    force_email_valid(True)
    fake_user_model([u])
    assert get_user_by_email(u.email) is u


def test_duplicates_print_warning_and_return_first(
    capsys, force_email_valid, fake_user_model
):
    users = [_make_user(i) for i in range(3)]
    force_email_valid(True)
    fake_user_model(users)
    result = get_user_by_email("dupe@example.com")

    # Assert first user returned
    assert result is users[0]

    # Assert warning printed
    out = capsys.readouterr().out.lower()
    assert "warning" in out
