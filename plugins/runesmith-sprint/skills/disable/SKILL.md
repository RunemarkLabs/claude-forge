---
name: disable
description: "Turn off the Atlassian interconnect for this project — strip applied CLAUDE.md sections, remove markers, remove deployed CC skills. Use when the user says \"disable atlassian\", \"turn off atlassian\", \"unwire Jira\", \"remove atlassian from this project\"."
compatibility: Requires Cowork desktop app environment.
---

# Disable Atlassian Interconnect

Strip the Atlassian-driven workflow from a project. Inverse of `/atlassian:enable`. Idempotent.

Comms history (archive) is preserved. CC `.credentials` and any user-edited content outside section markers are preserved.

## References

- `lib/atlassian-enabled.md` — marker semantics
- `lib/jira-apply.md` — what gets stripped
- `lib/comms-check.md` — runs first
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 0. Comms check (always first)

If `to: user` items exist, surface them. User may want to resolve before disabling.

### 1. State

Verify project is currently atlassian-enabled. If not: "Already disabled. Nothing to do."

## Workflow

### 1. Show plan

```
Disable Atlassian for {PROJECT}?

This will:
  - Strip applied sections from <workspace>/CLAUDE.md
  - Strip applied sections from {PROJECT}.cc/CLAUDE.md
  - Delete <workspace>/.atlassian-enabled
  - Set atlassianEnabled: false in {PROJECT}.cc/.claude-code-workspace
  - Remove deployed skills: {PROJECT}.cc/.claude/skills/atlassian/

This will NOT:
  - Delete {PROJECT}.cc/.credentials (manual cleanup if desired)
  - Touch any open or archived comms
  - Touch any plans (including their tickets/ subfolder), drafts, or Jira state
```

### 2. Get consent

Wait for trigger phrase ("disable", "yes", "unwire").

### 3. Snapshot

Backup files that will change to `archive/_pre-atlassian-disable/<ISO>/`.

### 4. Strip CLAUDE.md sections

In each of `<workspace>/CLAUDE.md` and `{PROJECT}.cc/CLAUDE.md`:
- Locate `<!-- atlassian-section:start -->` and `<!-- atlassian-section:end -->`.
- Replace content between with an empty line.
- Keep the markers themselves so future re-enable is clean.

### 5. Update marker

Read `{PROJECT}.cc/.claude-code-workspace`. Set:

```json
{
  "atlassianEnabled": false,
  "atlassian": null
}
```

Preserve other fields (`project`, `repos`, etc.).

### 6. Remove `.atlassian-enabled` file

```
rm <workspace-root>/.atlassian-enabled
```

### 7. Remove deployed CC skills

Delete `{PROJECT}.cc/.claude/skills/atlassian/` directory.

### 7a. Emit Project Instructions removal note (CRITICAL — don't skip)

Cowork's Project Instructions UI field is invisible to the agent. Disable cannot edit it directly. It MUST surface a removal instruction for the user.

The Atlassian supplement was wrapped in HTML-comment markers when sprint:enable emitted it. Tell the user to remove everything between (and including) the markers:

```
─────────────────────────────────────────────────────────────
PROJECT INSTRUCTIONS — atlassian supplement removal

Open Cowork's UI (app sidebar → project settings → Instructions)
and delete the entire block from:

  <!-- runesmith:atlassian-start -->

through to and including:

  <!-- runesmith:atlassian-end -->

inclusive. The base Project Instructions content stays.
─────────────────────────────────────────────────────────────
```

### 8. Report

```
✓ Atlassian disabled
Stripped: <workspace>/CLAUDE.md, {PROJECT}.cc/CLAUDE.md
Removed: .atlassian-enabled, .claude/skills/atlassian/
Marker updated: atlassianEnabled: false

Preserved:
  {PROJECT}.cc/.credentials  (delete manually if desired)
  comms/archive/             (audit trail)
  plans/, drafts/            (untouched; ticket JSON drafts under plans/active/<slug>/tickets/ untouched)
  archive/tickets-pushed/    (ticket history, untouched)

Re-enable any time with /runesmith-sprint:enable.
```

## Guard Rails

- [ ] Comms check ran first
- [ ] User consented explicitly
- [ ] Snapshot before any modify
- [ ] Section markers preserved (empty body); never deleted
- [ ] Marker JSON updated atomically
- [ ] CC `.credentials` not touched
- [ ] Comms not touched

## Error Cases

**Already disabled:** Exit clean; no-op.
**Marker file mismatch (workspace says disabled, CC says enabled):** Surface the inconsistency, default to disabling both, ask user before continuing.
**CC head deleted:** Workspace marker can still be removed; skip CC operations and warn.
