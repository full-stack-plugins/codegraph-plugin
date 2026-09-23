"""codegraph-plugin 内部库.

仅被本插件的 hook 脚本和测试调用。不暴露给宿主。
"""
from .host_targets import is_indexed, resolve_instructions_path
from .instructions_writer import (
    WriteResult,
    atomic_write_file_sync,
    remove_marked_section,
    replace_or_append_marked_section,
)
from .prompt import (
    CODEGRAPH_INSTRUCTIONS_BLOCK,
    CODEGRAPH_SECTION_END,
    CODEGRAPH_SECTION_START,
)

__all__ = [
    "CODEGRAPH_INSTRUCTIONS_BLOCK",
    "CODEGRAPH_SECTION_END",
    "CODEGRAPH_SECTION_START",
    "WriteResult",
    "atomic_write_file_sync",
    "is_indexed",
    "remove_marked_section",
    "replace_or_append_marked_section",
    "resolve_instructions_path",
]
