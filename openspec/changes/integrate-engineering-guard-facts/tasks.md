# 工程守卫实施任务

状态：全部待实施。本轮仅完成规划；下面的 fixture/测试模块为拟新增，不声称已经存在或执行。只在实现、目标 RED→GREEN、受影响回归及所需真实环境证据齐备后勾选。

依赖前缀：K=codeguard 内核，F=codegraph-plugin，H=codeguard-plugin，R=codereview-plugin，G=gitflow-plugin，W=flowguard-plugin。跨仓依赖通过任务 ID 引用，完成状态只在所属仓账本维护。所有实现先复核当前 HEAD 与用户修改；目标路径见 [design](design.md)。

## 1. P0 提供者契约与兼容

- [ ] 1.1 **EG-F01** 核对上游 CLI 能力与当前 SessionStart/原文块/命令覆盖，先加独立运行兼容反例；不创建用户索引。 依赖：EG-K01。规格：EG-CGP-001, EG-CGP-005。
- [ ] 1.2 **EG-F02** 编制版本/索引/源码身份与授权映射 fixture；缺索引、旧索引和查询时变化必须 unknown；转换器归 core。 依赖：EG-F01。规格：EG-CGP-002, EG-CGP-003。
- [ ] 1.3 **EG-F03** 为已支持 CLI 输出提供完整/截断/坏报告 fixture 与 capability 清单；没有机器协议时明确 advisory，不虚构命令。 依赖：EG-F02。规格：EG-CGP-004。

## 2. P2 宿主与事实分发

- [ ] 2.1 **EG-F04** 执行 unittest、README parity、命令覆盖及实际宿主 SessionStart；插件文档与官方原文块分离，分别记录宿主限制。 依赖：EG-F03。规格：EG-CGP-005。

## 3. P3 符号与影响契约

- [ ] 3.1 **EG-F05** 为符号/调用/API/受影响测试定义查询能力与解析类型测试集，包含宏/反射/跨语言 unknown，供 core EG-K21 使用。 依赖：EG-F03。规格：EG-CGP-002, EG-CGP-004。
- [ ] 3.2 **EG-F06** 共同验收不同文件 API 影响样例与源码位置漂移；不据 affectedTests 删减必需回归。 依赖：EG-F05, EG-K21。规格：EG-CGP-004。

## 4. P4 基线与发行

- [ ] 4.1 **EG-F07** 定义不同上游版本与事实模型的可比性、升级/回滚和许可来源；不自动重建用户索引。 依赖：EG-F06。规格：EG-CGP-002, EG-CGP-005。
- [ ] 4.2 **EG-F08** 完成不可变版本、manifest/市场同步和安装回执；索引可用、宿主接线和治理生效分别验收。 依赖：EG-F04, EG-F07。规格：EG-CGP-001, EG-CGP-005。
