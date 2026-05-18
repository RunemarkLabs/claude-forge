# runesmith-confluence

Confluence page authoring with storage XHTML conversion.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-confluence:feature-doc`** - Feature specification page.
- **`/runesmith-confluence:architecture-doc`** - Architecture decision record (ADR) or overview.
- **`/runesmith-confluence:project-overview`** - Project space landing page.
- **`/runesmith-confluence:decisions-log`** - Append-only decisions log page.
- **`/runesmith-confluence:known-issues`** - Known issues / tech debt tracker page.
- **`/runesmith-confluence:roadmap`** - Now / Next / Later roadmap page.
- **`/runesmith-confluence:session-log`** - Session outcomes (decisions, action items) page.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-confluence@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
