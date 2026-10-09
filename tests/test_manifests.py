"""Manifest 一致性 + 版本号一致性测试."""
from __future__ import annotations

import json
import re
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

    def test_description_not_gated_on_index_presence(self) -> None:
        """AGENTS.md 纪律：技能 description 不得以「已有 .codegraph/」为激活门槛。

        若门槛写回「仓库根有 .codegraph/ 目录时使用」，未索引仓库里技能根本不
        触发，其「未索引则提示用户」分支永远执行不到——插件的发现性目的被架空。
        """
        skill_md = PLUGIN_ROOT / "skills" / "codegraph-helper" / "SKILL.md"
        front = skill_md.read_text(encoding="utf-8").split("---", 2)[1]
        gated = re.search(r"\.codegraph/`?\s*(?:目录)?(?:存在)?时使用", front)
        self.assertIsNone(
            gated,
            "SKILL.md description 以 .codegraph/ 存在为激活门槛，"
            "未索引仓库无法触发「提示初始化」分支（见 AGENTS.md 发现性纪律）",
        )
        # 反向断言：必须显式声明「无论是否已索引」且包含检查动作
        self.assertRegex(front, r"无论|不论|regardless")
        self.assertRegex(front, r"codegraph init")


class TestReadmeParity(unittest.TestCase):
    """轻量级 README.md ↔ README.zh-CN.md 标题结构测试."""

    def test_both_exist(self) -> None:
        self.assertTrue((PLUGIN_ROOT / "README.md").exists())
        self.assertTrue((PLUGIN_ROOT / "README.zh-CN.md").exists())

    def test_heading_structure_matches(self) -> None:
        """双语 README 的标题层级序列必须一致（文本可译，结构不可漂移）."""
        import re

        def levels(text: str) -> list:
            return [m.group(1) for m in re.finditer(r"^(#+) ", text, re.MULTILINE)]

        en = levels((PLUGIN_ROOT / "README.md").read_text())
        zh = levels((PLUGIN_ROOT / "README.zh-CN.md").read_text())
        self.assertEqual(en, zh, "README 双语标题层级序列不一致")


if __name__ == "__main__":
    unittest.main()
