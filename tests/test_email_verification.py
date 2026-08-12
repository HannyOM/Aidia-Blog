import json
import pytest
from urllib.error import HTTPError

from bloggr import create_app
from bloggr.email_verification import verify_email
from bloggr.models import User


@pytest.fixture
def nodb_app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "MAILBOXLAYER_ACCESS_KEY": None,
        "MAILBOXLAYER_API_URL": None,
    })
    return app


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _enable_verification(app):
    app.config["MAILBOXLAYER_ACCESS_KEY"] = "test-key"


def _disable_email_sending(monkeypatch):
    monkeypatch.setattr(
        "bloggr.email_service.ResendEmailService.send_email",
        lambda self, **kwargs: None,
    )


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"format_valid": True, "mx_found": True}, True),
        ({"format_valid": True, "mx_found": True, "smtp_check": False}, True),
        ({"format_valid": True, "mx_found": True, "catch_all": True, "role": True, "disposable": True}, True),
        ({"format_valid": False, "mx_found": True}, False),
        ({"format_valid": True, "mx_found": False}, False),
        ({"format_valid": False, "mx_found": False}, False),
    ],
)
def test_verify_email_verdicts(nodb_app, monkeypatch, payload, expected):
    _enable_verification(nodb_app)
    monkeypatch.setattr(
        "bloggr.email_verification.urlopen",
        lambda request, timeout: FakeResponse(payload),
    )
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is expected


def test_verify_email_returns_none_without_key(nodb_app):
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is None


def test_verify_email_fails_open_on_api_error(nodb_app, monkeypatch):
    _enable_verification(nodb_app)
    payload = {"success": False, "error": {"info": "usage limit reached"}}
    monkeypatch.setattr(
        "bloggr.email_verification.urlopen",
        lambda request, timeout: FakeResponse(payload),
    )
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is None


def test_verify_email_fails_open_on_http_error(nodb_app, monkeypatch):
    _enable_verification(nodb_app)

    def raise_http_error(request, timeout):
        raise HTTPError("url", 429, "Too Many Requests", None, None)

    monkeypatch.setattr("bloggr.email_verification.urlopen", raise_http_error)
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is None


def test_verify_email_fails_open_on_timeout(nodb_app, monkeypatch):
    _enable_verification(nodb_app)

    def raise_timeout(request, timeout):
        raise TimeoutError("timed out")

    monkeypatch.setattr("bloggr.email_verification.urlopen", raise_timeout)
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is None


def test_verify_email_fails_open_on_invalid_json(nodb_app, monkeypatch):
    _enable_verification(nodb_app)

    class BadResponse(FakeResponse):
        def read(self):
            return b"not json"

    monkeypatch.setattr(
        "bloggr.email_verification.urlopen",
        lambda request, timeout: BadResponse({}),
    )
    with nodb_app.app_context():
        assert verify_email("someone@example.com") is None


def test_register_rejects_unverifiable_email(app, client, monkeypatch):
    _enable_verification(app)
    _disable_email_sending(monkeypatch)
    monkeypatch.setattr("bloggr.forms.verify_email", lambda email: False)

    response = client.post(
        "/register",
        data={
            "email": "fake@microsoft.com",
            "username": "newuser",
            "password": "Password123!",
            "password_confirm": "Password123!",
        },
    )

    assert response.status_code == 200
    assert b"could not be verified" in response.data
    with app.app_context():
        assert User.query.filter_by(email="fake@microsoft.com").first() is None


def test_register_allows_verified_email(app, client, monkeypatch):
    _enable_verification(app)
    _disable_email_sending(monkeypatch)
    monkeypatch.setattr("bloggr.forms.verify_email", lambda email: True)

    response = client.post(
        "/register",
        data={
            "email": "valid@example.com",
            "username": "newuser",
            "password": "Password123!",
            "password_confirm": "Password123!",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email="valid@example.com").first()
        assert user is not None
        assert [role.name for role in user.roles] == ["editor"]


def test_register_allows_verification_skipped(app, client, monkeypatch):
    _disable_email_sending(monkeypatch)

    response = client.post(
        "/register",
        data={
            "email": "valid@example.com",
            "username": "newuser",
            "password": "Password123!",
            "password_confirm": "Password123!",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(email="valid@example.com").first() is not None