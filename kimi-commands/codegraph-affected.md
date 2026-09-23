---
description: Find test files affected by changed source files
argument-hint: "[files...]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Find affected tests for the changed files in `$ARGUMENTS` (default to `git diff` of unstaged/staged changes). Run `codegraph affected [files...]` — BFS through dependents filtered to test file patterns.

Boundaries: read-only. Common workflow: after editing X, narrow down which tests to run.