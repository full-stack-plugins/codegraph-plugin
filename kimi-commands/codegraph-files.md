---
description: Show the indexed project file tree
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Run `codegraph files` in `$ARGUMENTS` (default `.`). Outputs the indexed file tree with language + symbol counts. Faster than Glob for project layout. Supports `--path` (prefix), `--pattern` (glob), `--format` (tree|flat|grouped, default tree), `--max-depth`.

MCP equivalent `codegraph_files` is not listed to agents by default (upstream exposes only `codegraph_explore`) — calling it returns a disabled-tool error. Use the CLI command above.

Boundaries: read-only.