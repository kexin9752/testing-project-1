import pytest
from pydantic import ValidationError

from app.routers.auth import RegisterRequest

VALID = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123",
    "full_name": "Alice Smith",
}


def test_valid_payload():
    req = RegisterRequest(**VALID)
    assert req.username == "alice"
    assert str(req.email) == "alice@example.com"


@pytest.mark.parametrize("username", ["ab", "a" * 51])
def test_username_length(username):
    with pytest.raises(ValidationError):
        RegisterRequest(**{**VALID, "username": username})


@pytest.mark.parametrize("password", ["short", "p" * 129])
def test_password_length(password):
    with pytest.raises(ValidationError):
        RegisterRequest(**{**VALID, "password": password})


def test_full_name_max_length():
    with pytest.raises(ValidationError):
        RegisterRequest(**{**VALID, "full_name": "A" * 101})


def test_full_name_empty():
    with pytest.raises(ValidationError):
        RegisterRequest(**{**VALID, "full_name": ""})


@pytest.mark.parametrize("email", ["not-an-email", "missing@", "@nodomain"])
def test_invalid_email(email):
    with pytest.raises(ValidationError):
        RegisterRequest(**{**VALID, "email": email})
