---
description: Initialize CodeGraph in the current project
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Initialize CodeGraph in `$ARGUMENTS` (default `.`). Run `codegraph init <path>` and report the index status: files / nodes / edges / languages / backend / journal mode.

If `codegraph` is not on PATH, run `/codegraph-install` first.

Boundaries:
- Do not modify .gitignore
- Do not create or modify files under vendored skill directories
- Do not read or upload source code
- Do not block on partial failure (let the user decide next steps)