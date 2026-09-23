---
description: Find what a symbol calls
argument-hint: "<symbol> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Find callees of `$ARGUMENTS` (last token is the path, default `.`). Pass a symbol name; disambiguate same-named symbols with `--file <file>`. Run `codegraph callees <symbol>` and report all called functions (signature / file / line). Optional `--limit N` (default 20).

MCP alternative: `codegraph_callees(symbol, limit)`.

Boundaries: read-only.