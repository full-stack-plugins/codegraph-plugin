---
name: codegraph-helper
description: 仓库根有 `.codegraph/` 目录时使用——用户问及代码结构、callers、callees、impact、dead code、circular deps、type hierarchy、complexity 时，代码理解一律先走 CodeGraph。MCP 默认只暴露 `codegraph_explore` 一个工具，绝大多数问题它一次调用即可返回相关符号的逐字源码 + 调用路径；它答不全时（或非 MCP 宿主、subagent）走 `codegraph` CLI（`codegraph explore` / `callers` / `callees` / `impact` / `node` / `query` / `context` / `files` / `status` / `affected`）。**不要调用 `codegraph_callers` / `codegraph_callees` / `codegraph_impact` / `codegraph_node` / `codegraph_search` / `codegraph_files` / `codegraph_status` 这 7 个 MCP 工具**——它们默认不对 agent 列出，调用会返回 `Tool ... is disabled via CODEGRAPH_MCP_TOOLS` 错误，请改用同名 CLI 子命令。`.codegraph/` 不存在时引导用户运行 `/codegraph-init`。
license: Apache-2.0
---

# CodeGraph Helper

仓库已通过 `codegraph init` 索引后，**所有代码理解类问题**先尝试 CodeGraph 工具——`codegraph_explore` 一调用即返回相关符号源码 + 调用路径，比 Read + grep 快一个数量级。

## 何时用

- 用户问「X 在哪里定义 / 谁调用了 X / X 调用了谁 / 改 X 会影响什么 / X 的实现源码 / 项目的文件结构」。
- 用户做重构前需要 blast radius。
- 用户问「改完 X 该跑哪些测试」。

## 何时不用

- 仓库尚未 `codegraph init`（根目录没有 `.codegraph/`）：先运行 `/codegraph-init` 或提示用户跑 `codegraph init <path>`。
- 用户问「git log / 倒 L」「git blame」「最近 commit」——这些是 Git 工具。
- 用户问「运行测试 / build / 部署」——这些是语言工具链，不是代码理解。
- 用户问「怎么写代码」——这是创作任务，不是检索任务。

## MCP 工具

**默认只暴露一个工具**——上游 `DEFAULT_MCP_TOOLS = ['explore']`（`codegraph/src/mcp/tools.ts`），其余 7 个 handler 仍在但**不向 agent 列出**，直接调用会返回 `Tool ... is disabled via CODEGRAPH_MCP_TOOLS` 错误。

| 工具 | 状态 | 用途 |
|---|---|---|
| `codegraph_explore(query, maxFiles)` | ✅ **默认可用** | **主工具**：一次返回相关符号逐字源码 + 调用路径（含 grep 跟不动的动态派发跳转） |

需要 `callers` / `callees` / `impact` / `node` / `search` / `files` / `status` 时，**走下面的 CLI 表**，不要找 MCP 工具名。若用户显式要求，可提示设置
`CODEGRAPH_MCP_TOOLS=explore,node,search,callers,callees,impact,files,status` 重新启用——但那是改用户环境，需先征得同意。

## CLI（默认路径，MCP 之外的正确选择）

宿主不是 MCP、或需要上表以外的能力时，用 `codegraph` CLI：

| CLI 命令 | 用途 | 对应 MCP |
|---|---|---|
| `codegraph explore "<query>"` | 相关符号源码 + 调用路径（与 `codegraph_explore` 同输出） | ✅ 默认可用 |
| `codegraph context "<task>"` | 为任务构建符号 + 关系 + 代码块（`--format json` 可机读） | 无 MCP 等价 |
| `codegraph callers X` | 谁调用了 X | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph callees X` | X 调用了谁 | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph impact X` | 修改 X 影响什么（重构前必用） | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph node X` | 单符号源码 + 调用链 | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph query <search>` | 按名搜索符号位置 | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph affected <files...>` | 改动影响哪些测试文件 | 无 MCP 等价 |
| `codegraph files` | 索引文件树 | 需 `CODEGRAPH_MCP_TOOLS` |
| `codegraph status` | 索引健康（仅调试） | 需 `CODEGRAPH_MCP_TOOLS` |

完整 21 命令清单见 [references/commands-reference.md](references/commands-reference.md)。

## 注入的官方提示词

完整 verbatim 见 [references/instructions-block.md](references/instructions-block.md)。本 skill 的 description 优先在 `.codegraph/` 存在的项目里把智能体引导到上面的工具；当仓库未索引时通过 SessionStart 钩子不打扰用户（钩子只在 `.codegraph/` 存在时触发）。

## 注意事项

- 0 影响 ≠ 安全。dynamic dispatch、运行时多态、配置驱动的分支不会被静态索引覆盖。
- `codegraph callers` / `codegraph impact` 包含 class instantiation sites（#774 之后）。
- 项目升级 codegraph 后若上游 instructions 文本漂移，需重新同步本插件（参见 `AGENTS.md` 纪律）。

## 不做的事

- 不主动跑 `codegraph init`（索引是用户决策）。
- 不修改代码、不修改 `.gitignore`、不在 vendored skill 目录创建文件。
- 不读取或上传任何源代码到外部。