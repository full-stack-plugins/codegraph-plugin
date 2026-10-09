# codegraph-plugin 维护约束

- 任何代码改动走 `node scripts/bump-plugin.mjs codegraph patch|minor|major` 同步 4 个 manifest + catalog.json + 三平台 marketplace。
- 提示词文本必须 verbatim 同步自 `codegraph/src/installer/instructions-template.ts` 的 `CODEGRAPH_INSTRUCTIONS_BLOCK`（`scripts/codegraph_lib/prompt.py`）。每次 codegraph 升级（CHANGELOG 涉及 `instructions-template.ts`）需要手动重新同步，并在 `references/instructions-block.md` 中核对。
- SessionStart 钩子必须 fail-open，任何异常不阻断宿主启动。
- Hook 输出 `additionalContext` 内容来自 `prompt.CODEGRAPH_INSTRUCTIONS_BLOCK`，不擅自裁剪或附加额外段落。
- 写宿主 instructions 文件时——`<cwd>/.claude/CLAUDE.md` 存在则用它，否则用 `<cwd>/AGENTS.md`——使用标记区间替换，原子写、幂等。
- 不自动创建 `<cwd>/.claude/` 目录——避免插件越权定义用户的 `.claude/` 布局。
- 不修改 `codegraph` CLI 自身；本插件只调度 `codegraph` 现有命令。
- **不得把上游默认不对 agent 列出的 MCP 工具写成可用的「替代工具」**。上游 `DEFAULT_MCP_TOOLS = ['explore']`，其余 7 个（callers/callees/impact/node/search/files/status）调用会返回 `Tool ... is disabled via CODEGRAPH_MCP_TOOLS` 的 isError；上游 `server-instructions.ts` 亦明文要求「don't name them」。命令与技能文案一律引导走同名 CLI 子命令。由 `tests/test_commands.py::TestMcpToolClaimsMatchUpstream` 守卫。
- Marketplace `description` 在 `catalog.json` 与 `marketplace.json` 两文件保持一致；`shortDescription` 仅 `catalog.json` 有，`kimi-marketplace.json` 的 schema 只有 `id`/`displayName`/`icon`/`source`，不含描述字段。`bump-plugin.mjs --write` 后必须人工复查。

## 版本

- 当前: v0.2.0
- 同步自 codegraph v1.6.0 的 `instructions-template.ts`（0.1.7 重新核对：与上游逐字节一致，805 bytes，无文本漂移）
- Codex 后缀: `<version>+codex.YYYYMMDD`

## 同步自上游

- 升级 codegraph 后：
  1. `diff` 比对 `codegraph/src/installer/instructions-template.ts` 与 `scripts/codegraph_lib/prompt.py`
  2. 若文本漂移，更新 `prompt.py` 并 bump patch 版本
  3. 在 `RELEASE-NOTES.md` 与 `RELEASE-NOTES.zh-CN.md` 的 Release history 表记录「prompt 文本与 codegraph vX.Y.Z 同步」——本仓无 `CHANGELOG.md`，发布说明即变更记录
- 不要把上游 `codegraph` 代码 vendor 进本插件；本插件只调度其 CLI。

## 命令目录归属（2026-09-23 生态对照结论）

- `commands/*.json`：JSON 格式命令，由 `kimi.plugin.json` 的 `commands` 字段声明。
- `kimi-commands/*.md`：Markdown 格式命令。**目录名不改**——`kimi-commands/` 是生态约定名（flowguard-plugin 的 `kimi.plugin.json` 即指向 `./kimi-commands/`）。
- **不要**在文档中断言「`.json` 归 Kimi、`.md` 归 Codex」——实测生态内 .md 归属自相矛盾（flowguard 的 .md 用 `KIMI_PLUGIN_ROOT` 归 Kimi；bt/processon 的 `commands/*.md` 带 `argument-hint`/`skills:` frontmatter）。归属待实机验证，文档一律用中性表述「JSON 格式 / Markdown 格式」。

## 命令覆盖（2026-10-09 复核）

