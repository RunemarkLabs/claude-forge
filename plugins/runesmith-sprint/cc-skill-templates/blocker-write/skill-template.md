---
name: blocker-write
description: "Declare a blocker on a Jira ticket — write a comm requesting unblock, tag the ticket cc-blocked. Use when CC is stuck and needs Cowork or the user to act before continuing. Runs in Claude Code."
---

# Blocker Write (CC-side)

Pair: a comms file + a ticket label. The comm carries the explanation; the label makes the blocker visible on the Jira board.

## References

- `@comms/README.md` — comms protocol
- `@lib/jira-tags.md`
- Sibling: `ticket-document` (similar capability tiering)

## Pre-Flight Checks

1. Marker says `atlassianEnabled: true`.
2. `.credentials` available.
3. Probe label-write capability (cached per session).

## Workflow

### 1. Gather inputs

- Ticket key
- Blocker type: `ambiguity` | `blocker` | `user-action`
- `to:` — `cowork` (most blockers) or `user` (user-only actions like API key, repo creation, paste a secret)
- Body — what's blocking, what would unblock
- Acceptance — what response would let CC resume

### 2. Write the comm

```
comms/open/<ISO>-blocker-{ticket-or-slug}.md
```

```yaml
---
id: <id>
from: cc
to: cowork | user
type: ambiguity | blocker | user-action
ticket: {KEY}
status: open
created: <ISO>
---

# Blocked on {KEY}

## Body
<what's blocking — concrete, technical>

## Acceptance
<what response would unblock>
```

### 3. Tag the ticket `cc-blocked`

If capability allows direct label write:
```
PUT {SITE_URL}/rest/api/3/issue/{KEY}
{ "update": { "labels": [{ "add": "cc-blocked" }] } }
```

If `to: user`, also add `needs-user`.

If capability is read-only, append to the same comm a request for Cowork to add the labels:

```yaml
also-add-labels: [cc-blocked]   # or [cc-blocked, needs-user]
```

`check-comms` reads this hint and adds labels via MCP.

### 4. Stop work on this ticket

CC must NOT continue work on a `cc-blocked` ticket. Pick a different available ticket from the sprint (via `sprint-pull`) or pause the session if none available.

### 5. Report (in CC chat)

```
Blocked on {KEY}: {one-line summary}
Wrote: <comm filename>
Label cc-blocked added: <direct | via comms>
Picking next available ticket from sprint…
```

## Guard Rails

- [ ] Comm file written with full required frontmatter
- [ ] `to:` audience matches the blocker type (user-action → `to: user`)
- [ ] `cc-blocked` label requested (direct or via comms)
- [ ] CC stops work on this ticket immediately
- [ ] Body is concrete (no "I don't know" — name the specific thing missing)

## Error Cases

**Body too vague:** Surface to user via the comm itself: "I'm blocked on {KEY} but I don't have a concrete acceptance criterion. Need scope tightening." Treat as `type: ambiguity`.
**Label add fails (read-only):** Always succeeds via comms route as fallback. Surface in CC report.
**Ticket key invalid:** Cannot proceed — write `to: cowork, type: ambiguity` instead, naming the wrong key.

---

<!--
  Deployed from RuneSmith marketplace.
  Copyright 2026 Runemark Labs. Licensed under Apache-2.0.
  Source: https://github.com/runemarklabs/runesmith
-->
