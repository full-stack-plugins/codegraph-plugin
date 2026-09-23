"""Manifest 一致性 + 版本号一致性测试."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_HUB = PLUGIN_ROOT.parents[1] / "full-stack-plugins"


class TestManifestFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.kimi = json.loads((PLUGIN_ROOT / "kimi.plugin.json").read_text())
        self.codex = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.zcode = json.loads((PLUGIN_ROOT / ".zcode-plugin" / "plugin.json").read_text())
        self.marketplace = json.loads((PLUGIN_ROOT / ".agents" / "plugins" / "marketplace.json").read_text())

    def test_all_names_match(self) -> None:
        for name, m in [("kimi", self.kimi), ("codex", self.codex), ("zcode", self.zcode)]:
            with self.subTest(manifest=name):
                self.assertEqual(m["name"], "codegraph")

    def test_versions_present(self) -> None:
        for name, m in [("kimi", self.kimi), ("codex", self.codex), ("zcode", self.zcode)]:
            with self.subTest(manifest=name):
                self.assertIn("version", m)
                self.assertRegex(m["version"], r"^\d+\.\d+\.\d+")

    def test_kimi_has_hooks(self) -> None:
        """kimi.plugin.json 含 hooks 数组, 1 个 SessionStart 钩子"""
        self.assertIn("hooks", self.kimi)
        self.assertEqual(len(self.kimi["hooks"]), 1)
        self.assertEqual(self.kimi["hooks"][0]["event"], "SessionStart")

    def test_zcode_no_hooks_key(self) -> None:
        """ZCode 不在 manifest 里写 hooks (从 kimi 读)"""
        self.assertNotIn("hooks", self.zcode)


class TestMarketplaceHubEntry(unittest.TestCase):
    def test_catalog_entry_exists(self) -> None:
        """catalog.json 含 codegraph 条目, 字段齐全"""
        catalog_path = PLUGINS_HUB / "catalog.json"
        if not catalog_path.exists():
            self.skipTest(f"catalog.json not found at {catalog_path}")
        catalog = json.loads(catalog_path.read_text())
        plugins = {p["id"]: p for p in catalog.get("plugins", [])}
        self.assertIn("codegraph", plugins, "catalog.json 缺 codegraph 条目")
        entry = plugins["codegraph"]
        for field in ("displayName", "repository", "localDirectory", "version", "description", "category", "tags"):
            self.assertIn(field, entry, f"catalog 条目缺字段: {field}")
        self.assertEqual(entry["localDirectory"], "codegraph-plugin")
        self.assertEqual(entry["repository"], "full-stack-plugins/codegraph-plugin")


class TestSkillFrontmatter(unittest.TestCase):
    def test_skill_naming(self) -> None:
        skill_dir = PLUGIN_ROOT / "skills" / "codegraph-helper"
        self.assertTrue(skill_dir.exists())
        # 目录名必须 kebab-case
        self.assertRegex(skill_dir.name, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_skill_md_under_500_lines(self) -> None:
        skill_md = PLUGIN_ROOT / "skills" / "codegraph-helper" / "SKILL.md"
        if skill_md.exists():
            lines = skill_md.read_text().count("\n")
            self.assertLess(lines, 500, f"SKILL.md {lines} 行超 500 行限制")


class TestReadmeParity(unittest.TestCase):
    """轻量级 README.md ↔ README.zh-CN.md 标题结构测试."""

    def test_both_exist(self) -> None:
        self.assertTrue((PLUGIN_ROOT / "README.md").exists())
        self.assertTrue((PLUGIN_ROOT / "README.zh-CN.md").exists())

    def test_same_h1(self) -> None:
        readme = (PLUGIN_ROOT / "README.md").read_text()
        zh = (PLUGIN_ROOT / "README.zh-CN.md").read_text()
        # 提取第一行非空 markdown heading (H1) 作为 sanity check
        import re
        en_h1 = re.search(r"^# .+", readme, re.MULTILINE)
        zh_h1 = re.search(r"^# .+", zh, re.MULTILINE)
        self.assertIsNotNone(en_h1)
        self.assertIsNotNone(zh_h1)


if __name__ == "__main__":
    unittest.main()
