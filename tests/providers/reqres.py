from .base import Provider


class ReqresProvider(Provider):
    name = "reqres"
    base_url = "https://reqres.in/api"
    requires_api_key = True
    has_pagination = True
    has_auth = True

    def populated_page_params(self): return {"page": 2}
    def empty_page_params(self):     return {"page": 999}
    def register_url(self):          return f"{self.base_url}/register"
    def login_url(self):             return f"{self.base_url}/login"

    def auth_headers(self, api_key=""):
        return {"x-api-key": api_key} if api_key else {}

    def register_payload(self):
        return {"email": "eve.holt@reqres.in", "password": "pistol"}

    def login_invalid_payload(self):
        return {"email": "peter@klaven"}

    def extract_users(self, body):      return body["data"]
    def extract_user_id(self, body):    return body["data"]["id"]
    def extract_created_id(self, body): return body["id"]  # POST create is flat, no data wrapper
    def extract_email(self, body):    return body["data"]["email"]
    def extract_token(self, body):    return body.get("token", "")
    def extract_error(self, body):    return body.get("error", "")
