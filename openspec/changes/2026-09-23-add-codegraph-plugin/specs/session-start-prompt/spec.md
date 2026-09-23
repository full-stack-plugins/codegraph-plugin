## ADDED Requirements

### Requirement: SessionStart Prompt Injection

When the host fires SessionStart, the plugin hook SHALL detect whether the working directory is CodeGraph-indexed, write the official prompt block to the host instruction file, and inject the same block as session context. The hook SHALL always fail open.

#### Scenario: 已索引 cwd

**WHEN** SessionStart 钩子在 `<cwd>/.codegraph/` 是目录时触发

**THEN** 钩子 SHALL 解析 `<cwd>/.claude/CLAUDE.md`（存在则优先）否则 `<cwd>/AGENTS.md` 作为写入目标，不自动创建 `.claude/` 目录，以标记区间原子写入 CODEGRAPH_INSTRUCTIONS_BLOCK（字节级幂等），并向 stdout 输出 `hookSpecificOutput.additionalContext` JSON。

#### Scenario: 未索引 cwd

**WHEN** SessionStart 钩子在 `<cwd>/.codegraph/` 不是目录时触发

**THEN** 钩子 SHALL 静默 exit 0，不输出任何 stdout 内容，不写任何文件。

#### Scenario: 异常

**WHEN** 钩子内部任何 IO / 解析 / 写盘操作抛出异常

**THEN** 钩子 SHALL 打印 `[codegraph-plugin] 内部错误已忽略(fail-open)` 到 stderr 并 exit 0，不阻塞宿主启动。

### Requirement: CodeGraph Prompt Verbatim Sync

The block written to disk and emitted as additionalContext SHALL be byte-equal to the upstream codegraph instructions-template.ts CODEGRAPH_INSTRUCTIONS_BLOCK constant at the time of last sync. The current reference is codegraph v1.5.0 (2026-07-21).

#### Scenario: 上游文本漂移

**WHEN** 上游 codegraph 发布新版本且 instructions-template.ts 的文本发生变化

**THEN** 本插件 SHALL 更新 scripts/codegraph_lib/prompt.py 为新文本，bump patch 版本并通过 bump-plugin.mjs 同步全部 manifest，核对 references/instructions-block.md 的 verbatim 引用。
