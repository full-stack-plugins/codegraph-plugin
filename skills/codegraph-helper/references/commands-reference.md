# CodeGraph 命令清单

来源：codegraph v1.6.0（`src/bin/codegraph.ts` 与 `src/mcp/tools.ts`）。codegraph 共 23 个子命令，本插件以 21 个 slash 命令覆盖其中**除 `help`、`ui`/`web` 与两个隐藏命令 `prompt-hook` / `serve --mcp` 之外的全部命令**：

- `help` —— 宿主自带帮助，无需插件暴露
- `ui`（别名 `web`）—— 打开浏览器查看器，面向人而非 agent
- `prompt-hook` / `serve --mcp` —— codegraph 自家隐藏命令，分别供 Claude Code 的 UserPromptSubmit 钩子和 MCP stdio 入口使用

## CLI 命令（21 个 slash command 已覆盖）

### 生命周期

| 命令 | 用途 |
|---|---|
| `codegraph init [path]` | 初始化 CodeGraph 索引 |
| `codegraph uninit [path]` | 删除 `.codegraph/`（不可逆） |
| `codegraph index [path]` | 全量重建索引（discard + reindex） |
| `codegraph sync [path]` | 增量同步（watcher 默认自动） |
| `codegraph status [path]` | 查看索引状态与统计 |

### 安装 / 卸载

| 命令 | 用途 |
|---|---|
| `codegraph install` | 一次性把 MCP server 接入 Claude Code / Cursor / Codex / opencode / Hermes Agent / Gemini / Antigravity / Kiro |
| `codegraph uninstall` | 移除 MCP wiring（`--keep-cli` 保留 CLI） |
| `codegraph upgrade [version]` | 升级 codegraph CLI |

### 查询 / 分析（与 MCP 工具一一对应）

| 命令 | MCP 等价工具 |
|---|---|
| `codegraph query <search>` | `codegraph_search`（默认不对 agent 列出） |
| `codegraph explore <query...>` | `codegraph_explore`（**主工具，默认唯一列出**） |
| `codegraph context <task...>` | （无 MCP 对应；CLI 专属，codegraph 1.6.0 新增） |
| `codegraph node [name]` | `codegraph_node`（默认不对 agent 列出） |
| `codegraph files` | `codegraph_files`（默认不对 agent 列出） |
| `codegraph callers <symbol>` | `codegraph_callers`（默认不对 agent 列出） |
| `codegraph callees <symbol>` | `codegraph_callees`（默认不对 agent 列出） |
| `codegraph impact <symbol>` | `codegraph_impact`（默认不对 agent 列出） |
| `codegraph affected [files...]` | （无 MCP 对应；CLI 专属） |

### 维护

| 命令 | 用途 |
|---|---|
| `codegraph daemon` | 列出 / 停止后台守护进程 |
| `codegraph unlock [path]` | 移除陈旧锁文件 |
| `codegraph version` | 打印版本（亦可用 `codegraph -v`） |
| `codegraph telemetry [status\|on\|off]` | 查看 / 修改匿名遥测开关 |

### 隐藏 / 不暴露

| 命令 | 用途 | 不暴露原因 |
|---|---|---|
| `codegraph prompt-hook` | Claude Code UserPromptSubmit 钩子端点（codegraph 自家用） | 隐藏内部命令 |
| `codegraph serve --mcp` | MCP stdio 入口（宿主代理自启动，不应手跑） | 隐藏内部命令 |
| `codegraph help` | CLI 帮助 | 宿主自带帮助 |
| `codegraph ui` / `codegraph web` | 在浏览器中打开图谱查看器 | 面向人的交互式命令，agent 无法消费 |

## MCP 工具（8 个，定义于 `src/mcp/tools.ts` 的 `tools` 数组，约 1580–1760 行——行号随上游漂移，以符号名 `name: 'codegraph_*'` 为准）

默认**只暴露 `codegraph_explore`**，其他 7 个需设置 `CODEGRAPH_MCP_TOOLS=explore,node,search,callers,callees,impact,files,status` 才能在 MCP 客户端可见。

| 工具 | 简介 |
|---|---|
| `codegraph_explore` | 主要入口——一次返回相关符号源码 + 调用路径 |
| `codegraph_search` | 按名搜索（仅位置，无源码） |
| `codegraph_callers` | 列出调用某符号的所有函数/方法 |
| `codegraph_callees` | 列出某符号调用的所有函数/方法 |
| `codegraph_impact` | 修改某符号影响的所有符号（带传递深度） |
| `codegraph_node` | 单符号源码 + 调用链，或单文件源码 + 依赖它的文件清单 |
| `codegraph_status` | 索引健康检查（调试用） |
| `codegraph_files` | 索引文件树（含语言 + 符号数） |

## 通用约定

- `codegraph` CLI 默认由用户自行 `npm i -g @colbymchenry/codegraph` 安装。
- 索引在 `<cwd>/.codegraph/`，git-friendly 吗？**否**——`.codegraph/` 应加入 `.gitignore`。
- watcher（`codegraph watch`）默认随 `codegraph init` 自动启动。`codegraph sync` 仅在 watcher degraded 时手动跑。
- 升级 codegraph 后若本插件的提示词文本未同步，会触发 SessionStart 钩子的 byte-equal 短路（无写盘操作）。此时需要手动同步 `scripts/codegraph_lib/prompt.py` 并 bump patch 版本。