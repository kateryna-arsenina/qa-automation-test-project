"""
Source-agnostic integration tests.

Switch the API source without changing any test code:
    TEST_SOURCE=dummyjson       pytest tests/integration
    TEST_SOURCE=jsonplaceholder pytest tests/integration
    pytest                                               # default: reqres
"""
import pytest
import jsonschema


def _ok(response, expected_status):
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}: {response.text}"
    )
    return response.json()


def _validate(body, schemas, key):
    entry = schemas.get(key, {})
    if entry.get("schema"):
        jsonschema.validate(instance=body, schema=entry["schema"])


def _require_endpoint(schemas, key, source_name):
    """Skip if endpoint is absent. Distinguishes 'not probed' from 'not supported'."""
    entry = schemas.get(key)
    if entry is None:
        pytest.skip(f"{source_name}: schemas not generated yet — run make probe-all first")
    if not entry.get("available", False):
        pytest.skip(f"{source_name}: {key!r} endpoint not supported by this source")


# ── List users ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("populated", [True, False], ids=["populated-page", "empty-page"])
def test_list_users_page(http, provider, schemas, populated):
    # Arrange
    if not populated:
        _require_endpoint(schemas, "users_list_empty", provider.name)
    params = provider.populated_page_params() if populated else provider.empty_page_params()
    # Act
    body = _ok(http.get(provider.users_list_url(), params=params), provider.ok)
    _validate(body, schemas, "users_list" if populated else "users_list_empty")
    # Assert
    users = provider.extract_users(body)
    assert isinstance(users, list)
    assert (len(users) >= 1) if populated else (users == [])


# ── Single user ───────────────────────────────────────────────────────────────

def test_get_single_user_returns_correct_id(http, provider, schemas):
    # Arrange / Act
    body = _ok(http.get(provider.user_url(1)), provider.ok)
    _validate(body, schemas, "user_single")
    # Assert
    assert provider.extract_user_id(body) == 1


def test_get_single_user_has_valid_email(http, provider):
    # Arrange / Act
    body = _ok(http.get(provider.user_url(1)), provider.ok)
    # Assert
    assert "@" in provider.extract_email(body)


def test_get_unknown_user_returns_not_found(http, provider):
    # Act
    response = http.get(provider.user_url(9999))
    # Assert
    assert response.status_code == provider.not_found


# ── Create / Delete ───────────────────────────────────────────────────────────

def test_create_user_returns_created_with_id(http, provider, schemas):
    # Arrange / Act
    body = _ok(
        http.post(provider.create_user_url(), json=provider.create_user_payload()),
        provider.created,
    )
    _validate(body, schemas, "user_create")
    # Assert
    assert provider.extract_created_id(body)


def test_delete_user_returns_success(http, provider):
    # Act
    response = http.delete(provider.user_url(2))
    # Assert
    assert response.status_code == provider.no_content


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_register_returns_token(http, provider, schemas):
    # Arrange
    _require_endpoint(schemas, "register", provider.name)
    # Act
    body = _ok(http.post(provider.register_url(), json=provider.register_payload()), provider.ok)
    _validate(body, schemas, "register")
    # Assert
    assert provider.extract_token(body)


def test_login_invalid_payload_returns_error(http, provider, schemas):
    # Arrange
    _require_endpoint(schemas, "login_invalid", provider.name)
    # Act
    body = _ok(
        http.post(provider.login_url(), json=provider.login_invalid_payload()),
        provider.bad_request,
    )
    _validate(body, schemas, "login_invalid")
    # Assert
    assert provider.extract_error(body)
