# Plugin Install Paths

Different runtimes load plugins from different locations. Skills that scan or write plugin files must check both.

## Cowork (desktop app)

Windows host path:
```
~/AppData/Roaming/Claude/local-agent-mode-sessions/<session>/<workspace>/rpm/plugin_*/
```

Inside a Cowork shell session this is mounted at:
```
/sessions/<session>/mnt/.remote-plugins/plugin_*/
```

Read-only from inside the session. Per-session, per-workspace. Manual install via drag-drop of `.plugin` zip into the Cowork sidebar - Cowork writes to the host `rpm/` directory, then the session sees it on next restart.

## Claude Code (CLI)

```
~/.claude/plugins/<plugin-name>/
```

Or, for marketplace-managed:
```
~/.claude/plugins/marketplaces/<owner>/<repo>/plugins/<plugin-name>/
```

Marketplace install:
```
/plugin marketplace add <owner>/<repo>
/plugin install <plugin-name>@<marketplace-name>
```

## Claude Teams (managed)

Admin distributes via marketplace URL. Users see plugins in `/plugin` UI without manual file handling. Same on-disk path as Claude Code: `~/.claude/plugins/marketplaces/...`.

## Detection order for skills

1. `CLAUDE_PLUGINS_DIR` env var (override)
2. `~/.claude/plugins/` if exists (Claude Code / Teams)
3. Walk up from cwd for `rpm/plugin_*` (Cowork session)
4. Fall back: empty list, suggest `/core:install`

## Manual install (`.plugin` files)

`.plugin` is a zip of the plugin folder (the directory containing `.claude-plugin/plugin.json`). Inside the zip, the plugin folder is the top-level entry.

```
core.plugin
└── core/
    ├── .claude-plugin/plugin.json
    ├── skills/...
    └── lib/...
```

Build with:
```bash
cd plugins/core && zip -r ../../dist/core.plugin .claude-plugin skills lib
```

## Marketplace install (recommended)

Add `.claude-plugin/marketplace.json` at repo root. Users run:
```
/plugin marketplace add <git-url-or-owner/repo>
/plugin install core@bootstrap
/plugin install atlassian@bootstrap
/plugin install aiops@bootstrap
/plugin install devtools@bootstrap
```
