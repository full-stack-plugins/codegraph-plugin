---
description: Show the indexed project file tree
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Run `codegraph files` in `$ARGUMENTS` (default `.`). Outputs the indexed file tree with language + symbol counts. Faster than Glob for project layout. Supports `--path` (prefix), `--pattern` (glob), `--format` (tree|flat|grouped, default tree), `--max-depth`.

MCP alternative: `codegraph_files(format)`.

Boundaries: read-only.