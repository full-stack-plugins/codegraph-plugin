---
description: Aggregate symbols, relationships and code blocks for a task
argument-hint: "<task> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Build task context for `$ARGUMENTS` (last token is the path, default `.`). Run `codegraph context <task>` to aggregate relevant symbols, relationships and code blocks. Optional `--format json` for machine-readable output, `--max-nodes N` to cap symbols, `--no-code` for structure only.

Division of labour with `explore`: `context` is task-oriented aggregation; `explore` is symbol/file/question-oriented source plus call paths. When unsure, start with `explore`.

MCP alternative: none — `context` is CLI-only, upstream defines no matching MCP tool.

Boundaries: read-only. Reads only the local `.codegraph/` index, never uploads source.
