## Why

工程守卫需要可追溯的源码关系事实，但 CodeGraph 的查询成功、旧索引或截断输出都不能直接证明架构合规。插件需明确接入契约和能力边界，同时继续保持上游 CLI 的纯客户端定位。

## What Changes

- 规划 CodeGraph 提供者的能力清单、版本/索引/源码身份和不完整结果映射；实际事实转换器由 codeguard 的工程内核持有，本插件只提供接入说明和既有命令调度约束。
- 保留仅 SessionStart、官方提示词原文、无索引静默和 fail-open；不增加阻断 Hook，不修改或 vendor 上游 CLI。
- 缺索引、过期、未知解析语义、输出截断均保留 unknown；索引创建/更新遵守用户授权。
- P3 接入符号影响与并行变更风险；P4 增加事实基线版本协商，仍不输出架构放行。

## Capabilities

### New Capabilities

- `engineering-fact-provider`: 代码事实提供者的来源、能力、覆盖和兼容契约。

### Modified Capabilities

无。既有 session-start-prompt、commands-coverage 行为保持。

## Impact

插件文档、命令能力映射、协议 fixture 和宿主验收；不改变上游 codegraph。共同协议由 codeguard/add-engineering-guard-core 持有，转换器不在两个仓库重复实现。

本轮仅规划；仓库历史 `openspec/v1` schema 不被当前 CLI 识别，新 change 显式使用可用的 spec-driven；未修改根 config 或旧 change。
