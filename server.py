# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

import os

from mcp.server.fastmcp import FastMCP

from src.client import PracticeHubClient

mcp = FastMCP("practice-hub")

client = PracticeHubClient(
    base_url=os.environ["PRACTICE_API_URL"],
    token=os.environ["PRACTICE_API_TOKEN"],
)


@mcp.tool()
def list_posts(mine: bool = False, tag: str | None = None) -> list:
    """List posts on the Practice Hub. Set mine=True to return only posts
    written by the authenticated user, and pass tag to return only posts
    carrying that tag. Returns a list of post objects (id, title, body,
    tags, author, timestamps)."""
    raise NotImplementedError


@mcp.tool()
def get_post(post_id: int) -> dict:
    """Fetch one Practice Hub post by its integer id. Use this when you
    already know the post's id and need its full title, body, tags,
    author, and attachments."""
    raise NotImplementedError


@mcp.tool()
def create_post(title: str, body: str = "", tags: list | None = None) -> dict:
    """Create a new Practice Hub post owned by the authenticated user.
    title is required; body defaults to empty and tags to no tags.
    Returns the created post, including its new id."""
    raise NotImplementedError


@mcp.tool()
def update_post(post_id: int, title: str | None = None, body: str | None = None,
                tags: list | None = None) -> dict:
    """Change an existing post the authenticated user owns. Only the
    fields you pass (title, body, tags) are changed; omitted or null
    fields are left as they are. Returns the updated post."""
    raise NotImplementedError


@mcp.tool()
def delete_post(post_id: int) -> str:
    """Permanently delete a post the authenticated user owns, by its
    integer id. This cannot be undone."""
    raise NotImplementedError
