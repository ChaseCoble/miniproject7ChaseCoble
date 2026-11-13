# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests for the delete_post tool.

MP1's delete_post always returns None (client._handle_response is called
for its side effect -- raising on error -- and the method itself returns
None regardless). So there's no "passthrough" return value to test here;
success just means no error dict came back. Same TypeError case as
get_post/update_post (post_id isinstance check), same five typed
exceptions. No network: server.client is a MagicMock(spec=PracticeHubClient).
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


def test_delete_post_returns_none_on_success(mock_client):
    mock_client.delete_post.return_value = None

    result = server.delete_post(3)

    assert result is None


def test_delete_post_forwards_post_id_to_the_client(mock_client):
    mock_client.delete_post.return_value = None

    server.delete_post(9)

    mock_client.delete_post.assert_called_once_with(9)


def test_delete_post_returns_clear_message_on_bad_token(mock_client):
    mock_client.delete_post.side_effect = BadTokenError("Authentication failed: token missing, expired, or invalid.")

    result = server.delete_post(1)

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}


def test_delete_post_returns_clear_message_on_forbidden(mock_client):
    mock_client.delete_post.side_effect = ForbiddenError("Access denied: you do not have permission for this action.")

    result = server.delete_post(1)

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_delete_post_returns_clear_message_on_not_found(mock_client):
    mock_client.delete_post.side_effect = NotFoundError("Not found: the requested resource does not exist.")

    result = server.delete_post(999)

    assert result == {"error": "Not found: the requested resource does not exist."}


def test_delete_post_returns_clear_message_on_malformed(mock_client):
    mock_client.delete_post.side_effect = MalformedError("Unprocessable request: the submitted data was invalid.")

    result = server.delete_post(1)

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


def test_delete_post_returns_clear_message_on_rate_limited(mock_client):
    mock_client.delete_post.side_effect = RateLimitedError("Rate limited: too many requests, try again later.")

    result = server.delete_post(1)

    assert result == {"error": "Rate limited: too many requests, try again later."}


def test_delete_post_returns_clear_message_on_conflict(mock_client):
    mock_client.delete_post.side_effect = ConflictError("Conflict: the request conflicts with the current state of the resource.")

    result = server.delete_post(1)

    assert result == {"error": "Conflict: the request conflicts with the current state of the resource."}


def test_delete_post_returns_clear_message_on_locked(mock_client):
    mock_client.delete_post.side_effect = LockedError("Locked: the resource is temporarily locked and cannot be modified right now.")

    result = server.delete_post(1)

    assert result == {"error": "Locked: the resource is temporarily locked and cannot be modified right now."}


def test_delete_post_returns_clear_message_on_invalid_post_id_type(mock_client):
    mock_client.delete_post.side_effect = TypeError("post_id must be an int, got str")

    result = server.delete_post("not-an-int")

    assert result == {"error": "post_id must be an int, got str"}
