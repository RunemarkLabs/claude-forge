# runesmith-sprint

Atlassian sprint workflow + Cowork-CC interconnect.

Part of the [RuneSmith marketplace](https://github.com/runemarklabs/runesmith).

## Skills

- **`/runesmith-sprint:enable`** — Wire Atlassian into a project (CLAUDE.md updates + CC-side skill deploy).
- **`/runesmith-sprint:disable`** — Strip Atlassian wiring from a project.
- **`/runesmith-sprint:start-sprint`** — Hand the active sprint to Claude Code via session-init comm.
- **`/runesmith-sprint:sprint-status`** — Sprint board view + comms summary; auto-fires handshake on sprint change.
- **`/runesmith-sprint:check-comms`** — Triage open comms in {PROJECT}.cc/comms/open/ and process replies.
- **`/runesmith-sprint:plan-to-tickets`** — Convert plans/active/ plan.md files into Jira tickets organized by sprint.

## Install

Via marketplace (Claude Code / Teams):

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-sprint@runesmith
```

Via manual `.plugin` file (Cowork): drag the file from `dist-v2/` into the Cowork plugin sidebar.

## Configure

Run `/runesmith-core:setup` first to populate `.credentials` at the workspace root.

## License

Apache-2.0. See `LICENSE`.
