---
description: Show CodeGraph index status and statistics
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Run `codegraph status <path>` (default `.`) and report: index_state, indexed_with_version / indexed_with_extraction_version, files / nodes / edges, db size / WAL size, backend / journal mode, detected frameworks, pending reference count.

If index_state is not `complete`, advise whether the user should re-index.

Boundaries: read-only.