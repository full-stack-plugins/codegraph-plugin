---
description: Incrementally sync the CodeGraph index
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Incrementally sync the index in `$ARGUMENTS` (default `.`). Confirm `.codegraph/` exists first. Then run `codegraph sync <path>` and report filesAdded / filesModified / filesRemoved / durationMs.

Note: the file watcher auto-syncs on every change — only needed when watcher is degraded or off.