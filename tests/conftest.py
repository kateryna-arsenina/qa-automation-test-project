import json
import logging
import os
import time

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_log = logging.getLogger("qa.retry")

from tests.providers import get_provider
from tests.constants import SCHEMAS_DIR


_TRANSIENT = {429, 502}
_SOURCES = ("reqres", "dummyjson", "jsonplaceholder")

# ── Layer coverage ────────────────────────────────────────────────────────────
_LAYER_MINIMUMS = {"unit": 1, "integration": 4, "smoke": 1}
_layer_counts: dict = {}


def pytest_collection_finish(session) -> None:
    counts: dict = {layer: 0 for layer in _LAYER_MINIMUMS}
    for item in session.items:
        path = str(item.fspath).replace("\\", "/")
        for layer in counts:
            if f"/tests/{layer}/" in path:
                counts[layer] += 1
                break
    _layer_counts.update(counts)


def pytest_sessionfinish(session, exitstatus) -> None:
    active_layers = [l for l in _LAYER_MINIMUMS if _layer_counts.get(l, 0) > 0]
    counts_str = ", ".join(f"{l}={_layer_counts.get(l, 0)}" for l in _LAYER_MINIMUMS)

    # Only enforce cross-layer minimums when the run spans more than one layer
    if len(active_layers) <= 1:
        print(f"\n[layer-coverage] {counts_str} (subset run — skipping cross-layer check)")
        return

    violations = [
        f"  {layer}: need >= {minimum}, collected {_layer_counts.get(layer, 0)}"
        for layer, minimum in _LAYER_MINIMUMS.items()
        if _layer_counts.get(layer, 0) < minimum
    ]
    if violations:
        print("\n[layer-coverage] FAIL — minimum thresholds not met:")
        for v in violations:
            print(v)
        session.exitstatus = 1
    else:
        print(f"\n[layer-coverage] PASS ({counts_str})")


def _test_type(nodeid: str) -> str:
    if "/unit/" in nodeid or "\\unit\\" in nodeid:
        return "Unit"
    if "/integration/" in nodeid or "\\integration\\" in nodeid:
        return "Integration"
    if "/smoke/" in nodeid or "\\smoke\\" in nodeid:
        return "Smoke"
    return "-"


def _readable_title(nodeid: str) -> str:
    name = nodeid.split("::")[-1]
    if "[" in name:
        func, params = name.split("[", 1)
        func = func.removeprefix("test_").replace("_", " ")
        params = params.rstrip("]").replace("-", " ")
        return f"{func} ({params})"
    return name.removeprefix("test_").replace("_", " ")


def pytest_html_results_table_header(cells) -> None:
    cells.insert(1, "<th>Type</th>")
    cells.insert(2, "<th>Description</th>")


def pytest_html_results_table_row(report, cells) -> None:
    test_type = _test_type(report.nodeid)
    title = _readable_title(report.nodeid)
    type_colors = {"Unit": "#5b5ea6", "Integration": "#0066cc", "Smoke": "#cc6600"}
    color = type_colors.get(test_type, "#555")
    cells.insert(
        1,
        f"<td style='white-space:nowrap;color:{color};font-weight:bold'>{test_type}</td>",
    )
    cells.insert(2, f"<td style='min-width:220px'>{title.capitalize()}</td>")


def pytest_html_results_summary(prefix, summary, postfix) -> None:
    rows = ""
    all_pass = True
    for layer, minimum in _LAYER_MINIMUMS.items():
        actual = _layer_counts.get(layer, 0)
        ok = actual >= minimum
        if not ok:
            all_pass = False
        color = "#2d862d" if ok else "#cc0000"
        badge = "PASS" if ok else "FAIL"
        rows += (
            f"<tr>"
            f"<td style='padding:4px 12px'>{layer}</td>"
            f"<td style='padding:4px 12px;text-align:center'>{actual}</td>"
            f"<td style='padding:4px 12px;text-align:center'>{minimum}</td>"
            f"<td style='padding:4px 12px;text-align:center;"
            f"color:{color};font-weight:bold'>{badge}</td>"
            f"</tr>"
        )
    header_color = "#2d862d" if all_pass else "#cc0000"
    prefix.extend([
        "<h2 style='margin-top:1.5em'>Layer Coverage</h2>",
        "<table border='1' style='border-collapse:collapse;margin-bottom:1.5em;font-size:0.95em'>",
        "<thead><tr style='background:#f0f0f0'>",
        "<th style='padding:4px 12px'>Layer</th>",
        "<th style='padding:4px 12px'>Collected</th>",
        "<th style='padding:4px 12px'>Minimum</th>",
        f"<th style='padding:4px 12px;color:{header_color}'>Status</th>",
        "</tr></thead>",
        f"<tbody>{rows}</tbody>",
        "</table>",
    ])


class SourceUnavailableError(Exception):
    """Raised when a source returns 429/502 on both the original request and one retry."""

    def __init__(self, status: int, source: str):
        alts = " or ".join(f"TEST_SOURCE={s}" for s in _SOURCES if s != source)
        reason = "rate-limited" if status == 429 else "unavailable"
        super().__init__(
            f"{source} {reason} (HTTP {status}) — switch source: {alts}"
        )


class _SmartSession(requests.Session):
    """Session that retries 429/502 once, then raises SourceUnavailableError."""

    source_name: str = ""

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 10)
        resp = super().request(*args, **kwargs)
        if resp.status_code in _TRANSIENT:
            reason = "rate-limited" if resp.status_code == 429 else "unavailable"
            _log.warning(
                "%s %s (HTTP %s) — retrying in 1 s ...",
                self.source_name, reason, resp.status_code,
            )
            time.sleep(1)
            resp = super().request(*args, **kwargs)
            if resp.status_code in _TRANSIENT:
                alts = " or ".join(f"TEST_SOURCE={s}" for s in _SOURCES if s != self.source_name)
                _log.warning(
                    "%s still %s after retry — test will be marked xfail. "
                    "Switch source: %s",
                    self.source_name, reason, alts,
                )
                raise SourceUnavailableError(resp.status_code, self.source_name)
        return resp


@pytest.fixture(scope="session")
def provider():
    return get_provider(os.environ.get("TEST_SOURCE", "reqres"))


@pytest.fixture(scope="session")
def schemas(provider):
    path = os.path.join(SCHEMAS_DIR, provider.name, "schemas.json")
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def http(provider):
    """Shared HTTP session for the active provider. Do not mutate headers/cookies."""
    headers = {"Accept": "application/json"}

    if provider.requires_api_key:
        key = os.environ.get("REQRES_API_KEY", "")
        if not key:
            pytest.skip("REQRES_API_KEY env var not set — skipping network tests")
        headers.update(provider.auth_headers(key))

    session = _SmartSession()
    session.source_name = provider.name
    session.headers.update(headers)
    # Transport-level retry only for connection errors, not status codes
    # (429/502 are handled by _SmartSession.request above)
    session.mount("https://", HTTPAdapter(
        max_retries=Retry(total=1, backoff_factor=0.5, status_forcelist=[503, 504])
    ))

    yield session
    session.close()


@pytest.fixture(autouse=True)
def _xfail_on_source_unavailable():
    """Convert SourceUnavailableError into an xfail with a human-readable hint."""
    try:
        yield
    except SourceUnavailableError as exc:
        pytest.xfail(str(exc))
