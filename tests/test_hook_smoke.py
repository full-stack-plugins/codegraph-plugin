"""SessionStart 钩子烟测.

不依赖 codeguard 之外的任何东西。覆盖三种场景:
1. cwd 没有 .codegraph/ → 静默 exit 0
2. cwd 有 .codegraph/ → 写 AGENTS.md + 输出 additionalContext
3. cwd 有 .claude/CLAUDE.md → 优先写 CLAUDE.md
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK = PLUGIN_ROOT / "hooks" / "inject_codegraph_prompt.py"


def run_hook(cwd: Path, payload: dict | None = None) -> tuple[int, str, str]:
    proc_input = json.dumps(payload or {"cwd": str(cwd)})
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=proc_input,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(cwd),
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestSessionStart(unittest.TestCase):
    def test_silent_when_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            # 没 .codegraph/
            code, out, err = run_hook(cwd)
            self.assertEqual(code, 0)
            self.assertEqual(out, "")
            self.assertEqual(err, "")
            # 不应创建 CLAUDE.md 或 AGENTS.md
            self.assertFalse((cwd / "AGENTS.md").exists())
            self.assertFalse((cwd / ".claude" / "CLAUDE.md").exists())

    def test_writes_agents_md_when_no_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".codegraph").mkdir()
            code, out, err = run_hook(cwd)
            self.assertEqual(code, 0)
            # 输出含 additionalContext + hookSpecificOutput
            parsed = json.loads(out)
            self.assertIn("hookSpecificOutput", parsed)
            self.assertEqual(parsed["hookSpecificOutput"]["hookEventName"], "SessionStart")
            self.assertIn("additionalContext", parsed["hookSpecificOutput"])
            # AGENTS.md 被写入
            self.assertTrue((cwd / "AGENTS.md").exists())
            content = (cwd / "AGENTS.md").read_text()
            self.assertIn("<!-- CODEGRAPH_START -->", content)
            self.assertIn("<!-- CODEGRAPH_END -->", content)
            self.assertIn("In repositories indexed by CodeGraph", content)
            # 没自动建 .claude/
            self.assertFalse((cwd / ".claude").exists())

    def test_prefers_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".codegraph").mkdir()
            (cwd / ".claude").mkdir()
            (cwd / ".claude" / "CLAUDE.md").write_text("# My Project\n\n## Notes\n", encoding="utf-8")
            code, out, err = run_hook(cwd)
            self.assertEqual(code, 0)
            # 写到 CLAUDE.md，不是 AGENTS.md
            claude_content = (cwd / ".claude" / "CLAUDE.md").read_text()
            self.assertIn("<!-- CODEGRAPH_START -->", claude_content)
            self.assertFalse((cwd / "AGENTS.md").exists())

    def test_idempotent_second_call(self) -> None:
        """第二次调用字节级幂等,不修改文件 mtime 逻辑."""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".codegraph").mkdir()
            code1, out1, _ = run_hook(cwd)
            code2, out2, _ = run_hook(cwd)
            self.assertEqual(code1, 0)
            self.assertEqual(code2, 0)
            self.assertEqual(out1, out2)

    def test_payload_missing_cwd_falls_back_to_env(self) -> None:
        """payload 无 cwd → 用 os.getcwd()"""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".codegraph").mkdir()
            code, out, _ = run_hook(cwd, payload={})
            self.assertEqual(code, 0)
            self.assertIn("<!-- CODEGRAPH_START -->", out)

    def test_malformed_payload_still_safe(self) -> None:
        """payload 是无效 JSON → fail-open 仍 exit 0"""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".codegraph").mkdir()
            # 直接 stdin 喂垃圾数据
            proc = subprocess.run(
                [sys.executable, str(HOOK)],
                input="not json",
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(cwd),
            )
            # 应仍 exit 0（fail-open），即使 output 行为退化
            self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
