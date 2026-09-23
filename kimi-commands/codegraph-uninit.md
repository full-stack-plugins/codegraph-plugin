---
description: Remove CodeGraph index from the current project
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Remove CodeGraph from `$ARGUMENTS` (default `.`). Confirm `<path>/.codegraph/` exists first. Then run `codegraph uninit <path>` (deletes the entire `.codegraph/` directory) and report counts of files/dirs removed.

Boundaries:
- This is destructive and irreversible — require explicit second confirmation
- Does not touch MCP wiring (that's `/codegraph-uninstall`)
- Do not read project source code