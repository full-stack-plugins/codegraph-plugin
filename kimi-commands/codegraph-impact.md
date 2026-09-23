---
description: Find what would be affected by changing a symbol
argument-hint: "<symbol> [path]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Find impact of `$ARGUMENTS` (last token is the path, default `.`). Pass a symbol name; disambiguate same-named symbols with `--file <file>`. Run `codegraph impact <symbol>` (default depth=2) and report affected symbols. Optional `--depth N` for transitive depth.

MCP alternative: `codegraph_impact(symbol, depth)`.

Boundaries: read-only. Always run this before changing core abstractions, but zero impact ≠ safe — also check dynamic dispatch, runtime polymorphism, configuration-driven branches.