---
name: check-comms
description: "Triage open comms in {PROJECT}.cc/comms/open/ — surface to-user items, draft replies, archive resolved pairs. Use when the user says \"check comms\", \"any messages from CC\", \"what does CC need\", \"check messages\", \"is CC blocked\", \"triage comms\", or wants to clear out CC's open comms."
compatibility: Requires Cowork desktop app environment.
---

# Check Comms

Read every `*.md` in `{PROJECT}.cc/comms/open/`. Surface `to: user` items first. Let user reply or defer. Resolve pairs and move to archive.

Works in both base config and atlassian-enabled config. In atlassian config, comms may carry `ticket: <KEY>` and `type: ticket-transition` — this skill executes the Jira mutation when that's the request, via the workspace's MCP-connected Atlassian tools.

## References

- `agents/comms-triager.md` — subagent for per-comm parsing and action

- `lib/comms-protocol.md` — file format and lifecycle
- `lib/comms-check.md` — same-named lib doc, but DIFFERENT thing (lib is the on-entry helper; this is the standalone triage skill)
- `lib/atlassian-enabled.md`
- `lib/jira-tags.md` — tags to add/remove on resolution
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 1. Locate comms folder

Find `{PROJECT}.cc/comms/open/`. If missing or empty: report and exit clean.

### 2. Atlassian-enabled?

Read marker. Used to decide whether to handle `type: ticket-transition` items inline.

## When to Use

Use for:
- After CC has been working — "what's CC need from me / Cowork?"
- Before kicking off another planning skill (the on-entry lib does a quick version of this; this skill is the deep version)
- Closing the loop on resolved comms (archive)

Do not use for:
- Writing new comms yourself (do that within other skills)
- Cleaning up archive (out of scope; archive is permanent)

## Workflow

### 1. List open comms

Read every `*.md` in `comms/open/`. Parse frontmatter. Group by `to:`:

- `to: user`  (highest priority)
- `to: cowork`
- `to: cc`  (informational; user can't act on these)

### 2. Surface to-user items

For each `to: user` comm:

```
[from cc, type: blocker]  <slug>
ticket: PROJ-42  (if atlassian-enabled)
created: <ISO>
body: <first 5 lines>

What do you want to do?
  [r]eply  — write an answer comm
  [d]efer  — leave open, move on
  [s]how   — print full comm
```

On `[r]eply`: prompt user for answer text. Write a new comm in `open/` with `from: user, to: cc, parent: <id>, type: answer`. Flip the original's `status: resolved` (in-place edit). On next iteration, both will archive.

On `[d]efer`: skip.

On `[s]how`: print full body, return to action prompt.

### 3. Handle to-cowork items

For each `to: cowork` comm:

#### type: ticket-transition (atlassian-enabled only)

CC asked Cowork to transition a Jira ticket. Body specifies `ticket: <KEY>` and target state.

Show user:
```
[from cc, type: ticket-transition]  <KEY>: <summary>
Target state: <state>

Surface a structured single-pick prompt: question "Approve transition?", options "Approve" / "Deny" / "Show details first".
```

On approve:
1. Look up transition id via `GET {SITE_URL}/rest/api/3/issue/{KEY}/transitions`.
2. Find transition by name matching target state. (Use Cowork's MCP atlassian connector or REST fallback if MCP can't.)
3. POST the transition.
4. On 200: write reply comm `from: cowork, to: cc, type: answer, parent: <id>`, status: resolved. Add `cowork-transition` label to the ticket. Remove `cc-done` label per `jira-tags.md`.
5. Flip both files to resolved, archive.

On deny: write reply with reason. Don't archive yet — let user re-engage later.

#### type: ambiguity / blocker / user-action where to: cowork (rather than user)

CC is asking Cowork directly (e.g., "what's the convention for X?"). Show user, prompt for guidance, write reply on user's behalf.

### 4. Show to-cc items

For `to: cc` comms (Cowork → CC, awaiting CC pickup):
- These need CC to act, not the user. Show as informational:
  ```
  [from cowork, type: task]  <slug>
  status: open since <ISO>
  CC will pick this up on next session.
  ```
- No action required from user; user can `[c]ancel` an outgoing task if it shouldn't be there.

### 5. Archive resolved pairs

For every comm pair where both files have `status: resolved`:
- Determine `<slug>` (from filename or frontmatter `slug` field).
- Move both files to `comms/archive/<YYYY-MM>/<slug>/`.
- Preserve filenames so timestamps are still discoverable.

### 6. Report

```
✓ Comms triaged
Surfaced to user: n
Handled (replied/transitioned): m
Archived: k pairs
Still open: x

Open comms by audience:
  to user:    {n}
  to cowork:  {n}
  to cc:      {n}
```

## Guard Rails

- [ ] Comms folder located; exit clean if empty
- [ ] Frontmatter parsed for every file (skip with warning if malformed)
- [ ] User explicitly approves any reply or transition before write
- [ ] Atlassian transitions only attempted when atlassian-enabled
- [ ] Tags updated per `jira-tags.md` on transition
- [ ] Resolved pairs archived; not deleted
- [ ] Malformed comm files surfaced but not modified

## Error Cases

**Malformed frontmatter:** Surface filename + parse error; ask user — fix manually, delete (with consent), or skip.
**Transition fails (Jira 400/403):** Show error; reply comm captures the failure; ticket stays in current state. User can retry after fixing the cause.
**Comms folder doesn't exist:** Either CC head doesn't exist (suggest `/devtools:bootstrap-cc`) or user is in the wrong workspace.
**User wants to bulk-defer:** Provide a `[d]efer all` shortcut that skips through.
**Comm references a ticket the user can't access:** Surface the auth error; user fixes Jira permissions; retry.
