# ADDED Requirements

## Slash Command Coverage

### Scenario: 全部 codegraph CLI 命令暴露

The plugin SHALL expose **20 slash commands** covering all 20 visible codegraph CLI subcommands, in two formats each:

- Kimi / ZCode host reads `commands/codegraph-<verb>.json`
- Codex host reads `kimi-commands/codegraph-<verb>.md`

### Hidden Commands Excluded

The plugin SHALL NOT expose:

- `codegraph prompt-hook` (codegraph internal UserPromptSubmit hook endpoint)
- `codegraph serve --mcp` (codegraph internal MCP stdio entry)

### Command Verb List (20)

The 20 covered commands, in `commands/` and `kimi-commands/`:

| Slash | Equivalent CLI | Purpose |
|---|---|---|
| `codegraph-init` | `codegraph init [path]` | Initialize CodeGraph |
| `codegraph-uninit` | `codegraph uninit [path]` | Remove .codegraph/ |
| `codegraph-install` | `codegraph install` | Wire MCP into host agents |
| `codegraph-uninstall` | `codegraph uninstall` | Remove MCP wiring |
| `codegraph-index` | `codegraph index [path]` | Rebuild full index |
| `codegraph-sync` | `codegraph sync [path]` | Incremental sync |
| `codegraph-status` | `codegraph status [path]` | Index stats |
| `codegraph-query` | `codegraph query <search>` | Keyword symbol search |
| `codegraph-explore` | `codegraph explore <query>` | Multi-symbol source + paths |
| `codegraph-node` | `codegraph node <name>` | One symbol or one file |
| `codegraph-files` | `codegraph files` | Project file tree |
| `codegraph-callers` | `codegraph callers <symbol>` | Who calls X |
| `codegraph-callees` | `codegraph callees <symbol>` | What X calls |
| `codegraph-impact` | `codegraph impact <symbol>` | X's blast radius |
| `codegraph-affected` | `codegraph affected [files]` | Affected tests |
| `codegraph-daemon` | `codegraph daemon` | Manage daemons |
| `codegraph-unlock` | `codegraph unlock [path]` | Remove stale lock |
| `codegraph-version` | `codegraph version` | Print version |
| `codegraph-telemetry` | `codegraph telemetry [status\|on\|off]` | Telemetry |
| `codegraph-upgrade` | `codegraph upgrade [version]` | Upgrade CLI |

### Format Consistency

For each slash command:

- The `.json` and `.md` files SHALL have the same `name` (matches filename stem).
- The `.md` file SHALL have YAML frontmatter with `description` and optional `argument-hint`.
- The `.json` file SHALL have `name`, `description`, `prompt` keys.
- Both files SHALL describe the same intent (Chinese vs English localization is allowed).