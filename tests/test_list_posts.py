# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Failing tests for the list_posts tool, written before server.py exists.

Contract this test file is specifying:
  - list_posts(mine, tag) calls client.list_posts(mine=mine, tag=tag) and
    returns exactly what the client returned -- no reshaping, no wrapping.
    Chase's call: "the returns should be the same as in mp1."
  - Each of the client's five typed exceptions is caught and turned into
    {"error": "<the exception's own message>"} rather than propagating.
    Reusing the client's existing message text (already written to be
    generic/non-leaking in _ERRORS) avoids inventing a second, possibly
    inconsistent, copy of the same wording at the tool layer.
  - None of this touches the network: server.client is swapped for a
    MagicMock(spec=PracticeHubClient) by the mock_client fixture.
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


def test_list_posts_returns_exactly_what_the_client_returns(mock_client):
    fake_posts = [{"id": 1, "title": "first post"}, {"id": 2, "title": "second post"}]
    mock_client.list_posts.return_value = fake_posts

    result = server.list_posts()

    assert result is fake_posts


def test_list_posts_forwards_mine_and_tag_to_the_client(mock_client):
    mock_client.list_posts.return_value = []

    server.list_posts(mine=True, tag="python")

    mock_client.list_posts.assert_called_once_with(mine=True, tag="python")


def test_list_posts_defaults_mine_false_and_tag_none(mock_client):
    mock_client.list_posts.return_value = []

    server.list_posts()

    mock_client.list_posts.assert_called_once_with(mine=False, tag=None)


def test_list_posts_returns_clear_message_on_bad_token(mock_client):
    mock_client.list_posts.side_effect = BadTokenError("Authentication failed: token missing, expired, or invalid.")

    result = server.list_posts()

    assert result == {"error": "Authentication failed: token missing, expired, or invalid."}


def test_list_posts_returns_clear_message_on_forbidden(mock_client):
    mock_client.list_posts.side_effect = ForbiddenError("Access denied: you do not have permission for this action.")

    result = server.list_posts()

    assert result == {"error": "Access denied: you do not have permission for this action."}


def test_list_posts_returns_clear_message_on_not_found(mock_client):
    mock_client.list_posts.side_effect = NotFoundError("Not found: the requested resource does not exist.")

    result = server.list_posts()

    assert result == {"error": "Not found: the requested resource does not exist."}


def test_list_posts_returns_clear_message_on_malformed(mock_client):
    mock_client.list_posts.side_effect = MalformedError("Unprocessable request: the submitted data was invalid.")

    result = server.list_posts()

    assert result == {"error": "Unprocessable request: the submitted data was invalid."}


def test_list_posts_returns_clear_message_on_rate_limited(mock_client):
    mock_client.list_posts.side_effect = RateLimitedError("Rate limited: too many requests, try again later.")

    result = server.list_posts()

    assert result == {"error": "Rate limited: too many requests, try again later."}


def test_list_posts_returns_clear_message_on_conflict(mock_client):
    mock_client.list_posts.side_effect = ConflictError("Conflict: the request conflicts with the current state of the resource.")

    result = server.list_posts()

    assert result == {"error": "Conflict: the request conflicts with the current state of the resource."}


def test_list_posts_returns_clear_message_on_locked(mock_client):
    mock_client.list_posts.side_effect = LockedError("Locked: the resource is temporarily locked and cannot be modified right now.")

    result = server.list_posts()

    assert result == {"error": "Locked: the resource is temporarily locked and cannot be modified right now."}


def test_list_posts_does_not_touch_the_real_network(mock_client):
    """Sanity check on the test setup itself, not on server.py: if this
    fails, the mock_client fixture isn't actually wired in and every test
    above is meaningless."""
    mock_client.list_posts.return_value = []

    server.list_posts()

    assert mock_client.list_posts.called
