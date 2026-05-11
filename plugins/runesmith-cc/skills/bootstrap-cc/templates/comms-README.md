# Comms — file-based exchange between Cowork and Claude Code

This folder is the local channel between Cowork (planning) and Claude Code
(execution). Cowork writes here when it needs CC to do something. CC writes
here when it has questions, blockers, or needs the user.

## Folder layout

```
comms/
├── open/                       active messages (gitignored — ephemeral)
└── archive/<YYYY-MM>/<slug>/   resolved exchanges (committed — audit trail)
```

## Message format

Each file is markdown with YAML frontmatter:

```markdown
---
id: <unique id>
from: cowork | cc | user
to:   cowork | cc | user
type: session-init | task | answer | ambiguity | blocker | user-action | confirmation | ticket-transition | handshake
parent: <id of comm being answered, if any>
ticket: <Jira KEY>     # only when atlassian is enabled
plan: <slug>            # when relevant
status: open | resolved
created: <ISO>
resolved: <ISO>         # when status flips
---

# <human-readable title>

## Body
...

## Acceptance
What's needed before sender can move forward (sender-authored).
```

## Lifecycle

1. Sender writes a new file in `open/`. Filename: `<ISO>-<slug>.md`.
2. Receiver reads on next session start or skill invocation.
3. Receiver acts — may write a reply (new file, `parent: <original-id>`).
4. When the exchange is complete, both files move to
   `archive/<YYYY-MM>/<slug>/`.

## Rules

- The user is reached only through Cowork. CC never asks the user directly.
- Comms is local accelerator only — durable records of work live in plans
  (`../plans/active/<slug>/`) or in Jira tickets when atlassian is enabled.
- `open/` is gitignored; `archive/` is committed. Don't `git add open/`.

## Skills

Cowork side:
- `/atlassian:check-comms` — manual triage of open comms
- All planning skills run a check-on-entry of `open/`

CC side (deployed by `/atlassian:enable`):
- `sprint-pull`, `ticket-document`, `blocker-write`, `ticket-done` —
  read sprint, document on tickets, write blocker comms, request transitions

<!--
  Deployed from RuneSmith marketplace.
  Copyright 2026 Runemark Labs. Licensed under Apache-2.0.
  Source: https://github.com/runemarklabs/runesmith
-->
