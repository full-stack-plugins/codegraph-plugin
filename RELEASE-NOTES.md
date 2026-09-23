# codegraph-plugin — Release Notes

**Released**: 2026-09-23
**Repository**: [full-stack-plugins/codegraph-plugin](https://github.com/full-stack-plugins/codegraph-plugin)
**License**: Apache-2.0
**Plugin ID**: `codegraph` · **Version**: 0.1.5

> **Localization**: This file is the English release notes. The Chinese version is in [RELEASE-NOTES.zh-CN.md](RELEASE-NOTES.zh-CN.md).

---

## Release history

| Version | Date | Changes |
|---|---|---|
| 0.1.5 | 2026-09-23 | Fix format-attribution claims (JSON/Markdown neutral wording, ecosystem-verified); rename `KIMI_COMMANDS` test variable; document command-directory convention in AGENTS.md |
| 0.1.4 | 2026-09-23 | Add bump-plugin CLI tests (untested-hotspot closure); description parity check for all 40 command files; README heading-structure parity test; marker-containment guard in `replace_or_append_marked_section` |
| 0.1.3 | 2026-09-23 | Fix `bump-plugin.mjs` sync failure handling (no longer aborts post-write); extend cross-link lint to cover `kimi-commands/*.md`; make `scripts/tests/` discoverable; sync version surfaces |
| 0.1.2 | 2026-09-23 | Add `defaultPromptZhCn` to ZCode manifest; fix OpenSpec delta headers |
| 0.1.1 | 2026-09-23 | First `bump-plugin.mjs` release run (4 manifests + catalog + 3 marketplaces) |
| 0.1.0 | 2026-09-23 | Initial release (below) |

---

## What's in this release

Initial release of **codegraph-plugin** — a thin orchestration layer on top of the upstream [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) (MIT) CLI.

### Highlights

- **Discoverability via prompt injection**: at session start, when a `.codegraph/` directory exists in the cwd, this plugin injects the official CodeGraph prompt block — verbatim from upstream `src/installer/instructions-template.ts` — into both:
  - the host's instruction file (`<cwd>/.claude/CLAUDE.md` if present, else `<cwd>/AGENTS.md`); and
  - the active agent session via `SessionStart.additionalContext`.

  No user action required. The plugin is silent in non-indexed projects.

- **20 slash commands**: complete coverage of all visible `codegraph` CLI subcommands — `init`, `uninit`, `install`, `uninstall`, `index`, `sync`, `status`, `query`, `explore`, `node`, `files`, `callers`, `callees`, `impact`, `affected`, `daemon`, `unlock`, `version`, `telemetry`, `upgrade` — in two formats — JSON (`commands/*.json`, declared in `kimi.plugin.json`) and Markdown (`kimi-commands/*.md`). Hidden commands (`prompt-hook`, `serve --mcp`) are intentionally not exposed.

- **One plugin-local skill** (`codegraph-helper`): conditions the agent to prefer CodeGraph's MCP tools (`codegraph_explore`, `codegraph_callers`, `codegraph_callees`, `codegraph_impact`, etc.) when answering code-structure questions in indexed repositories.

### Coexistence with `codegraph install`

CodeGraph's own `codegraph install` writes the same prompt block to `~/.claude/CLAUDE.md`. This plugin's marker-fenced writer is **byte-equal idempotent**, so:

- If the user has already run `codegraph install`, this plugin's hook is a no-op.
- If the user runs `codegraph install` *after* installing this plugin, both writers' byte-equal strategies give no churn.

What this plugin adds on top of `codegraph install` alone:

1. **Two audiences covered** — the plugin emits `additionalContext` for the main agent at runtime; the file write handles Task-tool subagents.
2. **`AGENTS.md` fallback** — projects without `.claude/CLAUDE.md` get the block written to `AGENTS.md` (the OpenSpec / multi-agent convention).
3. **Slash commands** — `codegraph install` exposes no commands; this plugin covers all 20.

---

## Install

The plugin is shipped as a single command on the host:

```bash
# Codex / ZCode / Kimi marketplace install (auto-discovers marketplace (latest)):
codex plugin add codegraph@full-stack-plugins
zcode plugin install codegraph --ref v0.1.5
```

After install, **in any indexed project** (`./codegraph/` exists), start a new session — the plugin auto-injects the official prompt.

In a non-indexed project, no action happens. To index:

```bash
/codegraph-init
```

---

## Hooks installed

| Event | Matcher | Timeout | Purpose |
|---|---|---|---|
| `SessionStart` | `startup\|resume` | 10s | Inject the official CodeGraph prompt |

No `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `Stop` hooks — this plugin deliberately stays out of those events to avoid collision with `codeguard-plugin` and other plugins that own them.

---

## Slash commands

20 commands, one per `codegraph` CLI subcommand (excluding two hidden internal commands).

### Index lifecycle

| Slash | Equivalent CLI |
|---|---|
| `/codegraph-init` | `codegraph init [path]` |
| `/codegraph-uninit` | `codegraph uninit [path]` |
| `/codegraph-install` | `codegraph install` |
| `/codegraph-uninstall` | `codegraph uninstall` |
| `/codegraph-index` | `codegraph index [path]` |
| `/codegraph-sync` | `codegraph sync [path]` |
| `/codegraph-status` | `codegraph status [path]` |

### Query / analysis (with MCP equivalents)

| Slash | Equivalent CLI | MCP tool |
|---|---|---|
| `/codegraph-query` | `codegraph query <search>` | `codegraph_search` |
| `/codegraph-explore` | `codegraph explore <query>` | `codegraph_explore` (primary entry) |
| `/codegraph-node` | `codegraph node <name>` | `codegraph_node` |
| `/codegraph-files` | `codegraph files` | `codegraph_files` |
| `/codegraph-callers` | `codegraph callers <symbol>` | `codegraph_callers` |
| `/codegraph-callees` | `codegraph callees <symbol>` | `codegraph_callees` |
| `/codegraph-impact` | `codegraph impact <symbol>` | `codegraph_impact` |
| `/codegraph-affected` | `codegraph affected [files]` | (CLI only) |

### Maintenance

| Slash | Equivalent CLI |
|---|---|
| `/codegraph-daemon` | `codegraph daemon` |
| `/codegraph-unlock` | `codegraph unlock [path]` |
| `/codegraph-version` | `codegraph version` |
| `/codegraph-telemetry` | `codegraph telemetry [status\|on\|off]` |
| `/codegraph-upgrade` | `codegraph upgrade [version]` |

---

## Compatibility

- **Plugin host**: Claude Code (any version with `SessionStart.additionalContext` support), Codex, ZCode, Kimi.
- **Upstream**: `codegraph` v1.5.0 (verified at sync). The plugin's prompt block is verbatim from `codegraph/src/installer/instructions-template.ts:42-51`. When upstream's `instructions-template.ts` changes, this plugin's `scripts/codegraph_lib/prompt.py` must be re-synced and a patch version bumped (see `AGENTS.md` discipline).
- **Runtime**: pure Python stdlib. No `pip install`, no third-party runtime dependencies.
- **Filesystem**: writes to host instruction files only. Never auto-creates `<cwd>/.claude/` directory.

---

## What this release does NOT do

- Does **not** install the `codegraph` CLI itself. Users run `npm i -g @colbymchenry/codegraph` (or `install.sh` from upstream) before this plugin is useful.
- Does **not** auto-run `codegraph init`. Indexing is the user's decision; this plugin only activates when `.codegraph/` already exists.
- Does **not** modify the upstream `codegraph` project. The official prompt block is **copied verbatim** with attribution in `NOTICE`.

---

## Maintenance (post-release)

To upgrade after the upstream codegraph release:

```bash
# 1. Verify prompt text matches upstream
diff codegraph/src/installer/instructions-template.ts scripts/codegraph_lib/prompt.py

# 2. If text drifted, update prompt.py

# 3. Bump version (syncs 4 manifests + catalog.json + 3 platform marketplaces)
CODEGUARD_SKIP_GATE=1 node scripts/bump-plugin.mjs codegraph patch

# 4. Commit both repositories and push
cd /Users/wandl/workspaces/workspace-agent-skills/full-stack-plugins && git add -A && git commit -m "release: codegraph 0.1.x" && git push
cd /Users/wandl/workspaces/workspace-agent-skills/full-stack-plugins-repositories/codegraph-plugin && git add -A && git commit -m "release: v0.1.x" && git push
```

---

## Files shipped

86 files, 42 unit tests (all passing):

- 1 skill manifest (`skills/codegraph-helper/SKILL.md` + 2 references)
- 20 JSON slash commands (`commands/codegraph-*.json`, declared in `kimi.plugin.json`)
- 20 Markdown slash commands (`kimi-commands/codegraph-*.md`)
- 4 host manifests (`kimi.plugin.json`, `.codex-plugin/plugin.json`, `.zcode-plugin/plugin.json`, `.agents/plugins/marketplace.json`)
- 3 SVG assets (logo, composer icon, banner) + 3 PNG equivalents
- 1 hook (`hooks/inject_codegraph_prompt.py`) + manifest (`hooks/hooks.json`)
- 4 Python library modules (`scripts/codegraph_lib/`)
- 5 test files (`tests/` + `scripts/tests/`)
- 3 docs (`docs/codegraph-architecture.{md,zh_CN.md}`, `docs/codegraph-plugin-design.md`)
- 1 OpenSpec change (`openspec/changes/2026-09-23-add-codegraph-plugin/`)
- Standard plugin metadata: `LICENSE`, `NOTICE`, `PRIVACY.md`, `TERMS.md`, `README.md`, `README.zh-CN.md`, `AGENTS.md`
- Release notes pair: `RELEASE-NOTES.md` (English, this file), `RELEASE-NOTES.zh-CN.md`

---

## Acknowledgements

The official CodeGraph prompt block in `scripts/codegraph_lib/prompt.py` is verbatim from the upstream [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) project (MIT, Copyright (c) 2026 Colby McHenry). See `NOTICE` for full attribution.

---

## License

Apache-2.0. See [LICENSE](LICENSE).