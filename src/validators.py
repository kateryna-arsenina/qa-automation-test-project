"""Hand-written validator functions for reqres.in response shapes."""


def validate_user(data: dict) -> dict:
    required = {"id": int, "email": str, "first_name": str, "last_name": str, "avatar": str}
    for field, ftype in required.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], ftype):
            raise TypeError(f"Field '{field}' must be {ftype.__name__}, got {type(data[field]).__name__}")
    return data


def validate_list_response(payload: dict) -> dict:
    for key in ("page", "data", "total", "total_pages"):
        if key not in payload:
            raise ValueError(f"Missing key in list response: {key}")
    if not isinstance(payload["data"], list):
        raise ValueError("'data' must be a list")
    return payload


def validate_create_response(payload: dict) -> dict:
    for key in ("id", "createdAt"):
        if key not in payload:
            raise ValueError(f"Missing key in create response: {key}")
    if not payload["id"]:
        raise ValueError("'id' must be a non-empty string")
    return payload


def validate_register_payload(payload: dict) -> dict:
    if "email" not in payload or not payload["email"]:
        raise ValueError("Register payload must contain a non-empty 'email'")
    if "password" not in payload or not payload["password"]:
        raise ValueError("Register payload must contain a non-empty 'password'")
    return payload