codegraph v1.6.0 共 23 个子命令，本插件以 21 个 slash 命令覆盖，除以下 4 个外全覆盖：

| 不暴露 | 原因 |
|---|---|
| `prompt-hook` / `serve --mcp` | codegraph 自家隐藏内部命令 |
| `help` | 宿主自带帮助 |
| `ui` / `web` | 打开浏览器图谱查看器，面向人而非 agent |

`codegraph context`（v1.6.0 新增）在 0.1.7 补齐——v0.1.0 时期的「覆盖全部可见命令」表述在 v1.5.0 时成立，v1.6.0 加入 `context` 后即失效。

## 发现性是本插件的目的（0.2.0 起）

本插件存在的意义是**让智能体自己发现 CodeGraph 并主动引导用户建立索引**，不是只在已索引仓库里被动待命。因此：

- `codegraph-helper` 的 frontmatter `description` **不得**以「仓库根有 `.codegraph/` 目录时使用」作为激活门槛。若这样写，未索引仓库里技能根本不触发，其「未索引则提示用户」分支永远执行不到——这是 v0.1.x 的一个真实缺陷，0.2.0 已解除。
- 技能的行为契约：**先检查 → 已索引就用 CodeGraph 回答 / 未索引就主动提示并征得同意 → 同意后跑 `codegraph init`**。不得因为「索引是用户决策」就当没看见。
- **SessionStart 钩子保持静默**：上游注入块原文写着 "If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision."（见 `prompt.CODEGRAPH_INSTRUCTIONS_BLOCK`）。钩子若在未索引时发「你该去索引」的提示，等于自我否定刚 verbatim 注入的块，违反上方 L6。未索引场景由技能的「检查 + 提示」通路兜底。

## `init` 与 `install` 的边界

两者都是用户的决策，但性质不同，不可混为一谈：

| 命令 | 副作用 | 插件立场 |
|---|---|---|
| `codegraph init` | 在仓库根写 `.codegraph/`，项目内、可重建 | **主动检查 + 主动提示**；征得同意后可代跑 |
| `codegraph install` | 改用户全局 MCP 配置，跨项目、影响宿主 | **不代劳**，仅通过 `/codegraph-install` 引导 |

判断标准是副作用的作用域与可逆性，不是「谁做决定」。

## 不做的事

- 不暴露 `codegraph prompt-hook` / `codegraph serve --mcp`（codegraph 自家隐藏命令），也不暴露 `help` / `ui` / `web`
- 不挂 PreToolUse/PostToolUse/UserPromptSubmit/Stop 钩子（避免与 codeguard-plugin 抢触发器）
- 不自动跑 `codegraph install`（MCP wiring 改的是用户全局配置，作用域跨项目，插件不能越权——与 `init` 的处理见上节）
- 不读取或上传任何源代码到外部

<!-- partme-agent-plugin-policy:v1 -->
## Partme Agent Plugin Architecture Rules v1

- 组织级架构规范（跨 `full-aigc-plugins` 与 `full-stack-plugins` 的唯一事实源）：[Partme Agent Plugin Architecture Rules v1](https://github.com/full-aigc-plugins/.github/blob/main/docs/standards/partme-agent-plugin-architecture-rules-v1.md)。
- **Harness 可选**：默认直接使用 Skills + CLI/MCP；只有确有必要时才使用最多一个可发现的 `skills/*-harness/SKILL.md`，其中的 `scripts/harness.py` 同样可选。
- 不重复开发宿主 Agent Runtime、原生 CLI/MCP 业务执行器、持久数据库或权威任务状态。正式功能必须具备可核验的 Agent → Skill/Command → Tool → Artifact 调用链。
- 保留本仓库现有 OpenSpec、技能来源锁、安全门禁、版本发布及 CI 要求；静态检查不能替代真实宿主验收。
- CI 复用组织级 [Partme Plugin Architecture 检查器](https://github.com/full-aigc-plugins/.github/blob/main/scripts/check_plugin_architecture.py)，不得复制独立实现。
<!-- /partme-agent-plugin-policy:v1 -->
