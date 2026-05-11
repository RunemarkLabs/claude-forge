---
name: ticket-document
description: >
  Append a plan, action, or decision as a Jira ticket comment and tag the ticket appropriately. Use when CC starts work, makes a non-obvious decision, or completes a meaningful action on a ticket. Runs in Claude Code.
---

# Ticket Document (CC-side)

Write to Jira ticket comments + labels via REST. CC's token is read-only by design — but commenting on a ticket is a "write" that requires permissions beyond pure read.

**Important:** if CC's token does NOT have comment permission (typical for true read-only scoped tokens), this skill writes a comm of `type: ticket-transition` requesting Cowork to add the comment + label, instead of attempting the write itself.

CC's token capabilities should be configured by the user during `/runesmith-sprint:enable`:
- **Minimum:** read tickets, read sprints
- **Recommended:** + comment on tickets (lets CC document directly)
- **Not granted:** transitions, label management on existing tickets, ticket creation/deletion (those go through comms → Cowork)

This skill detects which capability tier is available and routes accordingly.

## References

- `@lib/jira-tags.md`
- `.credentials`, `.claude-code-workspace`

## Pre-Flight Checks

1. Marker says `atlassianEnabled: true`.
2. `.credentials` has Jira creds.
3. Probe write capability (cache result for the session): `POST /rest/api/3/issue/{KEY}/comment` dry-run or smallest valid request. If 403, mark capability as read-only.

## Workflow

### 1. Gather inputs

- Ticket key (`KEY-123`)
- Type: `plan` | `action` | `decision`
- Body markdown — what to record

Convert markdown → ADF for Jira comment body (per `@lib/atlassian-rest.md`).

### 2. Branch on capability

#### Capability: comment-write available

```
POST {SITE_URL}/rest/api/3/issue/{KEY}/comment
{ "body": <ADF document> }
```

Then add the matching label:

```
PUT {SITE_URL}/rest/api/3/issue/{KEY}
{ "update": { "labels": [{ "add": "cc-plan" }] } }
```

Tag mapping:
- `plan` → `cc-plan`
- `action` → `cc-action`
- `decision` → `cc-decision`

If label add 403: revert to comms route for the label only.

#### Capability: read-only

Write a comm:

```
comms/open/<ISO>-document-{KEY}.md
```

```yaml
---
id: <id>
from: cc
to: cowork
type: ticket-transition
ticket: {KEY}
status: open
---
```

Body specifies "Add comment + label `cc-plan`". Cowork's `check-comms` will execute via MCP.

### 3. Report (in CC chat)

```
Documented {KEY}:
  type: plan
  via: direct (or "via: comms — awaiting Cowork")
```

## Guard Rails

- [ ] Capability probe cached for session (don't re-probe per call)
- [ ] Comment body is valid ADF
- [ ] Tag matches type
- [ ] Comms route used when direct write not permitted
- [ ] No transitions or status changes from this skill (those go through comms)

## Error Cases

**Comment 400 (ADF invalid):** Validate ADF structure, retry once, then surface.
**Comment 403:** Capability tier wrong — re-probe. If still 403, switch to comms route.
**Label add 403:** Comms route for label.
**Ticket 404:** Wrong key. Surface to user via comm.

---

<!--
  Deployed from RuneSmith marketplace.
  Copyright 2026 Runemark Labs. Licensed under Apache-2.0.
  Source: https://github.com/runemarklabs/runesmith
-->
