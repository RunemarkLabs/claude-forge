# Comms Protocol

File-based message exchange between Cowork and Claude Code, plus the user as a routed audience.

Comms is a **local accelerator only** - fast, offline, structured. Persistent records of work (plans, decisions, ticket history) live elsewhere: in `plans/active/<slug>/` markdown for plans, in Jira tickets + tags for atlassian-enabled work. Comms is not the durable record.

## Why files

- Both Cowork and CC can read/write disk; no broker required.
- Survives session restarts on either side.
- Greppable, diffable, auditable.
- Same protocol works in base config and atlassian config - the only difference is whether messages reference Jira tickets.

## Folder layout

```
{PROJECT}.cc/comms/
├── open/                        active messages awaiting response or action
│   ├── <ISO>-<slug>.md
│   └── <ISO>-<slug>.md
├── archive/<YYYY-MM>/           resolved exchanges, paired by slug
│   └── <slug>/
│       ├── <ISO>-<slug>.md      original message
│       └── <ISO>-<slug>.md      reply
├── README.md                    summary of the protocol - readable by CC via @comms/README.md
└── .gitkeep                     keep dirs in git even when empty
```

`open/` is gitignored (ephemeral, per-session). `archive/` is committed (audit trail).

## File format

Every comms file is markdown with YAML frontmatter:

```markdown
---
id: <uuid-or-short-id>           # unique within this project
from: cowork | cc | user
to:   cowork | cc | user
type: session-init | task | answer | ambiguity | blocker | user-action | confirmation | ticket-transition | handshake
parent: <id>                     # for replies - links to the comm being answered
ticket: <KEY>                    # Jira key (atlassian-enabled only; omit otherwise)
plan: <slug>                     # plan slug (when relevant)
status: open | resolved
created: <ISO timestamp>
resolved: <ISO timestamp>        # populated when status flips to resolved
---

# <human-readable title>

## Body
What needs to be communicated.

## Acceptance
What's needed before the sender can move forward (sender-authored only).
```

## Types

| Type | From → To | Purpose |
|---|---|---|
| `session-init` | cowork → cc | Cowork tells CC which sprint/plan to work and the rules of engagement |
| `handshake` | cc → user | CC acks session-init, sets expectations, asks user to check in via Cowork |
| `task` | cowork → cc | Cowork hands CC a discrete task (base config; references a plan slug) |
| `answer` | any → any | Reply to a previous comm, identified by `parent` |
| `ambiguity` | cc → cowork | CC needs clarification; can't proceed without an answer |
| `blocker` | cc → cowork or cc → user | CC is blocked; describes blocker; routes to whoever can unblock |
| `user-action` | cc → user | CC needs the user to do something only the user can do (create repo, provide a configuration value, click in a UI) |
| `confirmation` | any → any | Lightweight acknowledgement, no body needed |
| `ticket-transition` | cc → cowork | (atlassian only) CC asks Cowork to transition a Jira ticket via MCP |

## Lifecycle

1. **Author writes** a new file in `comms/open/`. Filename: `<ISO>-<slug>.md` where `<slug>` is short kebab-case for grep-friendliness.
2. **Receiver reads** on their next session-start or skill invocation.
3. **Receiver acts.** May write a reply (new file, `parent: <original-id>`, status: open). May resolve the request and flip the original to `status: resolved`.
4. **When the exchange is complete** (both sides resolved), the originator (or whichever side notices last) moves the entire pair to `comms/archive/<YYYY-MM>/<slug>/`.
5. **Audit:** the archive holds the durable record of the exchange. Plans / Jira tickets hold the durable record of the work itself.

## Filename conventions

```
2026-04-27T18-15-22Z-blocker-config-value-needed.md
2026-04-27T18-30-01Z-answer-config-value-needed.md
```

Same `<slug>` ties a question to its answer. Different `<ISO>` orders them. Keep slugs short.

## Check-on-entry pattern

Every Cowork-side planning skill calls a comms-check helper at the start of its workflow. See `lib/comms-check.md`. Check applies to both base config and atlassian config - comms exists in both.

## Atlassian-enabled additions

When the workspace is atlassian-enabled, comms files MAY include:

- `ticket: <KEY>` in frontmatter - the Jira ticket the comm is about
- `type: ticket-transition` - CC asks Cowork to mutate a ticket (CC has read-only Jira access; mutations go through Cowork via MCP)

The protocol is identical otherwise.

## What comms is NOT

- **Not the plan.** Plans live in `plans/active/<slug>/plan.md`.
- **Not the Jira record.** Tags + comments on tickets are the persistent atlassian record.
- **Not for user broadcast.** User-bound messages go through Cowork's UI surfaces, not comms files.
- **Not a queue or pub/sub.** It's a directory of typed messages. Order is by ISO timestamp, not by status.

## Skills that read/write comms

- `core:plan` - checks comms on entry; may write tasks for CC in base config
- `atlassian:check-comms` - manual triage; lists `open/` items grouped by `to:`, surfaces `to: user` to the user, drafts replies, archives resolved pairs
- `atlassian:start-sprint` / `sprint-status` - write `session-init` comms when sprint changes
- `atlassian:plan-to-tickets` - checks comms on entry; produces tickets, may write task comms
- All atlassian publish skills - check comms on entry before publishing
- CC-side skill templates (`sprint-pull`, `ticket-document`, `blocker-write`, `ticket-done`) - write `from: cc` comms; read replies addressed back
