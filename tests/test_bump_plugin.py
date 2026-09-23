"""bump-plugin.mjs CLI 冒烟测试.

图谱深查确认 resolvePluginsRoot / bump 是全仓唯二真无测试的热点
（hooks 的 main/read_payload 由子进程烟测覆盖，属图谱假阳性，不在此列）。
用真实 CLI 冒烟覆盖: 无参/坏 level/坏 plugin-id 退出码 + --dry-run 计划形状
（含 bump() 版本递增输出与 resolvePluginsRoot 定位，脚本启动即执行）。

所有用例不写任何文件（--dry-run 与错误路径都在写盘前退出）。
node 不可用时 skip——工具 shell 与登录 shell 的 PATH 不一致是已知环境坑。
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "bump-plugin.mjs"


def find_node() -> str | None:
    node = shutil.which("node")
    if node:
        return node
    nvm_glob = sorted((Path.home() / ".nvm" / "versions" / "node").glob("*/bin/node"))
    return str(nvm_glob[-1]) if nvm_glob else None


NODE = find_node()


@unittest.skipUnless(NODE, "node 不可用（PATH 与 nvm 均未找到）")
class TestBumpPluginCli(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [NODE, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PLUGIN_ROOT),
        )

    def test_no_args_prints_usage(self) -> None:
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("用法", proc.stderr)

    def test_bad_level_rejected(self) -> None:
        proc = self.run_cli("codegraph", "banana")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("用法", proc.stderr)

    def test_unknown_plugin_id(self) -> None:
        proc = self.run_cli("no-such-plugin", "patch")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("没有插件", proc.stderr)

    def test_dry_run_plan_shape(self) -> None:
        """--dry-run 输出发版计划: 版本递增 + 5 处编辑清单，且不写盘."""
        proc = self.run_cli("codegraph", "patch", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertRegex(proc.stdout, r"codegraph \d+\.\d+\.\d+ -> \d+\.\d+\.\d+")
        self.assertIn("dry-run", proc.stdout)
        edit_lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("  - ")]
        self.assertEqual(len(edit_lines), 5, f"应有 5 处编辑计划: {edit_lines}")


if __name__ == "__main__":
    unittest.main()
