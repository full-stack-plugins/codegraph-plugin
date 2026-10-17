## Purpose

定义 codegraph-plugin 在七产品工程守卫体系中的证据和集成契约；沿用现有插件边界，不以报告、模型或本地 Hook 自称交付授权。

来源：2026-10-17 按既有总体规划重建；原引用路径在当前检出及本地可用历史中未找到。本变更是新重建的任务定义，不声称恢复了历史原文，也不声明实现或用户验收已完成。依据为 [traceability](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/traceability.md)、[acceptance](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/acceptance.md)、[protocol](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/protocol.md) 与本仓现有维护约束。

## ADDED Requirements

### Requirement: EG-CGP-001 Client boundary

系统 SHALL 插件只调度已安装的上游 CodeGraph CLI/MCP，不复制上游实现、专业规则、持久数据库或授权判定。官方提示保持原文，SessionStart 的故障不得阻断宿主启动。

#### Scenario: EG-CGP-001 reject unsupported or unsafe input

- **WHEN** 无 CLI 或调用失败
- **THEN** 报告能力不可用，启动保持原有 fail-open；工程流程消费者仍按缺证据处理

#### Scenario: EG-CGP-001 preserve supported behavior

- **WHEN** 已安装兼容版本且用户显式查询
- **THEN** 返回来源与能力声明，不把查询成功改写为工程放行

### Requirement: EG-CGP-002 Fact identity

系统 SHALL 输出事实必须保留当前来源摘要、生产者/适配器版本、索引身份、符号/位置、解析方式和覆盖限制，不同候选或旧索引不得重新贴标签为当前事实。

#### Scenario: EG-CGP-002 reject unsupported or unsafe input

- **WHEN** 源码已改变但索引未更新
- **THEN** 标记 stale/unknown，保留原始输出和身份

#### Scenario: EG-CGP-002 preserve supported behavior

- **WHEN** 索引与实际来源相符且查询完整
- **THEN** 返回可定位的事实并保留原始引用

### Requirement: EG-CGP-003 Explicit indexing

系统 SHALL 只读发现和普通查询不得执行 install/init/sync、建索引、修改 refs 或隐式外发源码；索引建立或刷新只接受用户针对该动作的显式授权。

#### Scenario: EG-CGP-003 reject unsupported or unsafe input

- **WHEN** 目标没有索引或索引不兼容
- **THEN** 列出准备缺口，不自动初始化或同步

#### Scenario: EG-CGP-003 preserve supported behavior

- **WHEN** 用户明确授权索引维护
- **THEN** 仅执行既有 CLI 对应动作并重新检查身份

### Requirement: EG-CGP-004 Bounded capabilities

系统 SHALL 能力报告必须按语言、版本和解析种类声明边界；截断、动态派发不完整、无解析覆盖或输出超限均不能宣称完整调用图或架构通过。

#### Scenario: EG-CGP-004 reject unsupported or unsafe input

- **WHEN** 输出截断或动态边无法解析
- **THEN** 保留已知事实并标注不完整，不消除必需验证

#### Scenario: EG-CGP-004 preserve supported behavior

- **WHEN** 受支持查询在预算内完整返回
- **THEN** 只对声明范围提供确定事实

### Requirement: EG-CGP-005 Lifecycle compatibility

系统 SHALL 插件必须维持原有安装/启动/移除行为，固定 provider 与协议兼容范围，逐宿主验证 N/N-1 和未知版本拒绝；运行失败不静默切换另一二进制或弱实现。

#### Scenario: EG-CGP-005 reject unsupported or unsafe input

- **WHEN** 未知 major 或制品摘要不符
- **THEN** 拒绝解释为兼容事实，给出诊断

#### Scenario: EG-CGP-005 preserve supported behavior

- **WHEN** 受支持组合安装、查询并移除
- **THEN** 实际事件与原行为兼容，移除只清理自身标记
