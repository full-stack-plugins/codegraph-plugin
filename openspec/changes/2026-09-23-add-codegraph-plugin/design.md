# 2026-09-23-add-codegraph-plugin — Design

## Why

CodeGraph 是 colbymchenry/codegraph 项目（MIT）提供的本地代码智能工具，通过 tree-sitter 构建代码知识图谱并以 MCP server 暴露给 AI 编码代理。当前在 `full-stack-plugins` 生态中没有任何编排，AI 代理只能：

1. 用户手动说「帮我用 codegraph」才会触发（依赖记忆与重复指令）
2. codegraph 自家 `codegraph install` 把官方提示词块写到 `~/.claude/CLAUDE.md`（**只覆盖 Task 工具子代理**，不覆盖主代理运行时上下文，也不管 AGENTS.md 兜底）
3. codegraph CLI 全量 20 个命令没有 slash command 形式暴露，用户得手动 `codegraph explore "<query>"` 等

本插件补齐以上三件事。

## What changes

- **新增** `codegraph-plugin`（Apache-2.0）仓库。
- **SessionStart 钩子**（Python stdlib，无依赖）检测 `<cwd>/.codegraph/`，存在则把官方提示词块（verbatim 同步自上游 `instructions-template.ts:42-51`）写到 `<cwd>/.claude/CLAUDE.md`（优先）或 `<cwd>/AGENTS.md`（兜底），并通过 `SessionStart.additionalContext` 注入主代理运行时上下文。
- **20 个 slash command**（`.json` Kimi 主读 + `.md` Codex 主读）一对一覆盖 codegraph CLI（除 `prompt-hook` / `serve --mcp` 两个隐藏命令外）。
- **1 个本地技能** `codegraph-helper`，description 触发智能体根据任务选择合适的 codegraph MCP 工具。
- **marketplace hub 注册**：在 `full-stack-plugins/catalog.json` 加条目，`sync-marketplaces.mjs --write` 重新生成三平台清单。

## Non-goals

- 不替代 codegraph CLI（用户已通过 `npm i -g @colbymchenry/codegraph` 安装）。本插件纯客户端，无任何 CLI 行为重写。
- 不替代 `codegraph install` 的 MCP wiring。本插件只调度 CLI 命令、不修改宿主代理的 MCP 配置。
- 不替代 `codegraph init`。索引是用户决策，本插件只在 `.codegraph/` 已存在时激活。
- 不挂 `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `Stop` 钩子——避免和 codeguard-plugin 等其他插件抢触发器。
- 不 vendor 任何第三方技能（`skills.lock.json` 故意为空）。
- 不修改上游 `codegraph` 本身的代码。

## Design decisions

| 决策 | 选择 | 备选 |
|---|---|---|
| 命令文件格式 | `.json` (Kimi) + `.md` (Codex) 双份 | 单 .json（Kimi 优先）；单 .md（Codex 优先） |
| 钩子事件 | 仅 `SessionStart` | +PreToolUse on git commit（被拒绝：和 watcher 重复；与 codeguard 抢触发器） |
| 文件写入目标 | `<cwd>/.claude/CLAUDE.md`（优先）<br> `<cwd>/AGENTS.md`（兜底）<br>**不**自动创建 `<cwd>/.claude/` | 仅 CLAUDE.md（仅 Claude Code 用户受益） |
| 标记格式 | `<!-- CODEGRAPH_START -->` / `<!-- CODEGRAPH_END -->` | 自定义 marker（被拒绝：与上游 installer 不兼容，用户切换时会有 diff） |
| 失败模式 | 全程 fail-open | 钩子错误 exit 1（被拒绝：会阻塞宿主启动） |
| 依赖 | 纯 Python stdlib | +requests / +httpx / +rich（被拒绝：增加供应链面） |
| 自动同步上游提示词 | **不**自动，每次 `codegraph upgrade` 后人工审 CHANGELOG → 同步 `prompt.py` → bump patch | Webhook 自动同步（被拒绝：会跳过审计链路） |
| Skills vendor | 0 个本地技能之外 + 1 个 `codegraph-helper` 本地技能 | 全 vendor（被拒绝：skills.lock.json 维护成本，无对应上游） |
| 提示词漂移检查 | AGENTS.md 强制纪律 + `references/instructions-block.md` verbatim | 自动对比（被拒绝：误报噪声大） |

## Scope

### In-scope

- `full-stack-plugins-repositories/codegraph-plugin/` 全部文件
- `full-stack-plugins/catalog.json` 加 `codegraph` 条目
- `full-stack-plugins/marketplace.json` + `full-stack-plugins/kimi-marketplace.json` 自动重生成

### Out-of-scope

- 修改 codegraph CLI 自身（上游）
- 修改 codeguard-plugin / flowguard-plugin / 其他 sibling 插件
- 修改 `full-stack-plugins/scripts/bump-plugin.mjs`（已经支持任意 plugin id）
- 创建 GitHub 仓库（用户后续手动）

## Risks

| 风险 | 缓解 |
|---|---|
| 上游提示词文本漂移 | AGENTS.md 强制纪律 + `references/instructions-block.md` verbatim + 单元测试比对 |
| 与 codegraph 自家 installer 重复写 | 字节级幂等（`replace_or_append_marked_section` byte-equal → noop） |
| SessionStart 钩子超时 | 10s 上限；所有 IO 用 try/except；任何异常 fail-open |
| 与 codeguard-plugin 钩子冲突 | 只挂 SessionStart，不碰 PreToolUse/PostToolUse/UserPromptSubmit/Stop |
| 命令数量多维护成本 | `.json` / `.md` 内容结构对齐；bump-plugin.mjs 集中版本同步 |

## Acceptance

- `python3 -m unittest discover -s tests -t .` 全绿（≥ 22 tests）
- 钩子在已索引 cwd 下产生 `additionalContext` JSON 输出，写入 `AGENTS.md` 或 `CLAUDE.md`
- 钩子在未索引 cwd 下静默 exit 0
- 钩子在标记已字节相等时第二次写入返回 `unchanged`（无 mtime 变化）
- `bump-plugin.mjs codegraph patch` 成功同步 4 个 manifest + catalog.json
- marketplace hub 注册后，`sync-marketplaces.mjs --write` 三平台清单一致

## Rollout

- v0.1.0 (本次): 仓库就绪 + 本地测试 + marketplace 注册 + 三个 platform 清单一致
- v0.1.x: 跟随 codegraph 上游 `instructions-template.ts` 同步
- v0.2.0 (后续): 如果发现用户强烈需求，加入 `/codegraph-explore` 这类「调用 MCP 工具」的快捷命令包装