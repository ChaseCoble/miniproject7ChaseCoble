# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

import os
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from src.client import PracticeHubClient
from src.exceptions import (BadTokenError, ForbiddenError, NotFoundError, ConflictError,
                            MalformedError, LockedError, RateLimitedError)

# The seven typed client exceptions. Each one's message is a fixed, generic
# string set in PracticeHubClient, so it's safe to hand back to the caller.
CLIENT_ERRORS = (BadTokenError, ForbiddenError, NotFoundError, ConflictError,
                 MalformedError, LockedError, RateLimitedError)
# get/update/delete_post also raise TypeError for a non-int post_id; that
# message is fixed in the client too.
POST_ID_ERRORS = CLIENT_ERRORS + (TypeError,)


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set; export it before starting the server.")
    return value


mcp = FastMCP("practice-hub")

client = PracticeHubClient(
    base_url=_require_env("PRACTICE_API_URL"),
    token=_require_env("PRACTICE_API_TOKEN"),
)


@mcp.tool()
def list_posts(mine: bool = False, tag: str | None = None) -> list | dict:
    """List posts on the Practice Hub. Set mine=True to return only posts
    written by the authenticated user, and pass tag to return only posts
    carrying that tag. Returns a list of post objects (id, title, body,
    tags, author, timestamps)."""
    try:
        return client.list_posts(mine=mine, tag=tag)
    except CLIENT_ERRORS as e:
        return {"error": str(e)}


@mcp.tool()
def get_post(post_id: int) -> dict:
    """Fetch one Practice Hub post by its integer id. Use this when you
    already know the post's id and need its full title, body, tags,
    author, and attachments."""
    try:
        return client.get_post(post_id)
    except POST_ID_ERRORS as e:
        return {"error": str(e)}


@mcp.tool()
def create_post(
    title: Annotated[str, Field(max_length=300)],
    body: str = "",
    tags: Annotated[list, Field(max_length=20)] | None = None,
) -> dict:
    """Create a new Practice Hub post owned by the authenticated user.
    title is required (at most 300 characters); body defaults to empty
    and tags to no tags (at most 20). Returns the created post, including
    its new id."""
    try:
        return client.create_post(title=title, body=body, tags=tags)
    except CLIENT_ERRORS as e:
        return {"error": str(e)}


@mcp.tool()
def update_post(post_id: int, title: str | None = None, body: str | None = None,
                tags: list | None = None) -> dict:
    """Change an existing post the authenticated user owns. Only the
    fields you pass (title, body, tags) are changed; omitted or null
    fields are left as they are. Returns the updated post."""
    fields = {k: v for k, v in {"title": title, "body": body, "tags": tags}.items() if v is not None}
    try:
        return client.update_post(post_id, **fields)
    except POST_ID_ERRORS as e:
        return {"error": str(e)}


@mcp.tool()
def delete_post(post_id: int) -> dict | None:
    """Permanently delete a post the authenticated user owns, by its
    integer id. This cannot be undone. Returns nothing on success, or
    {"error": ...} if the delete failed."""
    try:
        return client.delete_post(post_id)
    except POST_ID_ERRORS as e:
        return {"error": str(e)}
