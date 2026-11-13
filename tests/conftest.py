# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Shared test fixtures.

PRACTICE_API_TOKEN/PRACTICE_API_URL are set here, before any test module
imports server.py, because server.py reads them from os.environ at import
time and raises if they're missing (CLAUDE.md rule 6 + the startup-failure
behavior the test plan calls for). Values are obvious fakes -- never a
real token, and no test in this suite makes a real network call.

Real bug this file previously had, found by running the suite rather than
assumed: the setdefault() calls below run at collection time, before any
test module is imported -- that's unconditional, regardless of which
tests actually end up running. integration_test.py (yours) and
mcp_server_integration_test.py (mine) each gate on
`pytest.mark.skipif(not TOKEN, ...)`, but that only checks truthiness. In
a shell with no real PRACTICE_API_TOKEN exported, this file's fake
placeholder becomes the value TOKEN sees -- non-empty, so the skip never
fires -- and a plain `pytest tests/` sends real requests to
practice.fhsucyber.com with an obviously-wrong token instead of skipping.
Neither integration file's own code needs to change for this; the hook
below is collection-time, requires no edit to either file, and treats
both the same way.
"""

import os

_REAL_TOKEN_WAS_ALREADY_SET = bool(os.environ.get("PRACTICE_API_TOKEN"))

os.environ.setdefault("PRACTICE_API_TOKEN", "fake-token-not-real")
os.environ.setdefault("PRACTICE_API_URL", "https://practice.fhsucyber.com")

from unittest.mock import MagicMock

import pytest

import server
from src.client import PracticeHubClient


@pytest.fixture
def mock_client(monkeypatch):
    """Replace server's module-level client with a mock so no tool test
    ever touches the real Practice Hub API. spec=PracticeHubClient means
    a typo'd method name fails the test instead of silently returning
    a MagicMock."""
    mock = MagicMock(spec=PracticeHubClient)
    monkeypatch.setattr(server, "client", mock)
    return mock


def pytest_collection_modifyitems(config, items):
    """Skip every *integration_test* module outright unless a real token
    was present in the environment before this file's setdefault() ran.
    Without this, the placeholder above -- needed purely so `import
    server` doesn't raise in files that have nothing to do with the live
    API -- silently satisfies any integration test's own truthiness-only
    skip check and sends real, doomed-to-fail requests with a fake
    credential."""
    if _REAL_TOKEN_WAS_ALREADY_SET:
        return
    reason = (
        "No real PRACTICE_API_TOKEN was exported before pytest started, "
        "so this would otherwise run against the live API using "
        "conftest's fake placeholder token. Export a real "
        "PRACTICE_API_TOKEN first to run these."
    )
    for item in items:
        if "integration_test" in str(item.fspath):
            item.add_marker(pytest.mark.skip(reason=reason))
