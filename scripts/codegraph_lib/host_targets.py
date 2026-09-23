"""宿主 instructions 文件路径解析.

策略（与 `AGENTS.md` 纪律一致）:
1. `<cwd>/.claude/CLAUDE.md` 存在 → 返回它（与 codegraph 自家 installer 一致）
2. 否则 → `<cwd>/AGENTS.md`（OpenSpec / 多代理通用约定）

不自动创建 `<cwd>/.claude/` 目录——避免插件越权定义用户的 .claude/ 布局。
若两者都不存在，由调用者决定是否创建 AGENTS.md。
"""
from __future__ import annotations

from pathlib import Path


def resolve_instructions_path(cwd: Path) -> Path:
    """解析要写入的 instructions 文件路径。

    Args:
        cwd: 当前工作目录（git 仓库根或任意目录）

    Returns:
        优先 `<cwd>/.claude/CLAUDE.md`，否则 `<cwd>/AGENTS.md`
    """
    claude = cwd / ".claude" / "CLAUDE.md"
    if claude.exists():
        return claude
    return cwd / "AGENTS.md"


def is_indexed(cwd: Path) -> bool:
    """判断 cwd 是否已被 codegraph 索引。"""
    return (cwd / ".codegraph").is_dir()
