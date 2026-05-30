"""Smoke tests — stateless, idempotent, read-only. Requires REQRES_API_KEY env var."""


def test_smoke_api_returns_ok(http, provider):
    # Arrange
    url = provider.users_list_url()
    params = provider.populated_page_params()
    # Act
    response = http.get(url, params=params)
    # Assert
    assert response.status_code == provider.ok


def test_smoke_response_is_json(http, provider):
    # Arrange
    url = provider.users_list_url()
    params = provider.populated_page_params()
    # Act
    response = http.get(url, params=params)
    # Assert
    assert response.headers["Content-Type"].startswith("application/json")


def test_smoke_users_list_is_non_empty(http, provider):
    # Arrange
    url = provider.users_list_url()
    params = provider.populated_page_params()
    # Act
    response = http.get(url, params=params)
    body = response.json()
    # Assert
    assert len(provider.extract_users(body)) > 0
