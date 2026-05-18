---
name: start-sprint
description: "Hand the active (or specified) sprint to Claude Code via a session-init comm. Use when the user says \"start sprint\", \"begin sprint\", \"start sprint X\", \"kick off sprint\", \"kick off the next sprint\", \"let's start the sprint\", \"time to start sprint X\", or wants to explicitly hand off sprint work to CC."
compatibility: Requires Cowork desktop app environment.
---

# Start Sprint Handshake

Write a `session-init` comm telling Claude Code which Jira sprint it's working. Updates the CC marker's `activeSprintId`. Pairs with CC's `handshake` reply (CC writes that on next session start).

## References

- `lib/sprint-handshake.md` — comm format
- `lib/atlassian-enabled.md` — must be enabled
- `lib/atlassian-rest.md` — sprint endpoints
- `lib/comms-protocol.md` — comms file shape
- `lib/comms-check.md` — runs first
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 0. Comms check (always first)

### 1. Atlassian enabled

If not enabled: "Atlassian not enabled for this project. Run `/atlassian:enable` first."

### 2. CC head exists

Verify `{PROJECT}.cc/comms/open/` exists.

### 3. Credentials

Cowork-side `.credentials` for Jira reads.

## When to Use

Use for:
- Beginning work on a new sprint
- Re-firing a session-init for the current sprint (e.g., after CC archived the prior one)
- Switching CC's active sprint mid-cycle (rare; ask user to confirm)

Do not use for:
- Just checking sprint state → `/atlassian:sprint-status`
- Triaging comms → `/atlassian:check-comms`

## Workflow

### 1. Determine target sprint

Default: the **active** sprint on the project's board. Fetch via:

```
GET {SITE_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active
```

If multiple active sprints (parallel boards): list, ask user to pick.
If none active: list `state=future` sprints, ask user to pick or start one in Jira UI first.

User can override by saying "start sprint 42" — explicit sprint id wins.

Confirm: "Start sprint {SPRINT_ID} ({SPRINT_NAME})?"

### 2. Check for existing session-init

List `{PROJECT}.cc/comms/open/`. If a `type: session-init` comm exists for a different sprint:
- Mark it `status: superseded`, move to `archive/<YYYY-MM>/<old-slug>/`.
- Note in the new comm body that it supersedes the old one.

If a session-init exists for the same sprint and is unresolved:
- Ask user: "Existing session-init for this sprint not yet acked. Re-fire (replace) or skip?"

### 3. Write session-init comm

Per `lib/sprint-handshake.md`. Filename:

```
{PROJECT}.cc/comms/open/<ISO>-session-init-sprint-{SPRINT_ID}.md
```

Body uses canonical template, tokens substituted. `to: cc`, `status: open`.

### 4. Update CC marker

Read `{PROJECT}.cc/.claude-code-workspace`. Set `atlassian.activeSprintId = {SPRINT_ID}`. Write back.

### 5. Report

```
✓ Sprint {SPRINT_ID} ({SPRINT_NAME}) handed to CC
Comm: {PROJECT}.cc/comms/open/<filename>
Active sprint cached in marker.

CC will read on next session start and reply with a handshake comm
addressed to you. Run /atlassian:check-comms to pick up the handshake
when it appears.
```

## Guard Rails

- [ ] Comms check ran first
- [ ] Atlassian enabled
- [ ] Sprint id confirmed (active by default; explicit override allowed)
- [ ] Existing session-init for different sprint archived as superseded
- [ ] Comm file written with full required frontmatter
- [ ] Marker `activeSprintId` updated
- [ ] No Jira writes (read-only board sprint lookup)

## Error Cases

**Atlassian not enabled:** "Run `/atlassian:enable` first."
**No active sprint, no future sprints:** "No sprints exist on this board. Create one in Jira UI first." Provide URL.
**Multiple active sprints:** Surface list, ask user.
**User asks for sprint id that doesn't exist:** Verify via `GET /rest/agile/1.0/sprint/{id}`. If 404, surface and re-ask.
**CC head missing:** "Run `/devtools:bootstrap-cc` first." (Should not happen if enable succeeded; but defensive.)
