# CodeGraph Plugin — 架构（中文）

## 分层设计

```
┌──────────────────────────────────────────────────────────┐
│ 宿主代理 (Claude Code / Codex / ZCode / Kimi)              │
│  SessionStart ──┐                                       │
│  Slash 命令 ────┼───────────────────────────────┐         │
└─────────────────┼───────────────────────────────┼─────────┘
                  │                               │
                  ▼                               ▼
   ┌──────────────────────────┐    ┌──────────────────────────┐
   │ hooks/inject_codegraph_  │    │ commands/codegraph-*.   │
   │ prompt.py                │    │ json (Kimi)             │
   │ (SessionStart 钩子)      │    │ kimi-commands/          │
   │                          │    │ codegraph-*.md (Codex)  │
   └─────────┬────────────────┘    └────────────┬─────────────┘
             │                                │
             ▼                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │ scripts/codegraph_lib/                                    │
   │  • prompt.py         — verbatim 提示词块                  │
   │  • instructions_writer.py — 标记区间原子 I/O              │
   │  • host_targets.py   — 解析 CLAUDE.md vs AGENTS.md       │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 文件系统 (读 / 写)                                       │
   │  <cwd>/.codegraph/  ← 仅检测 (只读)                       │
   │  <cwd>/.claude/CLAUDE.md  ← 写入 (若存在)                 │
   │  <cwd>/AGENTS.md          ← 写入 (兜底)                    │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────┐
   │ codegraph CLI (上游, MIT)                                  │
   │  • codegraph init / sync / index / status / explore /    │
   │    callers / callees / impact / affected / 等           │
   └──────────────────────────────────────────────────────────┘
```

## 失败语义

| 失败 | 行为 |
|---|---|
| `cwd` 没有 `.codegraph/` | 钩子静默 exit 0。插件什么都不做。 |
| `cwd` 既无 `.claude/CLAUDE.md` 也无 `AGENTS.md` | 钩子写到 `AGENTS.md`（不存在则创建）。**绝不自动创建 `.claude/`**。 |
| 标记区间已字节相等 | `replace_or_append_marked_section` 返回 `unchanged`，不写盘。 |
| 写盘过程 I/O 错误 | 捕获，stderr 记录，但 `additionalContext` 仍输出。 |
| `codegraph` CLI 不在 PATH | slash 命令失败并给出明确错误；SessionStart 钩子不受影响。 |
| 其他任何异常 | fail-open: exit 0, stderr 记录。宿主永远看不到本插件的错误。 |

## 为什么是 SessionStart additionalContext + CLAUDE.md 写入

codegraph 自家的 `codegraph install` 只写 `<cwd>/.claude/CLAUDE.md`。这能覆盖 **Task 工具子代理**（它们读项目 instructions 文件），但**不能**直接注入主代理的运行时上下文（MCP `initialize` 响应覆盖主代理，文件覆盖不到）。

本插件的双轨方式覆盖两类读者：

| 读者 | 覆盖方式 |
|---|---|
| 主代理（MCP-aware） | `SessionStart.additionalContext` |
| 主代理（无 MCP / 非 MCP 宿主） | 由 **文件写入** 触发 `codegraph explore "<query>"` shell 回退 |
| Task 工具子代理 | CLAUDE.md / AGENTS.md 文件 |
| sub-sub-sub（罕见） | 文件（通过项目 instructions 继承） |

## 为什么只挂 SessionStart

- `PreToolUse` / `PostToolUse` 会与 codeguard-plugin 的硬门禁抢触发器。
- `UserPromptSubmit` 高频匹配（commit/push）增加延迟；本插件没有时效性任务。
- `Stop` 总结是 codeguard 的领域。

## 本地技能 vs Vendor 技能

- **零 vendor 技能**。`skills.lock.json` 为空。
- **一个本地技能**（`codegraph-helper`），登记在 `plugin-local-skills.json` 中。

这限制了插件的爆炸半径：无第三方维护负担。

## 版本纪律

- 任何代码改动 → 跑 `node scripts/bump-plugin.mjs codegraph patch|minor|major`，同步 4 个 manifest + catalog.json。
- patch 专门留给上游文本同步 + bug fix。
- minor 加新 slash 命令或钩子。
- major 改标记格式或重写钩子行为。

## 为什么纯 Python stdlib

- 零运行时依赖 → 不需要 `pip install`，无供应链风险。
- 插件的热路径是 `Path` 操作 + JSON 读写——不需要 `requests`、`httpx` 或任何网络库。
- 没有第三方代码就没有第三方安全边界。