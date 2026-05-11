# runesmith-jira

Jira tickets and project basics with current Cloud REST endpoints.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-jira:ticket`** — Create Task/Story/Bug/Epic tickets with proper ADF body.
- **`/runesmith-jira:bug-report`** — Document a bug in Confluence and create a linked Jira Bug ticket.
- **`/runesmith-jira:project-status`** — Read-only sprint board view (sprint-aware when atlassian-enabled).
- **`/runesmith-jira:new-project`** — Scaffold a Jira project with required fields (admin perms required).

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-jira@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
