# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests closing the env/config gap flagged by mutation testing
across every tool suite so far: nothing exercised how server.py reads
PRACTICE_API_URL/PRACTICE_API_TOKEN or builds the client from them,
because the mock_client fixture swaps server.client out *after* the
module already imported once.

These tests reload server.py under controlled env conditions instead of
relying on the module-import-time state conftest.py already set up.
Contract being specified:
  - Missing PRACTICE_API_TOKEN at import time raises a RuntimeError whose
    message names that exact variable -- not a bare KeyError traceback.
  - Missing PRACTICE_API_URL does the same, naming that variable.
  - The client is built from whatever is actually in the environment,
    not a hardcoded fallback -- proven by using non-default fake values
    and checking they ended up on the constructed client.

Implementer: this requires changing the two bare os.environ[...] lookups
in server.py into something that raises a clear RuntimeError on a missing
key instead of letting KeyError propagate. That's the only change this
file should require -- nothing about the five existing tools needs to
move.

No network, no real token: every value here is an obvious fake.
"""

import importlib

import pytest

import server as server_module


@pytest.fixture
def reload_server_with_env(monkeypatch):
    """Reload server.py under a specific, controlled env, then restore
    a known-good fake env and reload again at teardown so later test
    files (which import `server` expecting it to already be in a good
    state) aren't left looking at whatever this test broke it into."""

    def _reload(url="not-set", token="not-set"):
        if url is None:
            monkeypatch.delenv("PRACTICE_API_URL", raising=False)
        else:
            monkeypatch.setenv("PRACTICE_API_URL", url)
        if token is None:
            monkeypatch.delenv("PRACTICE_API_TOKEN", raising=False)
        else:
            monkeypatch.setenv("PRACTICE_API_TOKEN", token)
        return importlib.reload(server_module)

    yield _reload

    monkeypatch.setenv("PRACTICE_API_URL", "https://practice.fhsucyber.com")
    monkeypatch.setenv("PRACTICE_API_TOKEN", "fake-token-not-real")
    importlib.reload(server_module)


def test_server_raises_clear_error_when_token_missing(reload_server_with_env):
    with pytest.raises(RuntimeError, match="PRACTICE_API_TOKEN"):
        reload_server_with_env(url="https://example.test", token=None)


def test_server_raises_clear_error_when_url_missing(reload_server_with_env):
    with pytest.raises(RuntimeError, match="PRACTICE_API_URL"):
        reload_server_with_env(url=None, token="fake-token-not-real")


def test_server_builds_client_from_env_values_not_a_hardcoded_fallback(reload_server_with_env):
    mod = reload_server_with_env(
        url="https://not-the-real-default.test",
        token="some-other-fake-token",
    )

    assert mod.client.base == "https://not-the-real-default.test"
    assert mod.client.headers["Authorization"] == "Bearer some-other-fake-token"
