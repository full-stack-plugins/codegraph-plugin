# ADDED Requirements

## SessionStart Prompt Injection

### Scenario: 已索引 cwd

**WHEN** `SessionStart` 钩子在 `<cwd>/.codegraph/` 是目录时触发

**THEN** 钩子 SHALL:

1. 解析 `<cwd>/.claude/CLAUDE.md` 路径，**若存在**则作为写入目标
2. 否则解析 `<cwd>/AGENTS.md` 路径作为写入目标（创建文件若不存在）
3. SHALL NOT 自动创建 `<cwd>/.claude/` 目录
4. 调用 `replace_or_append_marked_section(target_path, CODEGRAPH_INSTRUCTIONS_BLOCK, "<!-- CODEGRAPH_START -->", "<!-- CODEGRAPH_END -->")` 写入标记区间
5. 字节级幂等：若标记区间已存在且内容 byte-equal，返回 `unchanged`，不触发 mtime 变化
6. 输出 JSON 到 stdout: `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "<CODEGRAPH_INSTRUCTIONS_BLOCK>"}}`

### Scenario: 未索引 cwd

**WHEN** `SessionStart` 钩子在 `<cwd>/.codegraph/` 不是目录时触发

**THEN** 钩子 SHALL:

1. 静默 exit 0
2. 不输出任何 stdout 内容
3. 不写任何文件

### Scenario: 异常

**WHEN** 钩子内部任何 IO / 解析 / 写盘操作抛出异常

**THEN** 钩子 SHALL:

1. 把异常 stderr 打印为 `[codegraph-plugin] 内部错误已忽略(fail-open): <repr>`
2. exit 0（不阻塞宿主启动）
3. 不输出 `additionalContext`（因为写盘未完成）

## CodeGraph Prompt Verbatim Sync

The block written to disk and emitted as `additionalContext` SHALL be byte-equal to the upstream `codegraph/src/installer/instructions-template.ts` `CODEGRAPH_INSTRUCTIONS_BLOCK` constant at the time of last sync. The current reference is codegraph v1.5.0 (2026-07-21).

If upstream's `instructions-template.ts` text drifts in a future codegraph release, `scripts/codegraph_lib/prompt.py` SHALL be updated to match, and the plugin SHALL be bumped (patch).