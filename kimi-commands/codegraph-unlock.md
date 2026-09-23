---
description: Remove a stale lock file blocking indexing
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Remove a stale lock from `$ARGUMENTS` (default `.`). Run `codegraph unlock <path>` and report the removed lock file path.

Boundaries: only invoke when CLI/MCP/watch simultaneously report "lock held by another process".