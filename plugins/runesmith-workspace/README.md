# runesmith-workspace

Workspace structure manager: _INBOX, plans/active, plans/archive, snapshots.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-workspace:reallocate`** — Migrate or initialize the workspace folder structure with auto-snapshot.
- **`/runesmith-workspace:inbox`** — Classify files in _INBOX/ and route them to plans, drafts, tickets, or notes.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-workspace@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
