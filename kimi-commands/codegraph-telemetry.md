---
description: View or change codegraph telemetry
argument-hint: "[status|on|off]"
skills: codegraph-helper
---

Use the `codegraph-helper` skill for this request:

Run `codegraph telemetry <action>` where action defaults to `status`. Supports `status | on | off`. This plugin does NOT automatically change the user's telemetry preference.

Boundaries: read-only unless user explicitly invokes with `on` or `off`.