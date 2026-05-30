"""
Resilience demo tests — simulate transient HTTP errors without real network calls.

Each test triggers the real _SmartSession retry logic via mocked responses so the
live WARNING log and xfail suggestion are visible in the console.

Run:  make demo-retry
"""
import pytest
from unittest.mock import MagicMock, patch

from tests.conftest import SourceUnavailableError, _SmartSession


def _fake_response(status_code: int):
    r = MagicMock()
    r.status_code = status_code
    r.text = ""
    r.content = b""
    r.headers = {}
    return r


def _trigger(provider, status_code: int) -> None:
    session = _SmartSession()
    session.source_name = provider.name
    with (
        patch("requests.Session.request", side_effect=[
            _fake_response(status_code),
            _fake_response(status_code),
        ]),
        patch("time.sleep"),
    ):
        session.get("https://example.com/simulated")


@pytest.mark.resilience
def test_rate_limited_429_retries_then_xfails(provider):
    # Arrange
    status = 429
    # Act
    try:
        _trigger(provider, status)
    except SourceUnavailableError as exc:
        # Assert — WARNING was logged live above; xfail with switch suggestion
        pytest.xfail(str(exc))


@pytest.mark.resilience
def test_server_error_5xx_retries_then_xfails(provider):
    # Arrange
    status = 502
    # Act
    try:
        _trigger(provider, status)
    except SourceUnavailableError as exc:
        # Assert — WARNING was logged live above; xfail with switch suggestion
        pytest.xfail(str(exc))
