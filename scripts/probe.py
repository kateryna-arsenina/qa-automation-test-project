"""
Probe a provider, record live response shapes, and generate JSON Schema files.

Usage:
    python scripts/probe.py                              # reqres.in (default)
    TEST_SOURCE=dummyjson python scripts/probe.py
    TEST_SOURCE=jsonplaceholder python scripts/probe.py

Output:
    tests/schemas/<provider>/schemas.json
"""
import json
import os
import sys

import requests
from genson import SchemaBuilder

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.providers import get_provider

SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "schemas")


def _fetch(session, method, url, **kwargs):
    try:
        resp = getattr(session, method)(url, timeout=10, **kwargs)
        body = resp.json() if resp.text.strip() else None
        return resp.status_code, body
    except Exception as exc:
        return None, str(exc)


def _schema(sample):
    if sample is None:
        return {}
    builder = SchemaBuilder()
    builder.add_object(sample)
    schema = builder.to_schema()
    schema.pop("$schema", None)
    return schema


def probe(provider_name: str, api_key: str = "") -> dict:
    provider = get_provider(provider_name)
    print(f"\nProbing [{provider.name}]  {provider.base_url}")

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    if api_key:
        session.headers.update(provider.auth_headers(api_key))

    endpoints = [
        ("users_list",       "get",    provider.users_list_url(),  {"params": provider.populated_page_params()}),
        ("user_single",      "get",    provider.user_url(1),       {}),
        ("user_not_found",   "get",    provider.user_url(9999),    {}),
        ("user_create",      "post",   provider.create_user_url(), {"json": provider.create_user_payload()}),
        ("user_delete",      "delete", provider.user_url(2),       {}),
    ]
    if provider.has_pagination:
        endpoints.append(
            ("users_list_empty", "get", provider.users_list_url(), {"params": provider.empty_page_params()})
        )
    if provider.register_url():
        endpoints.append(
            ("register", "post", provider.register_url(), {"json": provider.register_payload()})
        )
    if provider.login_url():
        endpoints.append(
            ("login_invalid", "post", provider.login_url(), {"json": provider.login_invalid_payload()})
        )

    results = {}
    for name, method, url, kwargs in endpoints:
        status, body = _fetch(session, method, url, **kwargs)
        results[name] = {"status": status, "schema": _schema(body), "sample": body, "available": True}
        icon = "✅" if status else "❌"
        print(f"  {icon}  {name:<22} {status}  {url}")

    # Always write optional endpoint keys even when not probed — so tests can
    # distinguish "not yet probed" (key missing) from "probed, not supported" (available=False)
    for optional in ("users_list_empty", "register", "login_invalid"):
        if optional not in results:
            results[optional] = {"status": None, "schema": {}, "sample": None, "available": False}
            print(f"  --  {optional:<22} not supported by this source")

    out_dir = os.path.join(SCHEMAS_DIR, provider.name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "schemas.json")
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"\n  Saved → {out_path}\n")
    return results


if __name__ == "__main__":
    source = os.environ.get("TEST_SOURCE", "reqres")
    key = os.environ.get("REQRES_API_KEY", "") if source == "reqres" else ""
    probe(source, key)
