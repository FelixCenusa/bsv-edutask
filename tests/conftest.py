# make "src." imports work
import sys
from pathlib import Path

# repo_root/tests/conftest.py ->  two parents up is the repo root
repo_root = Path(__file__).resolve().parents[1]
backend_dir = repo_root / "backend"

# prepend so it has highest priority but can still be overridden by a venv pkg
sys.path.insert(0, str(backend_dir))


import re
import pytest
from types import SimpleNamespace

# email
@pytest.fixture
def force_email_valid(monkeypatch):
    """Patch re.fullmatch so we can flip email validity on/off."""
    def _apply(is_valid=True):
        monkeypatch.setattr(re, "fullmatch",
                            lambda _pat, _addr: bool(is_valid))
    return _apply


# dummy User model for DB isolation
class _DummyQuery:
    def __init__(self, users, explode=False):
        self._users = users
        self._explode = explode
    def filter(self, *a, **kw): return self
    def filter_by(self, *a, **kw): return self
    def all(self):
        if self._explode:
            raise Exception("DB connection failed")
        return self._users

@pytest.fixture
def fake_user_model(monkeypatch):
    """
    Replace backend.src.models.usermodel.User with a fake that returns
    the list of users you provide.

    Usage:
        fake_user_model([user1, user2])       # happy path
        fake_user_model([], explode=True)     # raise Exception from .all()
    """
    def _apply(users, explode=False):
        from types import SimpleNamespace
        dummy = _DummyQuery(users, explode)
        fake_cls = SimpleNamespace(query=dummy)
        monkeypatch.setattr(
            "backend.src.models.usermodel.User",  # adjust if path differs
            fake_cls,
            raising=True
        )
    return _apply
