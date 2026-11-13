#!/usr/bin/env bash
# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7
#
# Run mutation testing against one source file at a time, matching the
# "one unit at a time" build cycle: write the failing test, implement it,
# then run this against just that file before moving to the next tool.
#
# Usage:
#   scripts/run_mutation.sh src/practice_hub_client.py
#
# Why mutmut is pinned to 2.4.5 (see requirements-dev.txt):
# mutmut 3.x instruments the code it mutates through a "trampoline" layer
# that records qualified names for its stats, and that layer asserts the
# qualified name never starts with the literal string "src." -- an
# undocumented restriction, not something in mutmut's own docs. Since this
# project's existing import convention (carried over from Mini Project 1,
# e.g. "from src.exceptions import BadTokenError") makes every module's
# qualified name start with exactly that prefix, mutmut 3.8.1 crashes with
# "AssertionError: Failed trampoline hit. Module name starts with `src.`,
# which is invalid" before it can run a single mutant. mutmut 2.4.5 predates
# that instrumentation layer entirely and ran cleanly against this layout.
# If a future mutmut 3.x release documents a fix or an opt-out, re-evaluate
# the pin rather than assuming 2.4.5 forever.
#
# --runner mutation_runner.sh: mutmut 2.4.5's own killed/survived check
# (tests_pass() in mutmut/__init__.py) is `returncode != 1` -- only exit
# code 1 counts as "killed". Confirmed empirically: pytest exits 2 on a
# collection error, not 1, so an import-breaking mutant would otherwise
# be misreported as BAD_SURVIVED (added to the gaps you have to triage)
# even though the suite obviously caught it. The wrapper just normalizes
# any nonzero pytest exit code to 1 before mutmut sees it.
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path-to-source-file>" >&2
    exit 1
fi

TARGET="$1"

if [[ ! -f "$TARGET" ]]; then
    echo "No such file: $TARGET" >&2
    exit 1
fi

rm -rf .mutmut-cache

mutmut run --paths-to-mutate "$TARGET" --runner "bash scripts/mutation_runner.sh"
echo
echo "--- survived mutants (these are the gaps your tests don't catch yet) ---"
mutmut results
