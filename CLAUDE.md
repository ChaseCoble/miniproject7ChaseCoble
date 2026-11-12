# CLAUDE.md — Implementer Contract (Mini Project 7: Practice Hub MCP Server)

You are the implementation agent for this project. Claude (the assistant) writes
failing tests first; your job is to make them pass with the minimum code required,
following every rule below exactly. Deviating from any rule here, even to
"improve" something, requires stopping and reporting it before you proceed.

## Hard rules

1. **Never edit anything under `tests/`.** Not to fix a failing test, not to add a
   helper, not for any reason. If a test seems wrong, stop and report it.
2. **Never run `git commit`.** Stage changes if asked; committing is Chase's call.
3. **Implement only what the current failing test requires.** No speculative
   tools, parameters, or error handling that isn't driven by a test.
4. **Report every guess.** If a test or this contract is ambiguous (a return
   shape, an error-message wording, a default value), state the assumption
   you're making and why — don't resolve it silently.
5. **Three-line header on every `.py` file you create or edit:**
   ```python
   # INF601 - Advanced Programming in Python
   # Chase Coble
   # Mini Project 7
   ```

## Project-specific rules

6. **Never hard-code `PRACTICE_API_URL` or `PRACTICE_API_TOKEN`.** Both come from
   `os.environ` only — not a literal value anywhere, including in a test fixture
   or a comment. Tests use an obviously-fake token string and mock every network
   call. They never touch the real Practice Hub API.
7. **`server.py` must never `print()` to stdout.** stdio is the MCP protocol
   channel; any stray `print()` corrupts it and breaks the server in a way that
   looks like nothing happened from the caller's side. Log to `stderr` if you need
   to log anything.
8. **Reuse `PracticeHubClient` from Mini Project 1 — do not re-implement HTTP
   calls inline in `server.py`.** Each `@mcp.tool()` function calls the client;
   its typed exceptions (`BadTokenError`, `ForbiddenError`, `NotFoundError`,
   `MalformedError`, and `RateLimitedError` for a 429) are exactly what the
   rubric's "sensible error handling" item wants. Catch all five in each tool and
   return a clear, actionable message. None of them should ever propagate out of
   a tool function.
9. **Every tool needs a real, specific docstring** — the model reads it to decide
   when to call the tool. A placeholder ("Does the thing.") does not satisfy this
   even if a test only checks for non-empty.
10. **Confirmed (mcp 1.30.0 / FastMCP v1): `@mcp.tool()` is non-mutating.**
    `type(decorated_fn) is function` — the decorator registers the function
    with the server as a side effect and returns the exact same function
    object. A direct call (`list_posts(2, 3)`) runs with zero MCP-layer
    involvement: no Pydantic validation, no type coercion (`add("2", "3")`
    returns `"23"`, not `5`). That validation only happens on calls routed
    through the actual MCP protocol/client. Consequence: unit tests call
    tool functions directly and mock the client — correct and sufficient
    for tool *logic*. It cannot exercise tool *registration* (whether a
    function actually reached the server's tool table); that needs an
    in-memory client/session test, which is a different, not-yet-written
    layer, not a gap in the direct-call tests.

## Pinned dependency — confirmed with the professor

`mcp` is pinned to `<2` (resolves to 1.30.0) in `requirements.txt`. The professor
confirmed the class is written against `FastMCP`/`mcp.server.fastmcp`, not the
v2 `MCPServer`/`mcp.server.mcpserver` rename. Do not "helpfully" port anything to
v2 syntax — that import path does not exist in the pinned version and any code
written against it will fail with `ModuleNotFoundError`.

## Workflow

Per tool (`list_posts`, `get_post`, `create_post`, `update_post`, `delete_post`):
failing test exists → you implement → test passes → report back. Never implement
a tool ahead of its test.

After each unit passes, run `scripts/run_mutation.sh <the file you touched>` and
report the kill rate and any surviving mutant that looks like a real gap, not
just a `==`/`!=` type of mutation with no behavioral consequence.
