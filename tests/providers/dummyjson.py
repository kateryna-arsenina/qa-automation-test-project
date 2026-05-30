from .base import Provider


class DummyJsonProvider(Provider):
    name = "dummyjson"
    base_url = "https://dummyjson.com"
    has_pagination = True
    has_auth = True
    no_content = 200  # DELETE returns 200 + full deleted object

    def populated_page_params(self): return {"limit": 10, "skip": 10}
    def empty_page_params(self):     return {"limit": 10, "skip": 9990}
    def create_user_url(self):       return f"{self.base_url}/users/add"
    def login_url(self):             return f"{self.base_url}/auth/login"

    def create_user_payload(self):
        return {"firstName": "Morpheus", "lastName": "Test", "age": 30}

    def login_invalid_payload(self):
        return {"username": "emilys"}  # missing password → 400

    def extract_users(self, body):   return body["users"]
    def extract_user_id(self, body): return body["id"]
    def extract_email(self, body):   return body["email"]
    def extract_token(self, body):   return body.get("accessToken", body.get("token", ""))
    def extract_error(self, body):   return body.get("message", body.get("error", ""))
