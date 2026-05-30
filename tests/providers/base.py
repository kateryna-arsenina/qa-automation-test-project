class Provider:
    """Base provider — subclass one per API source."""

    name: str = "base"
    base_url: str = ""
    requires_api_key: bool = False
    has_pagination: bool = False
    has_auth: bool = False

    # ── Status codes ──────────────────────────────────────────────────────────
    ok: int = 200
    created: int = 201
    no_content: int = 204
    not_found: int = 404
    bad_request: int = 400

    # ── URL builders ─────────────────────────────────────────────────────────
    def users_list_url(self) -> str:
        return f"{self.base_url}/users"

    def user_url(self, user_id: int) -> str:
        return f"{self.base_url}/users/{user_id}"

    def create_user_url(self) -> str:
        return f"{self.base_url}/users"

    def register_url(self):
        return None

    def login_url(self):
        return None

    # ── Pagination ────────────────────────────────────────────────────────────
    def populated_page_params(self) -> dict:
        return {}

    def empty_page_params(self) -> dict:
        return {}

    # ── Payloads ──────────────────────────────────────────────────────────────
    def create_user_payload(self) -> dict:
        return {"name": "morpheus", "job": "leader"}

    def register_payload(self) -> dict:
        return {}

    def login_invalid_payload(self) -> dict:
        return {}

    # ── Auth ──────────────────────────────────────────────────────────────────
    def auth_headers(self, api_key: str = "") -> dict:
        return {}

    # ── Field extractors ─────────────────────────────────────────────────────
    def extract_users(self, body) -> list:
        return body if isinstance(body, list) else []

    def extract_user_id(self, body) -> int:
        return body["id"]

    def extract_email(self, body) -> str:
        return body["email"]

    def extract_created_id(self, body):
        return body["id"]

    def extract_token(self, body) -> str:
        return body.get("token", "")

    def extract_error(self, body) -> str:
        return body.get("error", body.get("message", ""))
