---
description: Search symbols by keyword
argument-hint: "<search> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Search symbols in `$ARGUMENTS` (last token is the path, default `.`). Run `codegraph query <query>` and report matched symbol locations (kind / file / line / signature).

MCP equivalent `codegraph_search` is not listed to agents by default (upstream exposes only `codegraph_explore`) — calling it returns a disabled-tool error. Use the CLI command above.

Boundaries: read-only.