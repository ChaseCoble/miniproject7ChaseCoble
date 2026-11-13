# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests for the update_post tool.

Same contract as the other tools: passthrough on success,
{"error": "..."} on any of the client's five typed exceptions, plus the
same TypeError case as get_post since MP1's update_post also does
isinstance(post_id, int) validation. update_post takes arbitrary
**fields (title=..., body=..., tags=...) per MP1's signature
update_post(self, post_id, **fields) -- the tool forwards whatever
fields it's given, same as MP1, rather than hard-coding a fixed set.
No network: server.client is a MagicMock(spec=PracticeHubClient).
"""

import server
from src.exceptions import (
    BadTokenError,
    ForbiddenError,
    NotFoundError,
    MalformedError,
    RateLimitedError,
    ConflictError,
    LockedError,
)


def test_update_post_returns_exactly_what_the_client_returns(mock_client):
    fake_post = {"id": 3, "title": "updated title"}
    mock_client.update_post.return_value = fake_post

    result = server.update_post(3, title="updated title")

    assert result is fake_post


def test_update_post_forwards_post_id_and_fields_to_the_client(mock_client):
    mock_client.update_post.return_value = {}

    server.update_post(5, title="new title", body="new body")

    mock_client.update_post.assert_called_once_with(5, title="new title", body="new body")


def test_update_post_forwards_tags_to_the_client(mock_client):
    mock_client.update_post.return_value = {}

    server.update_post(5, tags=["python", "mcp"])

    mock_client.update_post.assert_called_once_with(5, tags=["python", "mcp"])


def test_update_post_returns_clear_message_on_bad_token(mock_client):
    mock_client.update_post.side_effect = BadTokenError("Authentication failed: token missing, expired, or invalid.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}


def test_update_post_returns_clear_message_on_forbidden(mock_client):
    mock_client.update_post.side_effect = ForbiddenError("Access denied: you do not have permission for this action.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_update_post_returns_clear_message_on_not_found(mock_client):
    mock_client.update_post.side_effect = NotFoundError("Not found: the requested resource does not exist.")

    result = server.update_post(999, title="x")

    assert result == {"error": "Not found: the requested resource does not exist."}


def test_update_post_returns_clear_message_on_malformed(mock_client):
    mock_client.update_post.side_effect = MalformedError("Unprocessable request: the submitted data was invalid.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


def test_update_post_returns_clear_message_on_rate_limited(mock_client):
    mock_client.update_post.side_effect = RateLimitedError("Rate limited: too many requests, try again later.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Rate limited: too many requests, try again later."}


def test_update_post_returns_clear_message_on_conflict(mock_client):
    mock_client.update_post.side_effect = ConflictError("Conflict: the request conflicts with the current state of the resource.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Conflict: the request conflicts with the current state of the resource."}


def test_update_post_returns_clear_message_on_locked(mock_client):
    mock_client.update_post.side_effect = LockedError("Locked: the resource is temporarily locked and cannot be modified right now.")

    result = server.update_post(1, title="x")

    assert result == {"error": "Locked: the resource is temporarily locked and cannot be modified right now."}


def test_update_post_returns_clear_message_on_invalid_post_id_type(mock_client):
    mock_client.update_post.side_effect = TypeError("post_id must be an int, got str")

    result = server.update_post("not-an-int", title="x")

    assert result == {"error": "post_id must be an int, got str"}
