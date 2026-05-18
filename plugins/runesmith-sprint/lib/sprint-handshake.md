# Sprint Handshake

Two-message exchange when Cowork hands a sprint to CC.

## Trigger conditions

`atlassian:start-sprint` fires explicitly when the user says "start sprint", "begin sprint", "kick off sprint", "let's start sprint X", or invokes `/atlassian:start-sprint`.

`atlassian:sprint-status` fires implicitly when:
- It runs on an atlassian-enabled project AND
- The active sprint id from Jira differs from the cached `atlassian.activeSprintId` in the marker.

In either case, Cowork writes a `session-init` comm. Implicit firing also updates the marker's cached sprint id.

## Message 1: Cowork → CC

File: `{PROJECT}.cc/comms/open/<ISO>-session-init-sprint-{SPRINT_ID}.md`

```markdown
---
id: <unique>
from: cowork
to: cc
type: session-init
sprint-id: {SPRINT_ID}
sprint-name: "{SPRINT_NAME}"
project-key: {JIRA_PROJECT_KEY}
board-id: {BOARD_ID}
status: open
created: {ISO}
---

# Begin Sprint {SPRINT_ID} - {SPRINT_NAME}

You are working Sprint {SPRINT_ID} ({SPRINT_NAME}) on Jira project
{JIRA_PROJECT_KEY}, board {BOARD_ID}.

## How to work

Pull active sprint tickets via Jira REST (read-only token in
`.credentials`). Pick the next ticket. Implement. Document on the
ticket itself.

Tag tickets per `@.claude/skills/atlassian/jira-tags.md`:
- `cc-plan`     - implementation plan
- `cc-action`   - actions taken
- `cc-decision` - non-obvious decisions
- `cc-blocked`  - paired with a blocker comm
- `cc-done`     - completed (also write a transition comm)

For state changes, write `type: ticket-transition` comms. Cowork
executes the Jira mutation. Your token cannot write Jira state.

For ambiguity / blockers / user-only actions: write a comm of the
matching type. Tag the ticket `cc-blocked` if blocked.

Do not contact the user directly. The user is reached only through
Cowork. Have user check on you by running `/atlassian:check-comms`.

## Acceptance

Reply with a `type: handshake` comm addressed `to: user` so the user
knows you're set up.
```

## Message 2: CC → user (via Cowork)

File: `{PROJECT}.cc/comms/open/<ISO>-handshake-sprint-{SPRINT_ID}.md`

CC writes this on its next session start after seeing the session-init.

```markdown
---
id: <unique>
from: cc
to: user
type: handshake
parent: <session-init id>
sprint-id: {SPRINT_ID}
status: open
created: {ISO}
---

# Acknowledged - Sprint {SPRINT_ID}

Working Sprint {SPRINT_ID} ({SPRINT_NAME}) on project
{JIRA_PROJECT_KEY}.

I will document plans, actions, and decisions on each ticket using
the canonical tags. Blockers and user-only actions go through comms;
mutations to Jira state go through comms (Cowork executes).

If I block or need user-only action, I'll write the comm and tag the
ticket `cc-blocked`. Run `/atlassian:check-comms` in Cowork to pick
those up.

## Acceptance

Acknowledge in any way (Cowork's check-comms surfaces this; user
clicks acknowledge).
```

## Resolution

When the user acknowledges via `atlassian:check-comms`:
- Both files (session-init + handshake) move to `comms/archive/<YYYY-MM>/handshake-sprint-{SPRINT_ID}/`.
- Both flip to `status: resolved` in their archived form.
- The CC marker's `atlassian.activeSprintId` reflects the new sprint.

## Re-firing

If a new sprint becomes active later, the cycle repeats. Old session-inits in archive are kept; only one open at a time.

If the implicit detection fires while the user already has open session-inits, Cowork archives the prior unresolved one with a note (`status: superseded`) and writes a fresh session-init for the new sprint.

## Skill responsibilities

| Skill | Writes | Reads |
|---|---|---|
| `atlassian:start-sprint` | session-init | marker |
| `atlassian:sprint-status` | session-init (only if sprint changed) | marker, Jira sprint endpoint |
| `atlassian:check-comms` | reply confirmations | open comms; archives resolved pairs |
| CC-side `sprint-pull` | handshake (first run after session-init detected) | session-init, marker |
