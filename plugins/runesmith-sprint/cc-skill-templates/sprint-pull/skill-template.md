---
name: sprint-pull
description: "Pull the active sprint from Jira and list ticket details. Use when the session starts on an atlassian-enabled CC workspace, when the user (via comms) asks \"what's the sprint\", or when picking the next ticket to work. Runs in Claude Code, not Cowork."
---

# Sprint Pull (CC-side)

Read the active sprint and its tickets via Jira REST. CC's read-only token is in `.credentials`. This skill reads only — never writes Jira.

This skill is deployed to `{PROJECT}.cc/.claude/skills/atlassian/` by `/runesmith-sprint:enable` running in Cowork. Do not edit it directly here unless you intend the change to flow to all future enables.

## References

- `.claude-code-workspace` (marker, in CC root) — for `atlassian.activeSprintId`, `boardId`, `jiraProjectKey`, `siteUrl`
- `.credentials` (in CC root) — for auth
- `@lib/jira-tags.md` — tag taxonomy

## Pre-Flight Checks

### 1. Marker exists

Read `.claude-code-workspace`. Verify `atlassianEnabled: true`. If false: report and exit. CC is in a non-atlassian workspace.

### 2. Credentials

`.credentials` has `ATLASSIAN_API_URL`, `ATLASSIAN_API_EMAIL`, `ATLASSIAN_API_TOKEN`, `ATLASSIAN_BOARD_ID`. If missing: write a `to: user, type: user-action` comm asking Cowork to re-run `/runesmith-sprint:enable`. Exit.

### 3. Session-init comm awaiting handshake

List `comms/open/`. If a `type: session-init` comm is unresolved AND no `type: handshake` reply exists yet, write the handshake reply per `@comms/README.md`. Then continue with sprint pull.

## Workflow

### 1. Determine target sprint

Read `atlassian.activeSprintId` from marker. If null, look up active sprint:

```
GET {SITE_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active
```

Pick first; cache as `activeSprintId` in marker (write back).

### 2. Fetch sprint tickets

```
POST {SITE_URL}/rest/api/3/search/jql
{
  "jql": "sprint = {SPRINT_ID} ORDER BY status ASC, priority DESC",
  "fields": ["summary", "description", "status", "assignee", "priority",
             "labels", "issuelinks", "customfield_10014"],
  "maxResults": 100
}
```

(`customfield_10014` is the Jira default Epic Link field; may differ — discover via `GET /rest/api/3/field` once per session.)

### 3. Filter by current state

Categorize tickets:
- **Available** — `status: "To Do"` or `status: "Selected for Development"`, NOT `cc-blocked`
- **In progress** — `status: "In Progress"`, possibly with my prior `cc-plan` / `cc-action` activity
- **Blocked** — labels include `cc-blocked` (these need human attention via comms; CC should not pick these)
- **Done** — `status: "Done"`

### 4. Pick next

Default: highest-priority Available ticket. Surface candidates:

```
Sprint {SPRINT_ID} — {SPRINT_NAME}

In progress (n)
  {KEY-1}  {priority}  {summary}    ← resume?
Available (n)
  {KEY-2}  {priority}  {summary}    ← next
  {KEY-3}  {priority}  {summary}
Blocked (n)
  {KEY-X}  cc-blocked   {summary}   (skip — needs Cowork or user)
Done (n)
  {KEY-Y}  cc-done      {summary}   (awaits transition)
```

Continue with the picked ticket: read full description, acceptance criteria, linked issues. Use `ticket-document` skill to record your plan as a `cc-plan` comment before starting work.

## Guard Rails

- [ ] Read-only — never POST/PUT/DELETE to Jira from this skill
- [ ] Marker `activeSprintId` cached and updated when sprint changes
- [ ] Skip `cc-blocked` tickets (don't compete with comms resolution)
- [ ] Surface up to first 100 tickets; paginate if more
- [ ] No company-specific assumptions about field ids — discover via `GET /rest/api/3/field`

## Error Cases

**No active sprint:** Write `to: cowork, type: ambiguity` comm: "no active sprint on board {BOARD_ID}. Need a sprint started." Exit; wait for reply.
**401:** Token expired or wrong. Write `to: user, type: user-action`: "CC's read-only Jira token failed. Re-run `/runesmith-sprint:enable` in Cowork to refresh." Exit.
**Sprint has 0 available, 0 in-progress, only blocked:** Write `to: user, type: blocker`: "All available sprint tickets are cc-blocked. Need triage." Exit.
**Network failure:** Retry once with backoff. If still failing, write `to: cowork, type: blocker` and exit.

---

<!--
  Deployed from RuneSmith marketplace.
  Copyright 2026 Runemark Labs. Licensed under Apache-2.0.
  Source: https://github.com/runemarklabs/runesmith
-->
