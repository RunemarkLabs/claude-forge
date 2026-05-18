# runesmith-core

Foundation plugin: credentials, plugin install/sync, chat-first planning.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-core:plan`** - Discuss and converge on a plan in chat before any writes; saves to plans/active/<slug>/plan.md.
- **`/runesmith-core:install`** - Browse and install plugins from this marketplace and optional catalogs.
- **`/runesmith-core:sync`** - Pull latest plugin versions and refresh AIOPS templates from upstream.
- **`/runesmith-core:setup`** - Configure .credentials (Atlassian, GitHub, plugin sources) with health checks.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-core@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
