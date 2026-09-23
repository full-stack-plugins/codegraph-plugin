# CodeGraph Plugin

> 让 CodeGraph 在 AI 编码代理中被自然想起——官方提示词注入 + 全量 20 个 CLI 命令暴露为 slash 命令。面向 Codex / ZCode / Kimi / Claude Code。

![CodeGraph Plugin](assets/banner.svg)

> **Parity**: README.md 与 README.zh-CN.md 必须保持相同的标题结构、链接和版本号；由 tests/test_readme_parity.py 强制。
>
> [English](README.md) · [简体中文](README.zh-CN.md)

## 本插件做什么

只做三件事，**严格只这三件**：

1. **会话启动时**，当 `<cwd>/.codegraph/` 存在时，把官方 CodeGraph 提示词块（verbatim 同步自上游 `codegraph/src/installer/instructions-template.ts`）注入到：
   - 当前会话，通过 `SessionStart.additionalContext` JSON 输出；
   - `<cwd>/.claude/CLAUDE.md`（如果存在）；否则 `<cwd>/AGENTS.md`。使用标记区间原子替换——字节级幂等，所以与 `codegraph install` 并存是安全的。
2. **暴露 codegraph 全量 20 个 CLI 命令**为 slash 命令，Kimi（`.json`）与 Codex（`.md`）双格式，包括 4 个隐藏但实用的维护命令（`daemon` / `unlock` / `version` / `telemetry`）。
3. **注册发现型技能**（`codegraph-helper`），让智能体根据用户问题选择合适的 CodeGraph MCP 工具。

## 本插件**不**做什么

- **不**修改或替换 `codegraph` CLI。上游 [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)（MIT）是唯一权威。
- **不**安装 `codegraph` CLI。用户自行 `npm i -g @colbymchenry/codegraph`（或 install.sh）；本插件仅提供 `/codegraph-install` 作为 `codegraph install` 的引导包装。
- **不**自动跑 `codegraph init`。索引是用户的决策，本插件只在 `.codegraph/` 已存在时激活。
- **不**挂 `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `Stop` 钩子——只挂 `SessionStart`。避免和 codeguard-plugin 等其他插件抢触发器。

## 前置条件

- **可用的 `codegraph` CLI** 在 PATH 中。安装方式：
  ```bash
  curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
  # 或：
  npm i -g @colbymchenry/codegraph
  ```
- **宿主代理**（Claude Code、Cursor、Codex CLI、opencode、Hermes Agent、Gemini CLI、Antigravity、Kiro）。MCP 工具需要先 `codegraph install` 一次；否则 slash 命令会回退到 CLI。
- **cwd 下有 `.codegraph/` 目录**，SessionStart 钩子才会激活。没有时插件静默退出。

## Slash 命令

20 个命令，**一对一覆盖** codegraph CLI（除 2 个隐藏命令外）。格式与 codegraph CLI 表面对齐。

| Slash 命令 | 等价 CLI | 用途 |
|---|---|---|
| `/codegraph-init` | `codegraph init [path]` | 在当前项目初始化 CodeGraph 索引 |
| `/codegraph-uninit` | `codegraph uninit [path]` | 删除 `.codegraph/`（不可逆） |
| `/codegraph-install` | `codegraph install` | 一次性把 MCP server 接入宿主代理 |
| `/codegraph-uninstall` | `codegraph uninstall` | 移除宿主代理的 MCP wiring |
| `/codegraph-index` | `codegraph index [path]` | 从头重建索引 |
| `/codegraph-sync` | `codegraph sync [path]` | 增量同步（watcher 默认自动） |
| `/codegraph-status` | `codegraph status [path]` | 查看索引状态与统计 |
| `/codegraph-query` | `codegraph query <search>` | 按关键词搜索符号 |
| `/codegraph-explore` | `codegraph explore <query>` | 多符号源码 + 调用路径（**主入口**） |
| `/codegraph-node` | `codegraph node <name>` | 单符号源码 + 调用链，或单文件 |
| `/codegraph-files` | `codegraph files` | 索引文件树 |
| `/codegraph-callers` | `codegraph callers <symbol>` | 找谁调用了 X |
| `/codegraph-callees` | `codegraph callees <symbol>` | X 调用了谁 |
| `/codegraph-impact` | `codegraph impact <symbol>` | 改 X 影响什么 |
| `/codegraph-affected` | `codegraph affected [files]` | 受变更文件影响的测试 |
| `/codegraph-daemon` | `codegraph daemon` | 管理后台守护 |
| `/codegraph-unlock` | `codegraph unlock [path]` | 移除陈旧锁 |
| `/codegraph-version` | `codegraph version` | 打印已安装版本 |
| `/codegraph-telemetry` | `codegraph telemetry [status\|on\|off]` | 查看 / 修改遥测 |
| `/codegraph-upgrade` | `codegraph upgrade [version]` | 升级 codegraph CLI |

隐藏命令（`prompt-hook`、`serve --mcp`）**不**暴露。

## SessionStart 钩子行为

```
[SessionStart]
    │
    ▼
