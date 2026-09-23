# 隐私政策

**codegraph-plugin** 是**纯客户端**插件，全部在用户机器上运行。

## 收集的数据

**无。** 本插件：

- 不联网回传
- 不发送使用统计、分析或崩溃报告
- 不读取用户源代码上传
- 不需要任何认证

所有操作均在本地：

- 读取 `codegraph` CLI 版本（`command -v codegraph`、`codegraph version`）
- 读取 `<cwd>/.codegraph/` 是否存在（仅目录探测，不读图谱内容）
- 把官方 CodeGraph 提示词块写入 `<cwd>/.claude/CLAUDE.md` 或 `<cwd>/AGENTS.md`（标记区间替换）
- 列出用户输入的 slash 命令名，作为 `codegraph <command>` CLI 调用透传给上游

## 网络请求

无。

## 源码

- Apache-2.0 协议，完全开源可审计。
- 上游 `codegraph` 自身是 MIT 协议（Colby McHenry），本插件不修改它，只在官方 CLI 之上做编排。

## 第三方依赖

无运行时第三方依赖。纯 Python 标准库。

## 联系

Issues: https://github.com/full-stack-plugins/codegraph-plugin/issues