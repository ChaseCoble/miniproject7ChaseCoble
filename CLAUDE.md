# CLAUDE.md — Implementer Contract (Mini Project 7: Practice Hub MCP Server)

You are the implementation agent for this project. The tests already exist and
are failing; your job is to make them pass with the minimum code required,
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
   `MalformedError`, `RateLimitedError` for a 429, `ConflictError` for a 409,
   and `LockedError` for a 423) are exactly what the rubric's "sensible error
   handling" item wants. Catch all seven in each tool and return a clear,
   actionable message. None of them should ever propagate out of a tool
   function. **`get_post`, `update_post`, and `delete_post` must also
   catch `TypeError`** the same way — the client raises it for a non-int
   `post_id`, and the existing tests for all three
   (`test_..._returns_clear_message_on_invalid_post_id_type`) require it to
   come back as `{"error": str(e)}`, not propagate. `list_posts` and
   `create_post` take no `post_id`, so this doesn't apply to them.
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

## Real gap found by the protocol-layer tests (tests/test_crosscut_tool_registration.py)

Routing calls through the actual MCP protocol (not a direct Python call)
surfaced a genuine bug, confirmed empirically against the real `mcp==1.30.0`
in-memory session, not guessed: three signatures type an optional parameter
as a bare `str`/`list` with a `None` default instead of `str | None`/
`list | None`:

- `list_posts(tag: str = None)`
- `create_post(tags: list = None)`
- `update_post(title: str = None, body: str = None, tags: list = None)`

Omitting the key works fine today — FastMCP applies the Python default with
no Pydantic involved. But a client sending an explicit JSON `null` for an
unset optional field (normal, spec-legal behavior, not malformed input)
gets a Pydantic validation error back instead of the tool running, because
the generated schema for a bare `str`/`list` annotation isn't nullable.

Fix required: change those five parameters' annotations to `str | None` /
`list | None` (keep the `= None` defaults). That's the only change these
three tests need — nothing about `get_post`/`delete_post` is affected,
since `post_id: int` is required, not optional.

## Two more typed exceptions: `ConflictError` (409) and `LockedError` (423)

Spec source: https://practice.fhsucyber.com/docs-guide. The documented error
codes are 401/403/404/409/422/423, not the 401/403/404/422/429 that
`_ERRORS` currently maps. 429 isn't documented anywhere on that page —
leave it as-is for now (Chase's call whether that's real-but-undocumented or
a leftover assumption, not yours to resolve), but 409 and 423 **are**
documented and currently fall through `_handle_response` to a bare
`requests.HTTPError` via `resp.raise_for_status()` instead of a typed
exception. That's a real, currently-unhandled gap, not a guess.

Required:
- `src/exceptions.py`: add `ConflictError` and `LockedError` (same shape as
  the existing five — exact naming is Claude's proposal, not confirmed
  against any rubric wording, so flag it in your report if you'd rather
  name them something else).
- `src/client.py`'s `_ERRORS` dict: map `409 -> ConflictError` and
  `423 -> LockedError`, same pattern as the other five entries.
- `server.py`'s `CLIENT_ERRORS` tuple: add both, so all five tools catch
  all seven typed exceptions, not five (see rule 8 above).

Tests already exist and are failing for all of this:
`test_handle_response_409_raises` / `test_handle_response_423_raises` in
`practicehub_client_unit_test.py` (client layer), and
`test_<tool>_returns_clear_message_on_conflict` /
`test_<tool>_returns_clear_message_on_locked` in each of the five
`test_<tool>.py` files (tool layer).

## `delete_post`'s return value on success is `None`

Not `{"deleted": post_id}` or any other invented shape — `client.delete_post()`
itself always returns `None` on success, and
`test_delete_post_returns_none_on_success` already specifies that the tool
returns exactly that, unchanged. Return type annotation should be `None | dict`
(`None` on success, `{"error": ...}` on a caught exception), not `dict`.

## Pinned dependency

`mcp` is pinned to `<2` in `requirements.txt`, resolving to 1.30.0. This project is
written against that version's `FastMCP`/`mcp.server.fastmcp` API, not the v2
`MCPServer`/`mcp.server.mcpserver` rename. Do not "helpfully" port anything to v2
syntax — that import path does not exist in 1.30.0, and any code written against
it fails with `ModuleNotFoundError` at import time, not a deprecation warning.

## Workflow

Per tool (`list_posts`, `get_post`, `create_post`, `update_post`, `delete_post`):
failing test exists → you implement → test passes → report back. Never implement
a tool ahead of its test.

**Crosscut rule:** any test file named `test_crosscut_*` is in scope from the
same moment as the individual-function tests it spans, not after them. It
specifies a constraint that cuts across multiple tools/functions rather than
belonging to any one of them, so it never waits for the per-function suites to
finish first — you're writing each tool against both constraints at once from
the start.

Right now that's three files:

- `test_crosscut_server_config.py` — env/config handling that applies to the
  whole server, not any one tool.
- `test_crosscut_tool_registration.py` — protocol-layer constraints (actual
  MCP registration, and the `str | None`/`list | None` requirement on every
  optional parameter) that apply across all five tools.
- `test_crosscut_security.py` — threat-model-driven constraints across all
  five tools: no tool accepts a URL/host- or credential-shaped argument, no
  tool prints to stdout or leaks the real token/URL, the client is touched
  exactly once per call on every path (success and all five typed
  exceptions — this is what stops a future retry feature from flooding the
  API), content fetched from the API never registers a new tool no matter
  what it looks like, and `create_post`'s `title`/`tags` need a Pydantic
  `Field` length/count constraint (`max_length=300` on `title`,
  `max_length=20` on `tags`) — a bare type hint doesn't reject an oversized
  value, so this one specifically needs the `Field(...)` form, not just a
  type annotation change.

Concretely for the second one: write `tag`/`tags`/`title`/`body` as
`str | None`/`list | None` the first time, in the tool that introduces each
one (`list_posts` for `tag`, `create_post` for `tags`, `update_post` for all
three) — not as a retrofit after a test catches it. All three crosscut files
will fail to collect at all (`ModuleNotFoundError: No module named 'server'`)
until `server.py` exists even minimally; that's expected, not a sign anything's
wrong. If a future test file is added with `crosscut` in its name, the same
rule applies to it automatically — that's the point of naming it that way.

After each unit passes, run `scripts/run_mutation.sh <the file you touched>` and
report the kill rate and any surviving mutant that looks like a real gap, not
just a `==`/`!=` type of mutation with no behavioral consequence.

**Mutation-survivor triage, not 100% kill rate.** A surviving mutant is not
automatically a gap — some are equivalent mutants (behaviorally identical to
the original in every observable way) that no correct test can ever kill, and
some belong to a different test layer entirely (see rule 10). Classify every
survivor instead of ignoring it or chasing it to zero: real gap (write a test,
fix it) / out of scope for this layer (say so, move on) / structurally
unreachable (`if __name__ == "__main__":`, etc.) / equivalent or noise. The
bar is that every survivor gets a stated reason in your report — not that the
count hits zero.