从 JSON payload 读 cwd（兜底: os.getcwd()）
    │
    ▼
<cwd>/.codegraph/ 是否存在？
    │
    ├─ 否  → 静默退出 0。插件不做任何事；代理继续。
    │
    └─ 是 → 解析目标文件:
              <cwd>/.claude/CLAUDE.md（存在）
              否则 <cwd>/AGENTS.md
              （绝不自动创建 <cwd>/.claude/）
                │
                ▼
              标记区间原子写（字节级幂等 → noop）
                │
                ▼
              输出 SessionStart additionalContext JSON，
              内容为完整 CodeGraph 提示词块
```

所有异常都 fail-open（exit 0）——宿主代理不会看到本插件的任何 SessionStart 错误。

## 与 `codegraph install` 的共存

codegraph 自家的 `codegraph install` 把同样的提示词块写到 `~/.claude/CLAUDE.md`（或本地 `./.claude/CLAUDE.md`）。本插件的标记区间替换是**字节级幂等**的，所以：

- 用户已跑过 `codegraph install`：本插件钩子对该集群 noop。
- 用户在本插件之后跑 `codegraph install`：codegraph installer 自家的标记写入（`codegraph/src/installer/targets/shared.ts:130-194`）也是字节级幂等——不会反复写。

本插件在 `codegraph install` 之外增加的：

- **覆盖两类读者**：codegraph installer 只写文件（通过项目 instructions 文件触达 Task 工具子代理）；本插件同时在运行时给主代理发 `additionalContext`。
- **AGENTS.md 兜底**：项目若不用 `.claude/CLAUDE.md`，写到 `AGENTS.md`（OpenSpec / 多代理通用约定）。
- **slash 命令**：codegraph install 不暴露任何；本插件覆盖全 20 个。

## 维护

- **bump 版本 + 同步 manifest** 是强制流程。任何代码改动后跑：
  ```bash
  node scripts/bump-plugin.mjs codegraph patch|minor|major
  ```
- **同步上游**：当 codegraph CHANGELOG 涉及 `instructions-template.ts`，手动重新同步 `scripts/codegraph_lib/prompt.py` 并 bump patch。详见 `AGENTS.md`。
- **本地技能** 登记在 `plugin-local-skills.json`。`skills.lock.json` 故意为空——本插件不 vendor 任何第三方技能。

## 架构

见 [`docs/codegraph-architecture.zh_CN.md`](docs/codegraph-architecture.zh_CN.md)。

## 许可证

Apache-2.0。详见 [LICENSE](LICENSE)。`scripts/codegraph_lib/prompt.py` 中的官方 CodeGraph 提示词块 verbatim 同步自上游 [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)（MIT）—— 见 [NOTICE](NOTICE) 归属说明。

## 隐私

详见 [PRIVACY.md](PRIVACY.md)。本插件纯客户端，不联网，不读取用户源代码，仅用标记区间替换写宿主指令文件。