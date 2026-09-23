# CodeGraph Plugin — Architecture

## Layered design

```
┌──────────────────────────────────────────────────────────┐
│ Host agent (Claude Code / Codex / ZCode / Kimi)           │
│  SessionStart ──┐                                       │
│  Slash cmds ────┼───────────────────────────────┐         │
└─────────────────┼───────────────────────────────┼─────────┘
                  │                               │
                  ▼                               ▼
   ┌──────────────────────────┐    ┌──────────────────────────┐
   │ hooks/inject_codegraph_   │    │ commands/codegraph-*.   │
   │ prompt.py                │    │ json (JSON fmt)             │
   │ (SessionStart hook)      │    │ kimi-commands/codegraph │
   │                          │    │ -*.md (MD fmt)           │
   └─────────┬────────────────┘    └────────────┬─────────────┘
             │                                │
             ▼                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │ scripts/codegraph_lib/                                    │
   │  • prompt.py         — verbatim prompt block              │
   │  • instructions_writer.py — atomic marker-fenced I/O      │
   │  • host_targets.py   — resolve CLAUDE.md vs AGENTS.md     │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────┐
   │ Filesystem (read/write)                                   │
   │  <cwd>/.codegraph/  ← detected (read-only)               │
   │  <cwd>/.claude/CLAUDE.md  ← written (if exists)          │
   │  <cwd>/AGENTS.md          ← written (fallback)            │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────┐
   │ codegraph CLI (upstream, MIT)                             │
   │  • codegraph init / sync / index / status / explore /    │
   │    callers / callees / impact / affected / etc.           │
   └──────────────────────────────────────────────────────────┘
```

## Failure semantics

| Failure | Behavior |
|---|---|
| `cwd` lacks `.codegraph/` | Hook exits 0 silently. Plugin does nothing. |
| `cwd` lacks both `.claude/CLAUDE.md` and `AGENTS.md` | Hook writes to `AGENTS.md` (creates if absent). Never auto-creates `.claude/`. |
| Marked section already byte-equal | `replace_or_append_marked_section` returns `unchanged`, no write. |
| File I/O error during write | Caught, logged to stderr, but `additionalContext` still emitted. |
| `codegraph` CLI not in PATH | Slash commands fail with a clear error; SessionStart hook unaffected. |
| Any other exception | Fail-open: exit 0, log to stderr. Host never sees the error. |

## Why SessionStart additionalContext + CLAUDE.md write

Codegraph's own `codegraph install` writes only to `<cwd>/.claude/CLAUDE.md`. That reaches **Task-tool subagents** (which read the project instructions file) but **not** the main agent's runtime context (which the MCP `initialize` response covers, not the file).

This plugin's two-pronged approach covers both audiences:

| Audience | Reached by |
|---|---|
| Main agent (MCP-aware) | `SessionStart.additionalContext` |
| Main agent (no MCP / non-MCP harness) | `codegraph explore "<query>"` shell fallback, triggered by the **file write** |
| Task-tool subagents | The CLAUDE.md / AGENTS.md file |
| Sub-subagents (rare) | File (inherited via project instructions) |

## Why only SessionStart

- `PreToolUse` / `PostToolUse` would compete with codeguard-plugin's hard gate.
- `UserPromptSubmit` with high-frequency matchers (commit/push) adds latency; we have nothing time-sensitive to do.
- `Stop` summaries are codeguard's domain.

## Plugin-local vs vendored skills

- **Zero vendored skills.** `skills.lock.json` is empty.
- **One plugin-local skill** (`codegraph-helper`), registered in `plugin-local-skills.json`.

This keeps the plugin's blast radius small: no third-party maintenance burden.

## Versioning discipline

- Every code change bumps version + syncs all four manifests (`catalog.json` + three plugin manifests) via `node scripts/bump-plugin.mjs codegraph patch|minor|major`.
- Patch bumps are reserved for upstream text sync + bug fixes.
- Minor bumps add new slash commands or hooks.
- Major bumps change the marker format or rewrite the hook behavior.

## Why pure Python stdlib

- Zero runtime dependencies → no `pip install`, no supply-chain risk.
- The plugin's entire hot path is `Path` operations + JSON read/write — no need for `requests`, `httpx`, or any networking library.
- The plugin has no third-party security boundary because it has no third-party code.