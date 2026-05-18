# runesmith-aiops

Populate an AI Operations Confluence space from six template pages.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-aiops:bootstrap-aiops`** - Substitute tokens and publish Quick Start / Full Integration / Architecture / Best Practices / FAQ / Reference.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-aiops@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
