# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

import os
import pytest
from src.client import PracticeHubClient
from src.exceptions import BadTokenError, ForbiddenError, NotFoundError, MalformedError, RateLimitedError

@pytest.fixture
def client():
    return PracticeHubClient(base_url="https://practice.fhsucyber.com", token="fake-token")

@pytest.fixture
def sample_post():
    return {
        "id": 42,
        "title": "Test Post",
        "body": "Test body",
        "tags": ["test"],
        "author_id": 1,
        "author_name": "testuser",
        "created_at": "2026-09-03T14:45:17.968Z",
        "updated_at": "2026-09-03T14:45:17.968Z",
        "attachments": []
    }
@pytest.fixture
def mock_response(mocker):
    def _make(json_data, status_code=200):
        resp = mocker.Mock()
        resp.json.return_value = json_data
        resp.status_code = status_code
        resp.raise_for_status.return_value = None
        return resp
    return _make
#Single Post Get
def test_return_single_post(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_get = mocker.patch("requests.get", return_value=resp)
    result = client.get_post(42)

    mock_get.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts/42",
        headers=client.headers
    )
    assert result == sample_post
#Single Post update
def test_update_post_single_field(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_patch = mocker.patch("requests.patch", return_value=resp)

    client.update_post(42, title="New title")

    mock_patch.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts/42",
        json={"title": "New title"},
        headers=client.headers
    )

def test_update_post_multiple_fields(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_patch = mocker.patch("requests.patch", return_value=resp)

    client.update_post(42, title="New title", tags=["updated"])

    mock_patch.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts/42",
        json={"title": "New title", "tags": ["updated"]},
        headers=client.headers
    )

def test_update_post_no_fields_sends_empty_payload(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_patch = mocker.patch("requests.patch", return_value=resp)

    client.update_post(42)

    mock_patch.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts/42",
        json={},
        headers=client.headers
    )
#Single Post Delete
def test_delete_post(client, mocker):
    mock_delete = mocker.patch("requests.delete")
    mock_delete.return_value.raise_for_status.return_value = None
    client.delete_post(42)
    mock_delete.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts/42",
        headers=client.headers
    )

#Create Post
def test_create_post_sends_title_body_and_tags(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_post = mocker.patch("requests.post", return_value=resp)

    result = client.create_post("New Post", body="Some body", tags=["a", "b"])

    mock_post.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts",
        headers=client.headers,
        json={"title": "New Post", "body": "Some body", "tags": ["a", "b"]}
    )
    assert result == sample_post

def test_create_post_defaults_body_empty_and_tags_to_empty_list(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post)
    mock_post = mocker.patch("requests.post", return_value=resp)

    client.create_post("Title only")

    mock_post.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts",
        headers=client.headers,
        json={"title": "Title only", "body": "", "tags": []}
    )

#List Posts
def test_list_posts_defaults_to_mine_false_and_no_tag_filter(client, mock_response, mocker):
    resp = mock_response([])
    mock_get = mocker.patch("requests.get", return_value=resp)

    client.list_posts()

    mock_get.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts",
        headers=client.headers,
        params={"mine": False}
    )

def test_list_posts_forwards_mine_true(client, mock_response, mocker):
    resp = mock_response([])
    mock_get = mocker.patch("requests.get", return_value=resp)

    client.list_posts(mine=True)

    mock_get.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts",
        headers=client.headers,
        params={"mine": True}
    )

def test_list_posts_includes_tag_filter_only_when_given(client, mock_response, mocker):
    resp = mock_response([])
    mock_get = mocker.patch("requests.get", return_value=resp)

    client.list_posts(tag="python")

    mock_get.assert_called_once_with(
        "https://practice.fhsucyber.com/api/v1/posts",
        headers=client.headers,
        params={"mine": False, "tag": "python"}
    )

def test_list_posts_returns_exactly_what_the_client_receives(client, mock_response, sample_post, mocker):
    resp = mock_response([sample_post])
    mocker.patch("requests.get", return_value=resp)

    result = client.list_posts()

    assert result == [sample_post]

#Error-Handling Tests
def test_handle_response_200_returns_json(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=200)
    result = client._handle_response(resp)
    assert result == sample_post

def test_handle_response_401_raises(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=401)
    with pytest.raises(BadTokenError):
        client._handle_response(resp)

def test_handle_response_403_raises(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=403)
    with pytest.raises(ForbiddenError):
        client._handle_response(resp)

def test_handle_response_404_raises(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=404)
    with pytest.raises(NotFoundError):
        client._handle_response(resp)

def test_handle_response_422_raises(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=422)
    with pytest.raises(MalformedError):
        client._handle_response(resp)

def test_handle_response_429_raises(client, mock_response, sample_post, mocker):
    resp = mock_response(sample_post, status_code=429)
    with pytest.raises(RateLimitedError):
        client._handle_response(resp)


def test_handle_response_204_returns_none(client, mock_response, mocker):
    resp = mock_response(None, status_code=204)
    result = client._handle_response(resp)
    assert result is None
