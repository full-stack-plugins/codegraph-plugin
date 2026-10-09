## Purpose

为 Partme Guard 提供 engineering-fact-provider 的可观察行为契约，统一已批准约束、当前候选和独立验证证据的关联，并明确未知、失败、兼容模式与越权情况下不得伪造工程通过的边界。

## ADDED Requirements

### Requirement: EG-CGP-001 Client boundary

插件 SHALL 保持现有命令客户端和 SessionStart 提示定位；不改上游 CLI、不增加阻断 Hook、不在本插件重复实现工程策略或图谱引擎。

#### Scenario: EG-CGP-001 contract behavior
- **WHEN** 未安装统一工程内核或会话 Hook 异常
- **THEN** 保留原静默/fail-open 行为，不阻断宿主启动

### Requirement: EG-CGP-002 Fact identity

集成契约 SHALL 为图谱事实提供 CLI/索引版本、查询范围、源码摘要、位置、解析类型和覆盖限制；领域事实适配由 ArchGuard 实现，GuardCore 仅定义通用 envelope。

#### Scenario: EG-CGP-002 contract behavior
- **WHEN** 已有索引与候选文件不同或引擎版本不兼容
- **THEN** 标记 stale/unknown，不能作为完整架构负向证明

### Requirement: EG-CGP-003 Explicit indexing

插件 MUST 遵守索引创建、重建与配置的显式授权；只读接入检测不自动 init/sync/install。

#### Scenario: EG-CGP-003 contract behavior
- **WHEN** 发现没有索引
- **THEN** 报告缺失；可用的其他确定性检查继续，缺图谱义务保持未知

### Requirement: EG-CGP-004 Bounded capabilities

集成 SHALL 区分稳定结构化输出与自然语言发现输出；截断、动态分派未解析及不支持语法明确披露。

#### Scenario: EG-CGP-004 contract behavior
- **WHEN** 查询只返回部分调用关系
- **THEN** 结果不得声明无其他依赖或已完整发现冲突

### Requirement: EG-CGP-005 Lifecycle compatibility

插件 SHALL 保持官方提示词原文、命令目录归属、用户文档原子维护和既有独立运行；分发与宿主验收分别留证。

#### Scenario: EG-CGP-005 contract behavior
- **WHEN** 新增治理说明后启动会话
- **THEN** additionalContext 仍来自原文块，不混入自造门禁指令
