"""官方 CodeGraph 提示词常量.

verbatim 同步自 codegraph 上游 src/installer/instructions-template.ts。

任何上游变更（CHANGELOG 涉及 instructions-template.ts）必须:
1. 复制新文本到本文件
2. bump patch 版本
3. 核对 skills/codegraph-helper/references/instructions-block.md

上版本最后核对: codegraph v1.5.0 (2026-07-21)。
"""
from __future__ import annotations

# 与上游 codegraph 一致的标记常量。installer 用这两个标记做区间替换。
CODEGRAPH_SECTION_START: str = "<!-- CODEGRAPH_START -->"
CODEGRAPH_SECTION_END: str = "<!-- CODEGRAPH_END -->"


# 完整提示词块（含两个标记），与 upstream CODEGRAPH_INSTRUCTIONS_BLOCK
# 逐字节相同。本插件只复制文本，不改动。
CODEGRAPH_INSTRUCTIONS_BLOCK: str = (
    f"{CODEGRAPH_SECTION_START}\n"
    "## CodeGraph\n"
    "\n"
    "In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:\n"
    "\n"
    "- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.\n"
    "- **Shell** (always works): `codegraph explore \"<symbol names or question>\"` prints the same output.\n"
    "\n"
    "If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.\n"
    f"{CODEGRAPH_SECTION_END}"
)
