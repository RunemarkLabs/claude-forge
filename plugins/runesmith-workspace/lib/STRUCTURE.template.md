# Workspace Structure

This file is generated at workspace root by `/runesmith-workspace:reallocate` from the template in `runesmith-workspace/lib/STRUCTURE.template.md`. It documents the canonical workspace layout for any project bootstrapped with this marketplace.

For the destination map and lifecycle rules, see `runesmith-workspace/lib/folder-conventions.md` (the source of truth — this file is the user-facing summary).

## Layout

```
<workspace-root>/
├── _INBOX/                              drop zone — inbox skill empties it
│
├── plans/
│   ├── active/<slug>/                   active plans (claude-readable)
│   │   ├── plan.md                      required
│   │   ├── decisions.md                 optional, append-only
│   │   ├── refs/                        supporting docs
│   │   └── tickets/<KEY>.json           pre-push Jira drafts
│   └── archive/<YYYY-MM>/<slug>/        completed plans (carries refs+tickets)
│
├── notes/                               session notes, handoffs
│                                        flat. <YYYY-MM-DD>-<slug>.md
│
├── drafts/                              pre-publish Confluence content
│   ├── features/<slug>/                 feature pages
│   ├── project-docs/<slug>/             project docs
│   └── bugs/<slug>/                     bug docs
│
├── research/<topic>/                    standalone analysis (no plan yet)
│
├── source-docs/<topic>/                 external uploads being processed
│
├── archive/
│   ├── _pre-migration/<ISO>/            reallocate snapshots
│   ├── _pre-cc-bootstrap/<ISO>/         bootstrap-cc snapshots
│   ├── _pre-atlassian-enable/<ISO>/     atlassian:enable snapshots
│   ├── superseded/<YYYY-MM>/            consumed content, dead docs
│   └── tickets-pushed/<YYYY-MM>/        ticket JSON after Jira push
│
├── {PROJECT}.cc/                        Claude Code monorepo head
│   ├── CLAUDE.md                        monorepo constitution
│   ├── README.md
│   ├── .claude-code-workspace           marker JSON
│   ├── .credentials                     read-only Jira PAT (atlassian-enabled)
│   ├── .claude/
│   │   ├── settings.json
│   │   ├── settings.local.json          gitignored
│   │   ├── skills/                      project-local skills
│   │   ├── commands/, agents/, hooks/
│   ├── comms/
│   │   ├── open/                        gitignored
│   │   └── archive/<YYYY-MM>/           committed
│   ├── .gitignore
│   ├── .gitattributes
│   └── <repo>/                          actual code repos
│       └── CLAUDE.md
│
├── CLAUDE.md                            workspace constitution
├── STRUCTURE.md                         this file (generated)
├── .credentials                         gitignored
├── .credentials.example
├── .gitignore
├── .atlassian-enabled                   (only when atlassian:enable has run)
│
└── (marketplace dev workspace only:)
    ├── plugins/                         marketplace source
    ├── dist/                            packaged .plugin files
    ├── scripts/                         marketplace tooling
    ├── .claude-plugin/                  marketplace.json
    └── .github/                         CI
```

## Key conventions

- **Root stays clean.** Only the entries above. Anything else at root = inbox-item → run `/runesmith-workspace:inbox`.
- **`_INBOX/`** — permanent drop zone, transient contents. Inbox skill classifies and routes; reallocate never places files here.
- **`plans/active/<slug>/`** — every plan is a folder. `plan.md` is the entry point. See `runesmith-workspace/lib/plan-format.md`.
- **Tickets** live under their plan in `plans/active/<slug>/tickets/<KEY>.json` pre-push. After push, they move to `archive/tickets-pushed/<YYYY-MM>/`.
- **Research** lives at `research/<topic>/` when standalone; migrates to `plans/active/<slug>/refs/` once a plan adopts it.
- **Source-docs** at `source-docs/<topic>/` while content is being consumed; raw files archive to `archive/superseded/<YYYY-MM>/` after.
- **`comms/`** — Cowork ↔ Claude Code file-based exchange. `open/` is ephemeral; `archive/` is the audit trail. See `runesmith-workspace/lib/comms-protocol.md`.
- **`{PROJECT}.cc/`** — folder name matches the workspace root folder name with `.cc` suffix. Distinguishes this CC workspace from others.
- **Atlassian config** — toggled by `/runesmith-sprint:enable` and `/runesmith-sprint:disable`. Marker file `.atlassian-enabled` and CC marker JSON.

## Skills that maintain this structure

- `/runesmith-workspace:reallocate` — migrates and normalizes the workspace; refreshes this file
- `/runesmith-workspace:inbox` — processes `_INBOX/`
- `/runesmith-core:plan` — writes plans into `plans/active/<slug>/`
- `/runesmith-cc:bootstrap-cc` — creates `{PROJECT}.cc/`
- `/runesmith-sprint:enable` — wires Atlassian into the project
- `/runesmith-sprint:plan-to-tickets` — writes ticket drafts under their plan
- `/runesmith-sprint:check-comms` — triages `{PROJECT}.cc/comms/open/`
