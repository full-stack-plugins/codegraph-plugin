---
description: Explore multi-symbol source and call paths in one call
argument-hint: "<query> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Explore symbols in `$ARGUMENTS` (last token is the path, default `.`). Run `codegraph explore <query>` — equivalent to the `codegraph_explore` MCP tool. Returns verbatim source plus call paths grouped by file.

MCP alternative: `codegraph_explore(query, maxFiles)`.

Boundaries: read-only. This is the primary entry point — prefer it over `callers`/`callees`/`impact` when unsure.