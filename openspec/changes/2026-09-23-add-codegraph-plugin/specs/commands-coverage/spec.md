## ADDED Requirements

### Requirement: Slash Command Coverage

The plugin SHALL expose 20 slash commands covering all visible codegraph CLI subcommands, in two formats each: Kimi/ZCode host reads commands/codegraph-<verb>.json; Codex host reads kimi-commands/codegraph-<verb>.md.

#### Scenario: 全部命令成对存在

**WHEN** 检查 commands/ 与 kimi-commands/ 目录

**THEN** SHALL 满足：两个目录各含 20 个命令文件；`.json` 与同名 `.md` 的命令名集合完全相同；`.json` 含 name/description/prompt 字段且 name 与文件名一致；`.md` 含带 description 的 YAML frontmatter。

### Requirement: Hidden Commands Excluded

The plugin SHALL NOT expose codegraph's two hidden internal commands.

#### Scenario: 隐藏命令不暴露

**WHEN** 检查 20 个命令的名称清单

**THEN** SHALL NOT 包含 codegraph-prompt-hook（codegraph 自家 UserPromptSubmit 钩子端点）与 codegraph-serve（codegraph 自家 MCP stdio 入口）。

### Requirement: Format Consistency

For each slash command, the .json and .md files SHALL describe the same intent; Chinese and English localization differences are allowed.

#### Scenario: 双格式语义一致

**WHEN** 对比任一命令的 .json 与 .md

**THEN** SHALL 满足：描述同一 codegraph CLI 子命令；均不包含跨 skill 的相对路径链接（../）。
