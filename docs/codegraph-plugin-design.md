# CodeGraph Plugin — Design Decisions

This document captures the non-obvious design choices and why alternatives were rejected.

## 1. Why a plugin, not just docs?

**Question.** Why not just tell users to add the official prompt to their `CLAUDE.md` themselves?

**Answer.** Three audiences exist:
- **Main agent** with MCP — already gets the long-form server instructions via MCP `initialize`. The short block in `instructions-template.ts` is a no-op for them.
- **Main agent** without MCP — needs the prompt as plain text so the shell fallback (`codegraph explore`) is remembered.
- **Task-tool subagents** — read project instructions files but not MCP initialize. They were the **measured 1-of-9 failure case** that drove the upstream to write the file in the first place (see `instructions-template.ts:9-25`).

A plugin that activates on SessionStart ensures **all three** audiences get the block:
- File write reaches subagents (Task-tool + sub-sub-agents via inheritance).
- `additionalContext` injection reaches the main agent's runtime context.
- Both audiences get the same byte-equal text.

## 2. Why inject at SessionStart, not on every prompt?

**Question.** UserPromptSubmit fires every turn — wouldn't that be more reliable?

**Answer.** No. The prompt text is **stable** — it doesn't change between turns. Re-injecting wastes tokens (the block is ~600 chars). It also conflicts with codeguard-plugin's high-frequency matcher on `提交|commit|push`.

SessionStart fires once per session (and on `resume`/`startup`). That matches the prompt's stable lifetime.

## 3. Why CLAUDE.md AND AGENTS.md?

**Question.** Why not just one file?

**Answer.** Different ecosystems use different conventions:
- `.claude/CLAUDE.md` — Claude Code's convention; what codegraph's installer uses.
- `AGENTS.md` — OpenSpec / multi-agent convention; what tooling-aware users often already have.

The plugin tries `.claude/CLAUDE.md` first (matching codegraph's behavior); falls back to `AGENTS.md` if absent. Never auto-creates `.claude/` (avoids forcing a host directory structure).

## 4. Why 20 commands, not just the 5 most-used?

**Question.** Why expose all 20 instead of just `init`/`sync`/`status`/`callers`/`impact`?

**Answer.** 
- The plugin's purpose is **discoverability** — every command is one slash command away from the user.
- `codegraph install` / `codegraph upgrade` / `codegraph daemon` are operational tasks that benefit from slash-command form (the user doesn't need to remember CLI syntax).
- The 4 maintenance commands (`daemon`/`unlock`/`version`/`telemetry`) cost ~40 lines of JSON to ship; skipping them costs the user mental overhead later.

Trade-off: 40 command files instead of 10. We accept the file count for the discoverability win.

## 5. Why a `.md` mirror of every `.json`?

**Question.** Why two file formats?

**Answer.** User explicitly chose both formats (matching `flowguard-plugin`'s pattern). Different hosts split by-format:
- Kimi / ZCode read `commands/*.json`
- Codex reads `commands/*.md` (with YAML frontmatter and `$ARGUMENTS`)

Single-format for both is impossible without losing one host.

## 6. Why no PreToolUse / PostToolUse / UserPromptSubmit / Stop hooks?

**Question.** Why not hook `git commit` to auto-sync?

**Answer.** 
- **Conflict with codeguard-plugin**: codeguard owns PreToolUse Bash for git operations. Two plugins on the same hook race for timeout budget and confuse the host about which output to honor.
- **Redundant**: codegraph's `codegraph watch` already auto-syncs on file change (debounced, ~2s). A commit-time sync adds nothing the watcher hasn't done.
- **Stops and StopSummary**: they duplicate codeguard's domain (it owns stop summaries for governance hooks).
- **UserPromptSubmit with commit/push matcher**: would fire on every commit-related prompt, wasting 120s timeout budget.

The plugin stays out of these hooks by design.

## 7. Why fail-open on the hook?

**Question.** Shouldn't the hook return an error if the write fails?

**Answer.** No. SessionStart is host-blocking; if the hook returns an error, the host agent doesn't start. The plugin's job is to inject a **helpful hint**, not to gate the session. Failing the session to deliver a 600-char text block is a bad trade.

Same principle as `codegraph`'s own `instructions-template.ts` (which says the block exists specifically because failures are expensive):

> "the noise the unindexed-session policy exists to prevent"

This plugin inverts the noise-vs-silence trade: when `.codegraph/` exists, the prompt is silent and helpful; when it doesn't, the plugin is silent and out of the way.

## 8. Why pure Python stdlib?

**Question.** Why no `requests` / `httpx` / `rich`?

**Answer.** 
- The plugin makes zero network calls. There's nothing to do with `requests`.
- The plugin's hot path is two `Path.read_text` calls + one `atomic_write_file_sync` + one `print(json.dumps(...))`. No need for `rich`.
- Zero deps = zero supply-chain surface = zero `pip install` step in `codegraph install`.

The user's machine already runs codegraph's CLI. Adding a Python `requirements.txt` would be the first thing to break.

## 9. Why no auto-upgrade of the upstream prompt text?

**Question.** Why not subscribe to upstream releases and auto-sync?

**Answer.** The prompt text is a **policy decision** about how to talk to the agent. Changing it without the plugin author's review risks subtle regressions. The plugin explicitly says: "re-sync when the upstream CHANGELOG mentions `instructions-template.ts`" — manual, reviewed, version-bumped.

Auto-sync on each `codegraph upgrade` would hide drift and break the audit trail.

## 10. Why no per-host diffing?

**Question.** Why not specialize the prompt per host (Codex vs Claude Code vs Kimi)?

**Answer.** 
- The official prompt block is **deliberately CONDITIONAL** (see `instructions-template.ts:32-41`): it says "if `.codegraph/` exists..." — that language works across hosts.
- Per-host prompts diverge; the upstream text is the single source of truth.
- Hosts differ in features, not in the need to know "this repo is indexed".

## Summary

The plugin's design optimizes for:
1. **Discoverability** (commands + skill description).
2. **Verbatim upstream sync** (single source of truth in `prompt.py`).
3. **Fail-open everywhere** (host never blocked).
4. **No collisions** (SessionStart only; no vendor skills; no third-party deps).