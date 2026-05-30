from .base import Provider


class JsonPlaceholderProvider(Provider):
    name = "jsonplaceholder"
    base_url = "https://jsonplaceholder.typicode.com"
    has_pagination = False
    has_auth = False
    no_content = 200  # DELETE returns 200 + {}
    created = 201

    def extract_users(self, body):   return body if isinstance(body, list) else []
    def extract_user_id(self, body): return body["id"]
    def extract_email(self, body):   return body["email"]
