"""Unit tests for src/validators.py — no network calls."""
import pytest
from src.validators import (
    validate_user,
    validate_list_response,
    validate_create_response,
    validate_register_payload,
)


class TestValidateListResponse:
    def test_valid_payload_passes(self):
        # Arrange
        payload = {"page": 2, "per_page": 6, "total": 12, "total_pages": 2, "data": [{"id": 7}]}
        # Act
        result = validate_list_response(payload)
        # Assert
        assert result is payload

    @pytest.mark.parametrize("payload,match", [
        ({"page": 1, "total": 6, "total_pages": 1}, "data"),
        ({"page": 1, "total": 1, "total_pages": 1, "data": "not-a-list"}, "list"),
    ])
    def test_invalid_payload_raises_value_error(self, payload, match):
        # Act / Assert
        with pytest.raises(ValueError, match=match):
            validate_list_response(payload)


class TestValidateSingleUser:
    def test_valid_user_passes(self):
        # Arrange
        user = {
            "id": 1, "email": "george.bluth@reqres.in",
            "first_name": "George", "last_name": "Bluth",
            "avatar": "https://reqres.in/img/faces/1-image.jpg",
        }
        # Act
        result = validate_user(user)
        # Assert
        assert result["id"] == user["id"]

    def test_missing_email_raises_value_error(self):
        # Arrange
        user = {"id": 1, "first_name": "X", "last_name": "Y", "avatar": "url"}
        # Act / Assert
        with pytest.raises(ValueError, match="email"):
            validate_user(user)

    def test_wrong_id_type_raises_type_error(self):
        # Arrange
        user = {
            "id": "not-an-int", "email": "a@b.com",
            "first_name": "A", "last_name": "B", "avatar": "url",
        }
        # Act / Assert
        with pytest.raises(TypeError, match="id"):
            validate_user(user)


class TestValidateCreateResponse:
    def test_valid_create_response_passes(self):
        # Arrange
        payload = {"name": "morpheus", "job": "leader", "id": "731", "createdAt": "2024-01-01T00:00:00.000Z"}
        # Act
        result = validate_create_response(payload)
        # Assert
        assert result["id"] == payload["id"]

    @pytest.mark.parametrize("payload,match", [
        ({"name": "morpheus", "createdAt": "2024-01-01T00:00:00.000Z"}, "id"),
        ({"name": "morpheus", "id": "", "createdAt": "2024-01-01T00:00:00.000Z"}, "non-empty"),
    ])
    def test_invalid_payload_raises_value_error(self, payload, match):
        # Act / Assert
        with pytest.raises(ValueError, match=match):
            validate_create_response(payload)


class TestValidateRegisterPayload:
    def test_valid_payload_passes(self):
        # Arrange
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        # Act
        result = validate_register_payload(payload)
        # Assert
        assert result is payload

    @pytest.mark.parametrize("payload,match", [
        ({"email": "eve.holt@reqres.in"}, "password"),
        ({"email": "", "password": "pistol"}, "email"),
    ])
    def test_invalid_payload_raises_value_error(self, payload, match):
        # Act / Assert
        with pytest.raises(ValueError, match=match):
            validate_register_payload(payload)
