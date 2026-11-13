# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

"""Protocol-layer tests, closing the gap CLAUDE.md rule 10 names: every
other test file in this suite calls a tool function directly in Python,
which (confirmed empirically) never touches the MCP protocol stack --
no Pydantic validation, no argument coercion, and no proof the function
ever reached the server's tool table. A mutant that deletes a
`@mcp.tool()` line would survive every direct-call test unchanged.

This file routes calls through the real protocol instead, using the
official in-memory session helper from mcp.shared.memory
(create_connected_server_and_client_session), verified against the
actual installed mcp==1.30.0 in this project's venv before writing any
of this -- not assumed from memory or from the SDK docs alone. It takes
the live server.mcp FastMCP object directly (its signature accepts
Server | FastMCP; no private attribute needed).

No real network: server.client is swapped for the same
MagicMock(spec=PracticeHubClient) (mock_client fixture, conftest.py)
every other tool test file uses. Only the transport between "client"
and "server" here is real; the Practice Hub API is noAsync plugin: anyio's pytest plugin (anyio.pytest_plugin) registers
itself automatically via the pytest11 entry point as soon as anyio is
installed -- and it already is, as a transitive dependency of mcp. No
new entry in requirements-dev.txt, no pytest.ini change. Tests just need
@pytest.mark.anyio and the local anyio_backend fixture below, which pins
the run to asyncio only (trio isn't installed and nothing here needs it).

"""

from unittest.mock import MagicMock

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

import server


@pytest.fixture
def anyio_backend():
    return "asyncio"


EXPECTED_TOOL_NAMES = {"list_posts", "get_post", "create_post", "update_post", "delete_post"}


@pytest.mark.anyio
async def test_all_five_tools_are_registered():
    """The actual registration check. A mutant deleting any one
    @mcp.tool() line removes that name from this list -- something no
    direct-call test can detect, since the bare function still works
    fine when called directly without ever being registered."""
    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.list_tools()
        names = {tool.name for tool in result.tools}

    assert names == EXPECTED_TOOL_NAMES


@pytest.mark.anyio
async def test_list_posts_is_callable_through_the_protocol(mock_client):
    mock_client.list_posts.return_value = [{"id": 1, "title": "hi"}]

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("list_posts", {"mine": False})

    assert result.isError is False
    mock_client.list_posts.assert_called_once()


@pytest.mark.anyio
async def test_get_post_is_callable_through_the_protocol(mock_client):
    mock_client.get_post.return_value = {"id": 7}

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("get_post", {"post_id": 7})

    assert result.isError is False
    mock_client.get_post.assert_called_once_with(7)


@pytest.mark.anyio
async def test_create_post_is_callable_through_the_protocol(mock_client):
    mock_client.create_post.return_value = {"id": 1}

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("create_post", {"title": "t"})

    assert result.isError is False
    mock_client.create_post.assert_called_once()


@pytest.mark.anyio
async def test_update_post_is_callable_through_the_protocol(mock_client):
    mock_client.update_post.return_value = {"id": 1}

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("update_post", {"post_id": 1})

    assert result.isError is False
    mock_client.update_post.assert_called_once()


@pytest.mark.anyio
async def test_delete_post_is_callable_through_the_protocol(mock_client):
    mock_client.delete_post.return_value = None

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("delete_post", {"post_id": 1})

    assert result.isError is False
    mock_client.delete_post.assert_called_once_with(1)


# --- NOT YET IMPLEMENTED: these three are RED against the current
# server.py. They specify that explicit null for an unset optional
# field must work the same as omitting it -- see module docstring. ---


@pytest.mark.anyio
async def test_list_posts_accepts_explicit_null_for_optional_tag(mock_client):
    mock_client.list_posts.return_value = []

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("list_posts", {"mine": False, "tag": None})

    assert result.isError is False, result.content
    mock_client.list_posts.assert_called_once_with(mine=False, tag=None)


@pytest.mark.anyio
async def test_create_post_accepts_explicit_null_for_optional_tags(mock_client):
    mock_client.create_post.return_value = {"id": 1}

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool("create_post", {"title": "t", "body": "b", "tags": None})

    assert result.isError is False, result.content
    mock_client.create_post.assert_called_once_with(title="t", body="b", tags=None)


@pytest.mark.anyio
async def test_update_post_accepts_explicit_null_for_optional_fields(mock_client):
    mock_client.update_post.return_value = {"id": 1}

    async with create_connected_server_and_client_session(server.mcp) as session:
        result = await session.call_tool(
            "update_post", {"post_id": 1, "title": None, "body": None, "tags": None}
        )

    assert result.isError is False, result.content
    mock_client.update_post.assert_called_once_with(1)
