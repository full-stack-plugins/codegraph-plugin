---
name: codegraph-helper
description: 仓库根有 `.codegraph/` 目录时使用——用户问及代码结构、callers、callees、impact、dead code、circular deps、type hierarchy、complexity 时，优先调用 codegraph MCP 工具（codegraph_explore / codegraph_callers / codegraph_callees / codegraph_impact / codegraph_node / codegraph_search / codegraph_files / codegraph_status）。MCP 不可用时回退到 `codegraph` CLI。`.codegraph/` 不存在时引导用户运行 `/codegraph-init`。
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

## MCP 工具（默认 `codegraph_explore` 暴露）

| 工具 | 用途 |
|---|---|
| `codegraph_explore(query, maxFiles)` | **主工具**：一次返回相关符号源码 + 调用路径 |
| `codegraph_callers(symbol, limit)` | 谁调用了 X |
| `codegraph_callees(symbol, limit)` | X 调用了谁 |
| `codegraph_impact(symbol, depth)` | 修改 X 影响什么（重构前必用） |
| `codegraph_node(symbol, includeCode)` | 单符号源码 + 调用链 |
| `codegraph_search(query, kind, limit)` | 按名搜索符号位置 |
| `codegraph_files(format)` | 索引文件树 |
| `codegraph_status()` | 索引健康（仅调试） |

> 7 个非默认工具需 `CODEGRAPH_MCP_TOOLS=explore,node,search,callers,callees,impact,files,status` 环境变量启用。

## CLI 回退

MCP 不可用时（subagent / 非 MCP 宿主 / `codegraph_explore` 之外的任务），回退到 `codegraph` CLI：

| CLI 命令 | MCP 等价 |
|---|---|
| `codegraph explore "<query>"` | `codegraph_explore` |
| `codegraph callers X` | `codegraph_callers` |
| `codegraph callees X` | `codegraph_callees` |
| `codegraph impact X` | `codegraph_impact` |
| `codegraph node X` | `codegraph_node` |
| `codegraph query <search>` | `codegraph_search` |
| `codegraph files` | `codegraph_files` |
| `codegraph status` | `codegraph_status` |

完整 20 命令清单见 [references/commands-reference.md](references/commands-reference.md)。

## 注入的官方提示词

完整 verbatim 见 [references/instructions-block.md](references/instructions-block.md)。本 skill 的 description 优先在 `.codegraph/` 存在的项目里把智能体引导到上面的工具；当仓库未索引时通过 SessionStart 钩子不打扰用户（钩子只在 `.codegraph/` 存在时触发）。

## 注意事项

- 0 影响 ≠ 安全。dynamic dispatch、运行时多态、配置驱动的分支不会被静态索引覆盖。
- `codegraph_callers` / `codegraph_impact` 包含 class instantiation sites（#774 之后）。
- 项目升级 codegraph 后若上游 instructions 文本漂移，需重新同步本插件（参见 `AGENTS.md` 纪律）。

## 不做的事

- 不主动跑 `codegraph init`（索引是用户决策）。
- 不修改代码、不修改 `.gitignore`、不在 vendored skill 目录创建文件。
- 不读取或上传任何源代码到外部。