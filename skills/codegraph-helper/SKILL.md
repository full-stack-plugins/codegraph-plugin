---
name: codegraph-helper
description: 用户问及代码结构、X 在哪里定义、谁调用了 X、改 X 会影响什么、dead code、circular deps、type hierarchy、complexity、改完该跑哪些测试时使用——**无论仓库是否已建立 CodeGraph 索引**。先用一次检查确认仓库根是否有 `.codegraph/`：有则代码理解一律先走 CodeGraph（`codegraph_explore` 一次调用即可返回相关符号的逐字源码 + 调用路径，比 Read + grep 快一个数量级，答不全时走 `codegraph` CLI 子命令）；无则主动告诉用户「此仓库尚未索引，建立后我就能这样回答」，征得同意后运行 `codegraph init` 再继续。注意 MCP 默认只暴露 `codegraph_explore`，`codegraph_callers` / `callees` / `impact` / `node` / `search` / `files` / `status` 这 7 个默认不对 agent 列出，调用会返回 disabled 错误，请改用同名 CLI 子命令。
license: Apache-2.0
---

# CodeGraph Helper

## 0. 先检查，再行动

回答任何代码理解类问题**之前**，先确认仓库根是否有 `.codegraph/` 目录：

```bash
codegraph status          # 或直接检查 <repo-root>/.codegraph/ 是否存在
```

- **已索引** → 走下面的「已索引：怎么查」，用 CodeGraph 回答，**不要退回 Read + grep**。
- **未索引** → 走下面的「未索引：先提示用户」，**不要用 Read + grep 硬扛**，也不要在用户没同意前擅自索引。

## 1. 未索引：先提示用户

未建立索引时，代码理解只能靠 Read + grep，既慢又贵。此时**主动告知用户**并征得同意：

> 此仓库尚未建立 CodeGraph 索引。建立后，我可以用 `codegraph_explore` 一次调用拿到相关符号的逐字源码和调用路径，比 Read + grep 快一个数量级。现在索引吗？

- 用户同意 → 运行 `codegraph init`（即 `/codegraph-init`），完成后按「已索引」流程继续回答。
- 用户拒绝或未回应 → 按常规方式回答，**不要反复劝说**，也不要擅自索引。
- 用户本就问的是非代码问题（见「何时不用」）→ 不要提索引。

`codegraph init` 会在仓库根创建 `.codegraph/`，属于写盘操作，所以**必须先问**。已索引仓库的只读查询则不需要任何确认。

## 2. 已索引：怎么查

`codegraph_explore` 一调用即返回相关符号逐字源码 + 调用路径，比 Read + grep 快一个数量级。

## 何时用

- 用户问「X 在哪里定义 / 谁调用了 X / X 调用了谁 / 改 X 会影响什么 / X 的实现源码 / 项目的文件结构」。
- 用户做重构前需要 blast radius。
- 用户问「改完 X 该跑哪些测试」。

**未索引的仓库同样适用**——先检查、再按「未索引：先提示用户」处理，不要因为没有 `.codegraph/` 就当本技能不适用。

## 何时不用

以下情况与索引状态无关，直接不用 CodeGraph，**也不要提索引**：

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

完整 verbatim 见 [references/instructions-block.md](references/instructions-block.md)。SessionStart 钩子**只在已索引仓库**注入该块——这与上游原文 "If there is no `.codegraph/` directory, skip CodeGraph entirely" 一致，未索引时靠本技能的「先检查 → 提示用户」通路兜底。

## 注意事项

- 0 影响 ≠ 安全。dynamic dispatch、运行时多态、配置驱动的分支不会被静态索引覆盖。
- `codegraph callers` / `codegraph impact` 包含 class instantiation sites（#774 之后）。
- 项目升级 codegraph 后若上游 instructions 文本漂移，需重新同步本插件（参见 `AGENTS.md` 纪律）。

## 不做的事

- **不在用户同意前跑 `codegraph init`**——索引会在仓库根写 `.codegraph/`，必须先征得同意。但**要主动检查并主动提示**（见「先检查，再行动」），不能因为怕越权就当没看见。
- 不自动跑 `codegraph install`（MCP wiring 是用户的一次性配置决策，插件不代劳）。
- 不修改代码、不修改 `.gitignore`、不在 vendored skill 目录创建文件。
- 不读取或上传任何源代码到外部。