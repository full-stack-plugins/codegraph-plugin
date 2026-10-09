---
description: Find what a symbol calls
argument-hint: "<symbol> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Find callees of `$ARGUMENTS` (last token is the path, default `.`). Pass a symbol name; disambiguate same-named symbols with `--file <file>`. Run `codegraph callees <symbol>` and report all called functions (signature / file / line). Optional `--limit N` (default 20).

MCP equivalent `codegraph_callees` is not listed to agents by default (upstream exposes only `codegraph_explore`) — calling it returns a disabled-tool error. Use the CLI command above.

Boundaries: read-only.