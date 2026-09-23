"""20 个 slash 命令的 JSON + Markdown 解析 + 一致性测试.

每个 .json 必须:
- 可解析
- 含 name / description / prompt 三个字段
- name 与文件名一致

每个 .md 必须:
- 含 YAML frontmatter
- frontmatter 含 description
- 不允许使用相对路径引用文件

每个 .json 和同名 .md 的 description 必须各自存在且非空（跨语言语义等价机器不可判，靠人工核对）.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
COMMANDS = PLUGIN_ROOT / "commands"
KIMI_COMMANDS = PLUGIN_ROOT / "kimi-commands"


class TestCommandFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.jsons = sorted(COMMANDS.glob("*.json"))
        self.mds = sorted(KIMI_COMMANDS.glob("*.md"))

    def test_count(self) -> None:
        self.assertEqual(len(self.jsons), 20, f"expected 20 .json, got {len(self.jsons)}")
        self.assertEqual(len(self.mds), 20, f"expected 20 .md, got {len(self.mds)}")

    def test_json_files(self) -> None:
        for jf in self.jsons:
            with self.subTest(file=jf.name):
                data = json.loads(jf.read_text(encoding="utf-8"))
                self.assertIn("name", data)
                self.assertIn("description", data)
                self.assertIn("prompt", data)
                # name 与文件名（无 .json）一致
                self.assertEqual(data["name"], jf.stem)
                # description 非空
                self.assertGreater(len(data["description"]), 4)

    def test_md_files_have_frontmatter(self) -> None:
        for mf in self.mds:
            with self.subTest(file=mf.name):
                content = mf.read_text(encoding="utf-8")
                # 必须以 --- 开始（YAML frontmatter）
                self.assertTrue(content.startswith("---\n"), f"{mf.name} 缺 YAML frontmatter")
                # 含 description 字段
                self.assertIn("description:", content, f"{mf.name} 缺 description 字段")

    def test_names_match(self) -> None:
        json_names = {jf.stem for jf in self.jsons}
        md_names = {mf.stem for mf in self.mds}
        self.assertEqual(json_names, md_names, "JSON 与 MD 命令名集合必须完全相同")

    def test_descriptions_present_in_both(self) -> None:
        """每对同名命令: .json description 与 .md frontmatter description 都非空."""
        desc_re = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
        for jf in self.jsons:
            with self.subTest(command=jf.stem):
                data = json.loads(jf.read_text(encoding="utf-8"))
                self.assertGreater(len(data.get("description", "")), 4)
                mf = KIMI_COMMANDS / f"{jf.stem}.md"
                self.assertTrue(mf.exists(), f"{mf.name} 缺失")
                parts = mf.read_text(encoding="utf-8").split("---", 2)
                self.assertGreaterEqual(len(parts), 3, f"{mf.name} 缺 YAML frontmatter")
                m = desc_re.search(parts[1])
                self.assertIsNotNone(m, f"{mf.name} frontmatter 缺 description")
                self.assertGreater(len(m.group(1).strip().strip("\"' ")), 4)


class TestNoExternalVendoredCrossLinks(unittest.TestCase):
    """AGENTS.md 纪律: 不跨文件引用兄弟 skill 的资源。"""

    def test_no_dotdot_relative_links(self) -> None:
        link_re = re.compile(r"\[([^\]]+)\]\((\.\.?/[^)]+)\)")
        offenders = []
        # commands/（Kimi .json）与 kimi-commands/（Codex .md）都必须覆盖
        targets = (
            list(COMMANDS.glob("*.md"))
            + list(COMMANDS.glob("*.json"))
            + list(KIMI_COMMANDS.glob("*.md"))
            + list(KIMI_COMMANDS.glob("*.json"))
        )
        for md in sorted(targets):
            text = md.read_text(encoding="utf-8")
            for m in link_re.finditer(text):
                offenders.append((md.name, m.group(1), m.group(2)))
        self.assertEqual(offenders, [], f"发现跨 skill 相对路径链接: {offenders}")


class TestLocalSkillManifests(unittest.TestCase):
    def test_plugin_local_skills_json(self) -> None:
        data = json.loads((PLUGIN_ROOT / "plugin-local-skills.json").read_text())
        self.assertEqual(data.get("version"), 1)
        self.assertEqual(data.get("dest"), "skills/")
        skills = data.get("skills", [])
        self.assertIn("codegraph-helper", skills)

    def test_skills_lock(self) -> None:
        data = json.loads((PLUGIN_ROOT / "skills.lock.json").read_text())
        self.assertEqual(data.get("version"), 1)
        # 本插件不 vendor 任何第三方技能
        self.assertEqual(data.get("sources", []), [])

    def test_skill_md_exists(self) -> None:
        skill = PLUGIN_ROOT / "skills" / "codegraph-helper" / "SKILL.md"
        self.assertTrue(skill.exists())
        text = skill.read_text(encoding="utf-8")
        # frontmatter 必填字段
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: codegraph-helper", text)
        self.assertIn("description:", text)


if __name__ == "__main__":
    unittest.main()
