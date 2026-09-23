---
description: Remove codegraph MCP wiring from host agents
argument-hint: ""
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Verify `codegraph` is on PATH. Then run `codegraph uninstall` to remove MCP wiring from host agents (Claude Code, Cursor, Codex CLI, opencode, Hermes Agent, Gemini, Antigravity, Kiro). Report per-agent removal results. Pass `--keep-cli` if the user wants to keep the CLI installed.

Boundaries:
- Only removes MCP wiring, NOT the `.codegraph/` project index (that's `/codegraph-uninit`)
- Do not read project source code