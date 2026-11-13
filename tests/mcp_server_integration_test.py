# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7 Integration Tests

"""Live-API integration tests for server.py's tools, following the same
pattern as MP1's tests/integration_test.py: skipped entirely unless a
real PRACTICE_API_TOKEN is set, no token ever hardcoded, temp_post
cleans up after itself regardless of outcome.

Difference from MP1's version: server.py's tools never raise -- they
catch the client's exceptions and return {"error": "..."}. So where MP1
used pytest.raises(...), these assert on the returned error dict
instead. That's the actual thing this suite is for: proving the real
API's real error responses come back through the tool layer as the
same clear dict the mocked unit tests already specify, not just that
the client raises correctly in isolation (test_practice_hub_client.py
already covers that, with a mocked response).

This only makes sense to run once server.py actually exists and a real
PRACTICE_API_TOKEN is exported in the shell -- it's a one-time-per-change
manual run, not something CI should execute unattended.
"""

import importlib
import os

import pytest

import server

TOKEN = os.environ.get("PRACTICE_API_TOKEN")

pytestmark = pytest.mark.skipif(
    not TOKEN, reason="PRACTICE_API_TOKEN not set -- skipping live API integration tests"
)


@pytest.fixture
def temp_post():
    """Creates a real post through the create_post tool, yields its
    return value, deletes it afterward regardless of what the test did
    to it."""
    post = server.create_post(
        title="MP7 Integration Test Post",
        body="Created by server.py integration suite",
        tags=["integration-test"],
    )
    assert "error" not in post, f"setup failed, could not create post: {post}"
    yield post
    result = server.delete_post(post["id"])
    if isinstance(result, dict) and "error" in result:
        assert "Not found" in result["error"], f"unexpected cleanup failure: {result}"


# CRUD integration tests, implicitly tests the not-found error path too

def test_create_post():
    post = server.create_post(title="Create Test", body="body text", tags=["test"])
    assert post["title"] == "Create Test"
    assert post["id"] is not None
    server.delete_post(post["id"])


def test_read_post(temp_post):
    fetched = server.get_post(temp_post["id"])
    assert fetched["id"] == temp_post["id"]
    assert fetched["title"] == temp_post["title"]


def test_update_post(temp_post):
    updated = server.update_post(temp_post["id"], title="Updated Title")
    assert updated["title"] == "Updated Title"

    refetched = server.get_post(temp_post["id"])
    assert refetched["title"] == "Updated Title"


def test_delete_post_removes_it(temp_post):
    result = server.delete_post(temp_post["id"])
    assert result is None

    refetched = server.get_post(temp_post["id"])
    assert refetched == {"error": "Not found: the requested resource does not exist."}


def test_full_crud_cycle():
    created = server.create_post(title="Full Cycle Test", body="start", tags=["cycle"])
    assert created["title"] == "Full Cycle Test"

    fetched = server.get_post(created["id"])
    assert fetched["id"] == created["id"]

    updated = server.update_post(created["id"], body="changed")
    assert updated["body"] == "changed"

    server.delete_post(created["id"])
    refetched = server.get_post(created["id"])
    assert refetched == {"error": "Not found: the requested resource does not exist."}


# Error-handling integration tests -- same cases as MP1's, re-pointed at
# the tool layer so they prove the real API's error responses survive
# the catch-and-format step, not just that the raw client raises.

def test_bad_token_returns_clear_message(monkeypatch):
    """Swap in a deliberately wrong token, reload server.py so its
    module-level client is rebuilt against it, confirm the tool returns
    the clear error dict instead of propagating anything. Restores the
    real token and reloads again afterward so later tests aren't left
    pointed at a client that can't authenticate."""
    monkeypatch.setenv("PRACTICE_API_TOKEN", "invalid-token-xyz")
    reloaded = importlib.reload(server)

    result = reloaded.list_posts()

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}

    monkeypatch.setenv("PRACTICE_API_TOKEN", TOKEN)
    importlib.reload(server)


def test_forbidden_returns_clear_message():
    """Post id 4 is assumed to belong to another user on the shared
    class API, same assumption MP1's test_403_raises_forbidden_error
    made -- carried over as-is, not something new being assumed here."""
    result = server.update_post(4, title="Trying to edit someone else's post")

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_malformed_returns_clear_message():
    result = server.create_post(title="", body="", tags="not-a-list")

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


# Two cases the docs page (practice.fhsucyber.com/docs-guide) leaves
# genuinely unspecified -- "tags defaults to none" doesn't say what wire
# shape that takes, and the page says outright that what happens when
# `tag` is omitted from list_posts is "an inference, not a stated rule."
# No mock can answer either one without guessing, so these ask the real
# API directly instead of asserting a shape pulled from reading client.py.

def test_create_post_with_no_tags_has_no_tags_on_the_real_api():
    """Whatever representation the real API uses for "no tags" --- an
    empty list, a missing key, null --- it must not be a non-empty list.
    Deliberately not pinned to one exact shape, since the docs don't
    commit to one; this only rules out the wrong answer (tags silently
    getting populated with something)."""
    post = server.create_post(title="MP7 no-tags test", body="checking real default")
    assert "error" not in post, f"setup failed: {post}"
    try:
        assert not post.get("tags")
    finally:
        server.delete_post(post["id"])


def test_list_posts_with_no_tag_filter_still_returns_a_tagged_post(temp_post):
    """temp_post is created with tags=["integration-test"]. If omitting
    `tag` from list_posts() secretly filtered to untagged-only posts (one
    of the documented-as-unstated possibilities), temp_post would be
    missing from this result. This only checks that it isn't -- it does
    not assert anything about posts belonging to other users."""
    results = server.list_posts()
    assert not (isinstance(results, dict) and "error" in results), f"list_posts failed: {results}"

    returned_ids = [p["id"] for p in results]
    assert temp_post["id"] in returned_ids
