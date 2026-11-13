#!/usr/bin/env bash
# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7
#
# mutmut's --runner for run_mutation.sh. Not called directly.
#
# Why this wrapper exists, confirmed by reading mutmut 2.4.5's own source
# (tests_pass() in mutmut/__init__.py) and verifying empirically, not
# assumed: mutmut decides killed-vs-survived with exactly one check,
# `survived = (returncode != 1)`. Any exit code other than literally 1
# -- 0, 2, 3, whatever -- is treated as "survived". pytest exits 2 on a
# collection error, not 1 (confirmed: a deliberately broken import in a
# throwaway test file exits 2). So a mutant that breaks an import --
# about as obviously "caught by the suite" as a mutant gets -- would be
# misreported as BAD_SURVIVED instead of OK_KILLED without this, adding
# pure noise to every mutation report rather than a real gap.
python -m pytest -x --assert=plain
code=$?
if [ "$code" -eq 0 ]; then
    exit 0
else
    exit 1
fi
