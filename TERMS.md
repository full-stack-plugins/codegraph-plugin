# 使用条款

## 适用

- 本插件是 Apache-2.0 开源软件，按「现状」提供。
- 使用本插件需要在用户机器上已安装上游 `codegraph` CLI（https://github.com/colbymchenry/codegraph，MIT 协议）。
- 本插件的功能是把 `codegraph` CLI 的能力以 slash 命令 + SessionStart 提示词注入的方式暴露给 AI 编码代理。

## 责任边界

- 本插件不修改、读取或上传用户的源代码。
- 本插件不替代 `codegraph install`（一次性 MCP wiring），也不替代 `codegraph init`（构建索引）。
- 本插件不替代 `codegraph` 自身的升级；用户应定期 `codegraph upgrade`，本插件在 `codegraph upgrade` 后只更新提示词文本同步（参见 `AGENTS.md` 纪律）。
- 本插件对 `codegraph` 的输出不做任何二次封装或语义改写。

## 终止

- 卸载插件：在宿主代理中停用插件即可。已写入 `<cwd>/.claude/CLAUDE.md` 或 `<cwd>/AGENTS.md` 的标记区间不会被自动清除（用户可手动删除）。
- 本插件不在任何远端保留任何状态。

## 数据

- 全部在本地文件系统运行；无云端依赖。
- 详细见 `PRIVACY.md`。

## 联系

Issues: https://github.com/full-stack-plugins/codegraph-plugin/issues