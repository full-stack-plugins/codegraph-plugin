---
description: One-time wiring of codegraph MCP server into host agents
argument-hint: ""
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Verify `codegraph` is on PATH (else prompt user to install via `npm i -g @colbymchenry/codegraph` or the install script). Then run `codegraph install` to wire the MCP server into host agents (Claude Code, Cursor, Codex CLI, opencode, Hermes Agent, Gemini, Antigravity, Kiro). Report per-agent wiring results.

Boundaries:
- One-time setup — do not invoke per-session
- Does not write any files inside the project
- Do not read project source code