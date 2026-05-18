---
name: sprint-status
description: "Show the active sprint board state plus any open comms summary. Auto-fires a session-init comm if the active sprint changed since last cache. Use when the user says \"sprint status\", \"what's in the sprint\", \"where are we in the sprint\", \"show me the sprint\", \"sprint update\", \"any blockers in the sprint\"."
model: haiku
---

# Sprint Status

Read-only sprint summary plus comms triage hint. Atlassian-enabled only — replaces `project-status` for this config.

If the active sprint id from Jira differs from the cached `activeSprintId` in the marker, this skill **implicitly fires** a session-init comm (per `start-sprint`) before reporting. That keeps CC in sync without requiring the user to remember.

## References

- `lib/atlassian-rest.md` — search/sprint endpoints
- `lib/comms-check.md` — runs first
- `lib/atlassian-enabled.md`
- `lib/sprint-handshake.md`
- `lib/jira-tags.md`
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 0. Comms check (always first)

Surface any `to: user` items immediately.

### 1. Atlassian enabled

If not, route the user to `/atlassian:enable` or `/atlassian:project-status` (the existing read-only skill that works in any config).

### 2. Credentials

Cowork-side `.credentials` for Jira read.

## Workflow

### 1. Fetch active sprint

```
GET {SITE_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active
```

Pick first active sprint (or surface multi-active for user pick if rare).

### 2. Implicit handshake

Compare new sprint id to cached `atlassian.activeSprintId` in marker.

If different (or null):
- Hand off to `start-sprint` workflow: write session-init comm, archive any superseded one, update marker.
- Note in this skill's output: "Detected new active sprint — fired session-init."

If same: no comm action.

### 3. Fetch sprint tickets

```
POST {SITE_URL}/rest/api/3/search/jql
{
  "jql": "sprint = {SPRINT_ID} ORDER BY status ASC, updated DESC",
  "fields": ["summary", "status", "assignee", "priority", "labels", "updated"],
  "maxResults": 100
}
```

### 4. Group + summarize

Bucket tickets by `status.name`. Highlight tickets carrying tags from `jira-tags.md`:

- `cc-blocked` — surface separately as Blockers
- `cc-done` — pending transition
- `needs-user` — pending user action
- `cowork-planned` — Cowork-spawned this sprint

### 5. Comms summary

Read `{PROJECT}.cc/comms/open/`. Count by `to:`:
- `to: user`
- `to: cowork`
- `to: cc`

### 6. Output

```
Sprint {SPRINT_ID} — {SPRINT_NAME}    (board {BOARD_ID})

By status
  In Progress (n)
    {KEY-1}  {summary}  {assignee}  {tags}
    ...
  To Do (n)
    ...
  Done (n)
    ...

Blockers ({cc-blocked count})
  {KEY-3}  {summary}  ← cc-blocked, needs-user

CC done, pending transition ({cc-done count})
  {KEY-7}  {summary}

Comms ({PROJECT}.cc/comms/open/)
  {n} to user        — run /atlassian:check-comms
  {n} to cowork
  {n} to cc

Board: {SITE_URL}/jira/software/projects/{JIRA_PROJECT_KEY}/boards/{BOARD_ID}
```

If a session-init was fired in step 2, prepend:

```
ℹ Active sprint changed → wrote session-init comm.
  CC will ack via comms on next session start.
```

## Guard Rails

- [ ] Comms check ran first
- [ ] Atlassian enabled
- [ ] Implicit handshake fired only when sprint id changed
- [ ] Search uses `/search/jql` POST (not deprecated GET `/search`)
- [ ] No mutating writes
- [ ] Output is scannable, grouped, bounded (max 100 tickets)

## Error Cases

**No active sprint:** "No active sprint on board {BOARD_ID}. Use Jira UI to start one or run `/atlassian:start-sprint` to pick a future sprint."
**Sprint has 0 tickets:** Note "Sprint empty. Run `/atlassian:plan-to-tickets` to populate from a plan."
**API 401 on sprint endpoint:** Re-read `.credentials`, retry once, then suggest `/core:setup`.
**Multiple active sprints:** List them; ask user to pick which is "the" one for purposes of the marker.
