#!/usr/bin/env python3
"""SessionStart 钩子: 检测 cwd 是否有 .codegraph/, 有则把官方提示词
写入 host instructions 文件 + 通过 additionalContext 注入会话。

失败语义: 任何异常都 fail-open,不阻断宿主启动。

设计文档: AGENTS.md（说明 verbatim 来源、文件策略、fail-open 边界）
库模块: scripts.codegraph_lib
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from codegraph_lib import (  # noqa: E402
    CODEGRAPH_INSTRUCTIONS_BLOCK,
    CODEGRAPH_SECTION_END,
    CODEGRAPH_SECTION_START,
    is_indexed,
    replace_or_append_marked_section,
    resolve_instructions_path,
)


def read_payload() -> dict:
    """从 stdin 读 SessionStart JSON payload.

    TTY/无 payload → 返回空 dict,后续 cwd 走 os.getcwd().
    """
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}


def main() -> int:
    try:
        payload = read_payload()
        cwd_str = payload.get("cwd") if isinstance(payload, dict) else None
        cwd = Path(cwd_str) if cwd_str else Path(os.getcwd())

        # 1. 仅在已索引项目中注入 → 静默退出条件
        if not is_indexed(cwd):
            return 0

        # 2. 写入 host instructions 文件(标记区间替换, 字节级幂等)
        instructions_path = resolve_instructions_path(cwd)
        try:
            replace_or_append_marked_section(
                instructions_path,
                CODEGRAPH_INSTRUCTIONS_BLOCK,
                CODEGRAPH_SECTION_START,
                CODEGRAPH_SECTION_END,
            )
        except Exception as exc:  # noqa: BLE001 — 写盘失败不影响 additionalContext 注入
            print(f"[codegraph-plugin] 写 {instructions_path} 失败: {exc!r}", file=sys.stderr)

        # 3. 通过 additionalContext 把同一段文本注入会话
        print(json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": CODEGRAPH_INSTRUCTIONS_BLOCK,
                },
            },
            ensure_ascii=False,
        ))

        return 0
    except Exception as exc:  # noqa: BLE001 — 终极 fail-open
        print(f"[codegraph-plugin] 内部错误已忽略(fail-open): {exc!r}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    # 任何未捕获异常都吞掉
    with contextlib.suppress(Exception):
        sys.exit(main())
    sys.exit(0)
