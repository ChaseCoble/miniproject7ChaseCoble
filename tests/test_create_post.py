# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests for the create_post tool.

Same contract as list_posts/get_post: passthrough on success,
{"error": "..."} on any of the client's five typed exceptions. Unlike
get_post, MP1's create_post has no isinstance check of its own (title/
body/tags aren't type-validated client-side), so there's no extra
TypeError case to pin here -- only what MP1 actually does. No network:
server.client is a MagicMock(spec=PracticeHubClient).
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


def test_create_post_returns_exactly_what_the_client_returns(mock_client):
    fake_post = {"id": 10, "title": "new post", "body": "content", "tags": []}
    mock_client.create_post.return_value = fake_post

    result = server.create_post("new post", "content")

    assert result is fake_post


def test_create_post_forwards_title_body_and_tags_to_the_client(mock_client):
    mock_client.create_post.return_value = {}

    server.create_post("a title", "a body", ["python", "mcp"])

    mock_client.create_post.assert_called_once_with(title="a title", body="a body", tags=["python", "mcp"])


def test_create_post_defaults_body_empty_and_tags_none(mock_client):
    mock_client.create_post.return_value = {}

    server.create_post("a title")

    mock_client.create_post.assert_called_once_with(title="a title", body="", tags=None)


def test_create_post_returns_clear_message_on_bad_token(mock_client):
    mock_client.create_post.side_effect = BadTokenError("Authentication failed: token missing, expired, or invalid.")

    result = server.create_post("a title")

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}


def test_create_post_returns_clear_message_on_forbidden(mock_client):
    mock_client.create_post.side_effect = ForbiddenError("Access denied: you do not have permission for this action.")

    result = server.create_post("a title")

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_create_post_returns_clear_message_on_not_found(mock_client):
    mock_client.create_post.side_effect = NotFoundError("Not found: the requested resource does not exist.")

    result = server.create_post("a title")

    assert result == {"error": "Not found: the requested resource does not exist."}


def test_create_post_returns_clear_message_on_malformed(mock_client):
    mock_client.create_post.side_effect = MalformedError("Unprocessable request: the submitted data was invalid.")

    result = server.create_post("a title")

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


def test_create_post_returns_clear_message_on_rate_limited(mock_client):
    mock_client.create_post.side_effect = RateLimitedError("Rate limited: too many requests, try again later.")

    result = server.create_post("a title")

    assert result == {"error": "Rate limited: too many requests, try again later."}


def test_create_post_returns_clear_message_on_conflict(mock_client):
    mock_client.create_post.side_effect = ConflictError("Conflict: the request conflicts with the current state of the resource.")

    result = server.create_post("a title")

    assert result == {"error": "Conflict: the request conflicts with the current state of the resource."}


def test_create_post_returns_clear_message_on_locked(mock_client):
    mock_client.create_post.side_effect = LockedError("Locked: the resource is temporarily locked and cannot be modified right now.")

    result = server.create_post("a title")

    assert result == {"error": "Locked: the resource is temporarily locked and cannot be modified right now."}
