# 官方 CodeGraph 提示词块（verbatim）

下述文本必须与 codegraph 上游 `src/installer/instructions-template.ts:42-51` 的 `CODEGRAPH_INSTRUCTIONS_BLOCK` 完全一致。

最后一次同步：codegraph v1.5.0 (2026-07-21)。

---

```text
<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
```

---

## 漂移检查

每次 codegraph 升级（CHANGELOG 涉及 `instructions-template.ts`）后：

1. 对照上游 `src/installer/instructions-template.ts` 比对 `scripts/codegraph_lib/prompt.py`
2. 若文本漂移：更新 `prompt.py`，bump patch 版本
3. 在 `CHANGELOG.md`（如有）记录「prompt 文本与 codegraph vX.Y.Z 同步」
4. 重新跑单元测试 + 烟测钩子