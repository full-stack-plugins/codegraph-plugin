# codegraph-plugin 维护约束

- 任何代码改动走 `node scripts/bump-plugin.mjs codegraph patch|minor|major` 同步 4 个 manifest + catalog.json + 三平台 marketplace。
- 提示词文本必须 verbatim 同步自 `codegraph/src/installer/instructions-template.ts` 的 `CODEGRAPH_INSTRUCTIONS_BLOCK`（`scripts/codegraph_lib/prompt.py`）。每次 codegraph 升级（CHANGELOG 涉及 `instructions-template.ts`）需要手动重新同步，并在 `references/instructions-block.md` 中核对。
- SessionStart 钩子必须 fail-open，任何异常不阻断宿主启动。
- Hook 输出 `additionalContext` 内容来自 `prompt.CODEGRAPH_INSTRUCTIONS_BLOCK`，不擅自裁剪或附加额外段落。
- 写 `<cwd>/.claude/CLAUDE.md`（不存在）或 `<cwd>/AGENTS.md`（CLAUDE.md 不存在时）时，使用标记区间替换，原子写、幂等。
- 不自动创建 `<cwd>/.claude/` 目录——避免插件越权定义用户的 `.claude/` 布局。
- 不修改 `codegraph` CLI 自身；本插件只调度 `codegraph` 现有命令。
- Marketplace `description` / `shortDescription` 在三个文件（catalog.json、marketplace.json、kimi-marketplace.json）保持一致；`bump-plugin.mjs --write` 后必须人工复查。

## 版本

- 当前: v0.1.0
- 同步自 codegraph v1.5.0 的 `instructions-template.ts`
- Codex 后缀: `0.1.0+codex.YYYYMMDD`

## 同步自上游

- 升级 codegraph 后：
  1. `diff` 比对 `codegraph/src/installer/instructions-template.ts` 与 `scripts/codegraph_lib/prompt.py`
  2. 若文本漂移，更新 `prompt.py` 并 bump patch 版本
  3. CHANGELOG 记录「prompt 文本与 codegraph vX.Y.Z 同步」
- 不要把上游 `codegraph` 代码 vendor 进本插件；本插件只调度其 CLI。

## 不做的事

- 不暴露 `codegraph prompt-hook` / `codegraph serve --mcp`（codegraph 自家隐藏命令）
- 不挂 PreToolUse/PostToolUse/UserPromptSubmit/Stop 钩子（避免与 codeguard-plugin 抢触发器）
- 不自动跑 `codegraph install`（那是用户的一次性 wiring 决策，插件不能越权）
- 不读取或上传任何源代码到外部