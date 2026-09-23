---
description: Upgrade codegraph CLI to the latest release
argument-hint: "[version]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Run `codegraph upgrade <version>` (default: latest). After upgrade, if upstream's `instructions-template.ts` has changed, the plugin's `scripts/codegraph_lib/prompt.py` must be re-synced manually and a patch bump applied (see AGENTS.md discipline).

Boundaries: does not modify the plugin itself — only the upstream `codegraph` CLI.