# runesmith-devtools

Developer helpers: help listing, plugin builder, tech-debt scan, skill updater.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-devtools:help`** - List installed plugins and their skills with natural-language triggers.
- **`/runesmith-devtools:plugin-builder`** - Scaffold a new Claude plugin.
- **`/runesmith-devtools:tech-debt`** - Scan workspace for stale or orphaned artifacts.
- **`/runesmith-devtools:skill-updater`** - Propagate convention changes across all skills.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-devtools@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
