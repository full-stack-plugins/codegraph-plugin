---
description: Search symbols by keyword
argument-hint: "<search> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Search symbols in `$ARGUMENTS` (last token is the path, default `.`). Run `codegraph query <query>` and report matched symbol locations (kind / file / line / signature).

MCP alternative: `codegraph_search(query, kind?, limit?)`.

Boundaries: read-only.