# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests for the get_post tool.

Same contract shape as list_posts: passthrough on success, {"error": "..."}
on any of the client's five typed exceptions. One addition here: MP1's
get_post also raises a plain TypeError (not one of the five) if post_id
isn't an int -- that's client-side input validation, not an API response,
but a model calling this tool can still pass the wrong type, so this file
also pins down that TypeError gets the same clear-message treatment
instead of propagating as a raw traceback. No network: server.client is
a MagicMock(spec=PracticeHubClient).
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


def test_get_post_returns_exactly_what_the_client_returns(mock_client):
    fake_post = {"id": 7, "title": "a post", "body": "content"}
    mock_client.get_post.return_value = fake_post

    result = server.get_post(7)

    assert result is fake_post


def test_get_post_forwards_post_id_to_the_client(mock_client):
    mock_client.get_post.return_value = {}

    server.get_post(42)

    mock_client.get_post.assert_called_once_with(42)


def test_get_post_returns_clear_message_on_bad_token(mock_client):
    mock_client.get_post.side_effect = BadTokenError("Authentication failed: token missing, expired, or invalid.")

    result = server.get_post(1)

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}


def test_get_post_returns_clear_message_on_forbidden(mock_client):
    mock_client.get_post.side_effect = ForbiddenError("Access denied: you do not have permission for this action.")

    result = server.get_post(1)

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_get_post_returns_clear_message_on_not_found(mock_client):
    mock_client.get_post.side_effect = NotFoundError("Not found: the requested resource does not exist.")

    result = server.get_post(999)

    assert result == {"error": "Not found: the requested resource does not exist."}


def test_get_post_returns_clear_message_on_malformed(mock_client):
    mock_client.get_post.side_effect = MalformedError("Unprocessable request: the submitted data was invalid.")

    result = server.get_post(1)

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


def test_get_post_returns_clear_message_on_rate_limited(mock_client):
    mock_client.get_post.side_effect = RateLimitedError("Rate limited: too many requests, try again later.")

    result = server.get_post(1)

    assert result == {"error": "Rate limited: too many requests, try again later."}


def test_get_post_returns_clear_message_on_conflict(mock_client):
    mock_client.get_post.side_effect = ConflictError("Conflict: the request conflicts with the current state of the resource.")

    result = server.get_post(1)

    assert result == {"error": "Conflict: the request conflicts with the current state of the resource."}


def test_get_post_returns_clear_message_on_locked(mock_client):
    mock_client.get_post.side_effect = LockedError("Locked: the resource is temporarily locked and cannot be modified right now.")

    result = server.get_post(1)

    assert result == {"error": "Locked: the resource is temporarily locked and cannot be modified right now."}


def test_get_post_returns_clear_message_on_invalid_post_id_type(mock_client):
    mock_client.get_post.side_effect = TypeError("post_id must be an int, got str")

    result = server.get_post("not-an-int")

    assert result == {"error": "post_id must be an int, got str"}
