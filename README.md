# Practice Hub MCP Server (Mini Project 7)

An [MCP](https://modelcontextprotocol.io/) server that lets an AI assistant (such as Claude
Code) read and manage posts on the INF601 Practice Hub. It exposes five tools over stdio and
wraps the `PracticeHubClient` from Mini Project 1. It does not make its own HTTP calls.

## Tools

| Tool | What it does | Returns |
|---|---|---|
| `list_posts(mine=False, tag=None)` | Lists posts. `mine=True` limits the list to the authenticated user's posts, and `tag` filters by tag. | A list of post objects |
| `get_post(post_id)` | Fetches one post by its integer ID. | The post |
| `create_post(title, body="", tags=None)` | Creates a post owned by the authenticated user. `title` can be at most 300 characters, and `tags` at most 20 items. | The new post, including its ID |
| `update_post(post_id, title=None, body=None, tags=None)` | Changes only the fields you pass. Omitted or `null` fields are left unchanged. | The updated post |
| `delete_post(post_id)` | Permanently deletes a post you own. | `None` on success |

### Error handling

No tool ever raises. Each one catches the client's seven typed exceptions and returns
`{"error": "<message>"}`:

| Exception | HTTP status |
|---|---|
| `BadTokenError` | 401 |
| `ForbiddenError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `MalformedError` | 422 |
| `LockedError` | 423 |
| `RateLimitedError` | 429 |

`get_post`, `update_post` and `delete_post` also catch the `TypeError` the client raises for a
non-integer `post_id`. The 429 mapping came over from Mini Project 1. The API's documentation
does not list 429, so it may never actually occur.

## Design constraints

- **Configuration comes from environment variables only.** `PRACTICE_API_URL` and
  `PRACTICE_API_TOKEN` are read from `os.environ` at startup and are never hard-coded. If
  either one is missing, the server refuses to start and says which variable to set.
- **Nothing is printed to stdout.** stdio carries the MCP protocol, so one stray `print()`
  would corrupt it without any visible error. Anything that needs logging goes to stderr.
- **Optional parameters are typed as nullable** (`str | None`, `list | None`). MCP clients
  may send an explicit JSON `null` for an unset field, and a bare `str = None` produces a
  schema that rejects it.
- **Input size limits use Pydantic.** `create_post` uses `Field(max_length=...)` to cap
  `title` at 300 characters and `tags` at 20 items. A plain type hint would not reject an
  oversized value.
- **The `mcp` package is pinned below version 2** (it currently resolves to 1.30.0). This
  code uses the v1 `mcp.server.fastmcp.FastMCP` API, which v2 renamed.

## Project layout

```
server.py            MCP server: the five tools
src/client.py        PracticeHubClient (from Mini Project 1)
src/exceptions.py    The seven typed client exceptions
tests/               Unit, crosscut, protocol-layer, and live integration tests
scripts/             Mutation-testing helpers
CLAUDE.md            Rules for the AI implementation agent
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt          # runtime: mcp<2, requests
pip install -r requirements-dev.txt      # tests: pytest, pytest-mock, mutmut==2.4.5
```

Set the two environment variables. Use your own Practice Hub token, and never commit it:

```bash
export PRACTICE_API_URL="<Practice Hub base URL>"
export PRACTICE_API_TOKEN="<your token>"
```

### Registering with Claude Code

Run this from the project directory:

```bash
claude mcp add practice-hub \
  --env PRACTICE_API_URL="<Practice Hub base URL>" \
  --env PRACTICE_API_TOKEN="<your token>" \
  -- .venv/bin/python server.py
