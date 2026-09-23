"""单元测试: 标记区间写入逻辑 + 宿主路径解析."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# 让脚本可以 import codegraph_lib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codegraph_lib import (
    CODEGRAPH_INSTRUCTIONS_BLOCK,
    CODEGRAPH_SECTION_END,
    CODEGRAPH_SECTION_START,
    WriteResult,
    atomic_write_file_sync,
    remove_marked_section,
    replace_or_append_marked_section,
)
from codegraph_lib import (
    host_targets as ht,
)


class TestMarkedSection(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "CLAUDE.md"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_empty(self) -> None:
        result = replace_or_append_marked_section(
            self.path,
            CODEGRAPH_INSTRUCTIONS_BLOCK,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, WriteResult.CREATED)
        self.assertTrue(self.path.exists())
        self.assertEqual(self.path.read_text(), CODEGRAPH_INSTRUCTIONS_BLOCK)

    def test_unchanged_is_idempotent(self) -> None:
        """byte-equal 第二次写应 noop."""
        # 第一次写入
        replace_or_append_marked_section(
            self.path,
            CODEGRAPH_INSTRUCTIONS_BLOCK,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        original = self.path.read_text()
        # 第二次写入同样的 body
        result = replace_or_append_marked_section(
            self.path,
            CODEGRAPH_INSTRUCTIONS_BLOCK,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, WriteResult.UNCHANGED)
        self.assertEqual(self.path.read_text(), original)

    def test_update_in_place(self) -> None:
        """旧 body 不同 → UPDATED"""
        old = f"{CODEGRAPH_SECTION_START}\n## OLD BODY\n{CODEGRAPH_SECTION_END}"
        self.path.write_text(old, encoding="utf-8")
        result = replace_or_append_marked_section(
            self.path,
            CODEGRAPH_INSTRUCTIONS_BLOCK,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, WriteResult.UPDATED)
        content = self.path.read_text()
        self.assertIn(CODEGRAPH_SECTION_START, content)
        self.assertIn(CODEGRAPH_SECTION_END, content)
        self.assertNotIn("OLD BODY", content)

    def test_append_when_other_content_exists(self) -> None:
        """现有非空但无标记 → 追加在末尾"""
        existing = "# Project Notes\n\nsome user content\n"
        self.path.write_text(existing, encoding="utf-8")
        result = replace_or_append_marked_section(
            self.path,
            CODEGRAPH_INSTRUCTIONS_BLOCK,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, WriteResult.APPENDED)
        content = self.path.read_text()
        self.assertTrue(content.startswith((existing.rstrip("\n"), existing)))
        self.assertIn(CODEGRAPH_INSTRUCTIONS_BLOCK, content)
        self.assertIn("# Project Notes", content)

    def test_remove(self) -> None:
        """删除标记区间，若文件空则删除文件。"""
        content_with = "# Before\n" + CODEGRAPH_INSTRUCTIONS_BLOCK + "\n# After"
        self.path.write_text(content_with, encoding="utf-8")
        result = remove_marked_section(
            self.path,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, "removed")
        content = self.path.read_text()
        self.assertNotIn(CODEGRAPH_SECTION_START, content)
        self.assertIn("# Before", content)
        self.assertIn("# After", content)

    def test_remove_when_empty_after(self) -> None:
        """只剩标记区间 → 删除文件。"""
        self.path.write_text(CODEGRAPH_INSTRUCTIONS_BLOCK, encoding="utf-8")
        result = remove_marked_section(
            self.path,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, "removed")
        self.assertFalse(self.path.exists())

    def test_remove_absent(self) -> None:
        """无标记 → absent（不写盘）"""
        self.path.write_text("# Other content\n", encoding="utf-8")
        result = remove_marked_section(
            self.path,
            CODEGRAPH_SECTION_START,
            CODEGRAPH_SECTION_END,
        )
        self.assertEqual(result, "absent")
        self.assertEqual(self.path.read_text(), "# Other content\n")


class TestAtomicWrite(unittest.TestCase):
    def test_writes_creates_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "deep" / "nested" / "f.md"
            atomic_write_file_sync(nested, "hello")
            self.assertTrue(nested.exists())
            self.assertEqual(nested.read_text(), "hello")


class TestHostTargets(unittest.TestCase):
    def test_claude_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".claude").mkdir()
            (cwd / ".claude" / "CLAUDE.md").write_text("# claude\n")
            self.assertEqual(
                ht.resolve_instructions_path(cwd),
                cwd / ".claude" / "CLAUDE.md",
            )

    def test_agents_when_no_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "AGENTS.md").write_text("# agents\n")
            self.assertEqual(ht.resolve_instructions_path(cwd), cwd / "AGENTS.md")

    def test_agents_when_neither_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            # 不创建任何文件 → 仍返回 AGENTS.md 路径（由调用者决定是否创建）
            self.assertEqual(ht.resolve_instructions_path(cwd), cwd / "AGENTS.md")

    def test_claude_preferred_over_agents(self) -> None:
        """两者都存在时,优先 .claude/CLAUDE.md."""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / ".claude").mkdir()
            (cwd / ".claude" / "CLAUDE.md").write_text("# claude\n")
            (cwd / "AGENTS.md").write_text("# agents\n")
            self.assertEqual(
                ht.resolve_instructions_path(cwd),
                cwd / ".claude" / "CLAUDE.md",
            )

    def test_is_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            self.assertFalse(ht.is_indexed(cwd))
            (cwd / ".codegraph").mkdir()
            self.assertTrue(ht.is_indexed(cwd))
            # 普通文件不算
            (cwd / ".codegraph").rmdir()
            (cwd / ".codegraph").write_text("not a dir")
            self.assertFalse(ht.is_indexed(cwd))


if __name__ == "__main__":
    unittest.main()
