---
description: Show one symbol's source + caller/callee trail, or read one file
argument-hint: "<name> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Inspect `$ARGUMENTS` (last token is the path, default `.`). Run `codegraph node <name>`. Two modes: pass a symbol name → location, signature, source (with line numbers), caller/callee trail. Pass a file path → full source with line numbers + dependent files.

MCP equivalent `codegraph_node` is not listed to agents by default (upstream exposes only `codegraph_explore`) — calling it returns a disabled-tool error. Use the CLI command above.

Boundaries: read-only. Prefer symbol names over file paths unless the user explicitly asks to read a whole file.