---
description: Rebuild the CodeGraph index from scratch
argument-hint: "[path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Rebuild the full index in `$ARGUMENTS` (default `.`). Confirm `.codegraph/` exists first. Then run `codegraph index <path>` (same semantics as fresh init — discards `codegraph.db` + sidecars and re-indexes). Report: filesIndexed / filesSkipped / filesErrored / durationMs / nodesCreated / edgesCreated / index_state.

Boundaries:
- Slower than scoped sync — only run when watch mode is off, index_state=partial, or extraction version is stale
- Do not exfiltrate source code