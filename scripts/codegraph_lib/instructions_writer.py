"""标记区间写入/移除工具.

逻辑复刻自 codegraph 上游 src/installer/targets/shared.ts 的
replaceOrAppendMarkedSection / removeMarkedSection。本插件不修改上游
行为，只是把 TS 实现翻译成 Python stdlib。

写盘走 atomic_write_file_sync（临时文件 + rename），避免半写状态。
"""
from __future__ import annotations

import contextlib
import os
from enum import Enum
from pathlib import Path
from typing import Literal


class WriteResult(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    APPENDED = "appended"
    UNCHANGED = "unchanged"


def atomic_write_file_sync(path: Path, content: str) -> None:
    """原子写入。临时文件 + os.replace。"""
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        with contextlib.suppress(OSError):
            tmp.unlink()
        raise


def replace_or_append_marked_section(
    file_path: Path,
    body: str,
    start_marker: str,
    end_marker: str,
) -> WriteResult:
    """读取 file_path,定位 <start_marker>...<end_marker> 区间:

    - 区间不存在 → 'created'（新建文件，仅 body）或 'appended'（追加到现有内容后）
    - 区间存在且 byte-equal body → 'unchanged'（不写盘）
    - 区间存在但不等 → 'updated'（就地替换）

    body 必须以 start_marker 开头、end_marker 结尾，否则抛 ValueError——
    裸 body 会让下次运行找不到区间而重复追加。
    """
    if not (body.startswith(start_marker) and body.endswith(end_marker)):
        raise ValueError("body 必须以 start_marker 开头、end_marker 结尾")
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8")
    else:
        existing = ""

    start_idx = existing.find(start_marker)
    end_idx = existing.find(end_marker, start_idx + len(start_marker)) if start_idx != -1 else -1

    if start_idx == -1 or end_idx == -1:
        if existing.strip() == "":
            atomic_write_file_sync(file_path, body)
            return WriteResult.CREATED
        sep = "" if existing.endswith("\n") else "\n"
        atomic_write_file_sync(file_path, existing + sep + "\n" + body)
        return WriteResult.APPENDED

    # 区间完整
    inside_start = start_idx + len(start_marker)
    inside = existing[inside_start:end_idx]
    # body 已经包含 marker，复用 'inside' 与 body 的去 marker 比较
    expected_inside = body[len(start_marker): -len(end_marker)]
    if inside == expected_inside:
        return WriteResult.UNCHANGED

    new_content = existing[:start_idx] + body + existing[end_idx + len(end_marker):]
    atomic_write_file_sync(file_path, new_content)
    return WriteResult.UPDATED


def remove_marked_section(
    file_path: Path,
    start_marker: str,
    end_marker: str,
) -> Literal["removed", "absent"]:
    """读取 file_path,移除 <start_marker>...<end_marker> 区间。

    - 区间不存在 → 'absent'
    - 区间存在 → 'removed'。区间前后用单个 '\\n' 拼接;
      若移除后整个文件为空 → 删除文件。
    """
    if not file_path.exists():
        return "absent"
    existing = file_path.read_text(encoding="utf-8")
    start_idx = existing.find(start_marker)
    end_idx = existing.find(end_marker, start_idx + len(start_marker)) if start_idx != -1 else -1
    if start_idx == -1 or end_idx == -1:
        return "absent"

    before = existing[:start_idx]
    after = existing[end_idx + len(end_marker):]
    sep = "\n"
    if not before or before.endswith("\n"):
        sep = ""
    if after and not after.startswith("\n") and sep == "":
        sep = "\n"
    merged = before + sep + after
    if not merged.strip():
        file_path.unlink()
    else:
        atomic_write_file_sync(file_path, merged)
    return "removed"
