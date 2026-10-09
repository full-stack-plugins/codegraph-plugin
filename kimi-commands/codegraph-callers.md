---
description: Find what calls a symbol
argument-hint: "<symbol> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Find callers of `$ARGUMENTS` (last token is the path, default `.`). Pass a symbol name; disambiguate same-named symbols with `--file <file>`. Run `codegraph callers <symbol>` and report all call sites (signature / file / line). Optional `--limit N` (default 20).

MCP equivalent `codegraph_callers` is not listed to agents by default (upstream exposes only `codegraph_explore`) — calling it returns a disabled-tool error. Use the CLI command above.

Boundaries: read-only. Includes class instantiation sites and dynamic-dispatch hops.