```

Claude Code saves these values, including the token, in plain text in `~/.claude.json`. Treat
that file as a secret. The command path is relative, so Claude Code must be started from the
project directory.

## Acceptance test

### 1. Check the MCP connection

From the project directory:

```bash
claude mcp list
```

You should see `practice-hub: .venv/bin/python server.py - ✔ Connected`. If it reports
**Failed to connect**, the usual cause is a missing environment variable. Run
`claude mcp get practice-hub` to see the registered command and env keys, then re-run the
`claude mcp add` command above.

Inside a Claude Code session, the `/mcp` command shows the same status and lists the five
tools.

### 2. Create a test post, then clean it up

Start `claude` in the project directory and give it these prompts in order:

1. `Create a Practice Hub post titled "MP7 acceptance test" with body "This post will be deleted" and tag "test".`
   Claude should call `create_post` and report the new post's ID.
2. `Get post <id>.` Claude should call `get_post` and show the same title, body and tag.
3. `Update post <id> so its body says "edited".` Claude should call `update_post` and show the new body.
4. `Delete post <id>.` Claude should call `delete_post`, which returns nothing on success.
5. `List my posts.` Claude should call `list_posts` with `mine=True`, and the test post
   should no longer be in the list.

If all five steps work, every tool is working against the live API. If a tool returns
`{"error": "..."}` instead, the message says what failed (for example, a bad token or a post
that doesn't exist).

### Automated equivalent

`tests/mcp_server_integration_test.py` does the same thing automatically. It calls the
server's tools against the live API to run a create → get → update → delete cycle, checks
that a deleted post comes back as not found, and checks the error paths. A real token must
be exported, or the tests are skipped:

```bash
export PRACTICE_API_URL="<Practice Hub base URL>"
export PRACTICE_API_TOKEN="<your token>"
pytest tests/mcp_server_integration_test.py -v
```

These tests create and delete real posts. Most of them clean up even if they fail, but
`test_create_post` and `test_full_crud_cycle` delete their post only when their assertions
pass. If one of those fails, check the feed for a leftover "Create Test" or "Full Cycle Test"
post and delete it.

## Testing

```bash
pytest
```

As of 2026-11-13, the suite reports **189 passed, 18 skipped**. It has these layers:

- **Tool unit tests** (`tests/test_<tool>.py`) call each tool function directly and replace
  the client with a mock. No network calls are made.
- **Client unit tests** (`tests/practicehub_client_unit_test.py`) map each HTTP status to
  its typed exception.
- **Crosscut tests** (`tests/test_crosscut_*.py`) check rules that span all five tools:
  - server configuration
  - real MCP registration through an in-memory client session, including nullable optional
    parameters
  - security: no URL- or credential-shaped arguments, no stdout output, no token leaks,
    exactly one client call per tool call, and API content can't register new tools
- **Live integration tests** (`tests/integration_test.py`, `tests/mcp_server_integration_test.py`)
  call the real Practice Hub API. `conftest.py` skips them unless a real
  `PRACTICE_API_TOKEN` was exported before pytest started. These are meant to be run by
  hand, not in CI.

### Mutation testing

```bash
scripts/run_mutation.sh server.py
```

This script runs mutmut on one file at a time. Every surviving mutant gets classified in one
of four ways: a real gap, out of scope for this test layer, unreachable, or equivalent.
`scripts/run_mutation.sh` explains why mutmut is pinned to 2.4.5: mutmut 3.x crashes on this
project's `src.` import layout.

## Live check against the real API

On 2026-11-13, Claude Code used this server, through its registered MCP connection, to call
all five tools against the live Practice Hub:
- It listed the feed and my own posts.
- It cleaned up test posts left over from earlier runs, deleting only posts I owned and only
  after I confirmed.
- It created, updated, fetched and deleted posts. A throwaway post announced its own
  deletion, and post #58, "Hello from Claude (now with CRUD)", is still up.

Every call succeeded, and each change was confirmed by reading the data back. The session
also found these behaviors:

- **Deleted post IDs get reused.** After posts #58 and #59 were deleted, the next two new
  posts were given those same IDs. Code or tests must not assume a deleted ID will return
  404 forever.
- **Earlier test runs left posts behind.** Seven identical "Create Test" posts matched what
  `test_create_post` creates in both `tests/integration_test.py` and
  `tests/mcp_server_integration_test.py`. Both versions delete their post only after their
  assertions pass, so a failed run leaves the post on the server. The other tests use a
  `temp_post` fixture that cleans up even when a test fails.
- **The full feed came back as exactly 50 posts.** That might be a page-size limit. The
  oldest post was included, so the list looked complete, but whether the API pages its
  results hasn't been confirmed.

## AI Usage

This project was built with AI assistance under rules I wrote and enforce. **I write the
tests. Claude Code writes the implementation.**

- **Tests (me):** I write every test, and each one is in place and failing before any
  implementation exists. The tests are the specification.
- **Test coverage review (a separate AI):** a separate AI, independent of the implementation
  agent, reviews my tests for coverage gaps. That way, the agent writing the code never decides
  whether the tests are thorough enough.
- **Implementation (Claude Code):** Claude Code writes the code to make my failing tests
  pass, and nothing more. It wrote `server.py` for this project. Claude also wrote
  `PracticeHubClient` (`src/`) for Mini Project 1, and Claude Code extended it here with the
  409 and 423 exceptions.
- `CLAUDE.md` is my contract for Claude Code. It may not edit tests or commit changes, may
  implement only what a failing test requires, and must report every assumption it makes.
- I enforce that discipline with a custom Claude Code skill I wrote, `tdd-development`
  (strict TDD agent pairing). It keeps test writing and implementation separate, so the
  agent can't grade its own work. I keep revising the skill as each project shows me where
  the agent's TDD discipline slips.
- Every AI-produced change was reviewed before I accepted it, and I authored every commit.
- During the live check described above, Claude Code worked only at my direction. It deleted
  only posts I explicitly told it to delete.

## Author

Chase Coble, FHSU INF601 (Advanced Programming in Python), Mini Project 7.
