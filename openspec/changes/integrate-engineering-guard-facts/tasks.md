# codegraph-plugin 工程守卫集成任务

来源：2026-10-17 按既有总体规划重建；原引用路径在当前检出及本地可用历史中未找到。本变更是新重建的任务定义，不声称恢复了历史原文，也不声明实现或用户验收已完成。依据为 [traceability](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/traceability.md)、[acceptance](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/acceptance.md)、[protocol](https://github.com/full-stack-plugins/codeguard/blob/8d7c0e997bf21b3306573b3be89ff8c312c9de38/docs/engineering-guard/protocol.md) 与本仓现有维护约束。

状态：全部待实施。完成状态只在本账本维护；实现与所需真实环境验证齐备后才能勾选。每行列出的依赖是前置验收义务，不把文档创建当成前置实现完成。

## 1. 实施与验证

- [ ] 1.1 **EG-F01** [owner=codegraph-plugin] 固定既有 CLI/MCP 客户端职责、提示原文与 SessionStart 行为，记录当前 provider/插件身份；正常与缺 CLI 启动均实测。 依赖：EG-M01。规格：EG-CGP-001, EG-CGP-005。

- [ ] 1.2 **EG-F02** [owner=codegraph-plugin] 实现无写 doctor/索引身份检查与显式维护授权边界；缺索引、旧索引、未授权 sync 反例检查文件/refs/网络均无变化。 依赖：EG-F01。规格：EG-CGP-002, EG-CGP-003。

- [ ] 1.3 **EG-F03** [owner=codegraph-plugin] 提供可独立验收的 provider 兼容描述及固定版本探测；缺/不兼容 provider 返回准备阻塞，不能依赖七产品最终发布才可探测。 依赖：EG-F01, EG-K01。规格：EG-CGP-004, EG-CGP-005。

- [ ] 1.4 **EG-F04** [owner=codegraph-plugin] 适配现有 CodeGraph 原始输出到版本化事实入口并保留原件；未知版本、损坏输出拒绝，查询 success 不成为工程通过。 依赖：EG-F03。规格：EG-CGP-001, EG-CGP-005。

- [ ] 1.5 **EG-F05** [owner=codegraph-plugin] 实现原始路径、symbol/edge/sourceSpan、source/index/producer 摘要映射；真实查询与源码位置对照，旧候选不可复用。 依赖：EG-F02, EG-F04。规格：EG-CGP-002, EG-CGP-004。

- [ ] 1.6 **EG-F06** [owner=codegraph-plugin] 实现语言/解析方式/coverage/limitations 与输出预算，包含截断、动态边未知和独立合法反例。 依赖：EG-F05。规格：EG-CGP-004。

- [ ] 1.7 **EG-F07** [owner=codegraph-plugin] 与 ArchGuard/GitGuard/TestGuard 消费方执行共同事实黄金样本及真实查询对照；不支持语言保持 unknown。 依赖：EG-F06, EG-K21。规格：EG-CGP-002, EG-CGP-005。

- [ ] 1.8 **EG-F08** [owner=codegraph-plugin] 完成实际宿主安装/启动/查询/移除、N/N-1 互操作与发布清单；原提示与 fail-open 行为不漂移，缺格保持未验收。 依赖：EG-F07, EG-K20。规格：EG-CGP-001, EG-CGP-005。
