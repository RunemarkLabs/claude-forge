---
name: plan
description: >
  Plan a change before executing — capture problem, decision, why-now, scope, trade-offs to a clean markdown file under plans/active/. Use when the user says "plan this", "let's plan", "draft a plan for", "spec this out", "I want to plan", or wants to think through a substantial change before any writes happen. Chat-first, file-last workflow.
---

# Plan a Change

Capture a project plan as `plans/active/<slug>/plan.md` — clean, claude-readable markdown that serves as the source of truth for project intent. Both Cowork and Claude Code read from `plans/active/`.

This skill performs no API calls. It writes one local file (plus optional decisions log + refs dir).

## References

- `lib/plan-format.md` — canonical plan.md schema
- `lib/comms-check.md` — check-on-entry pattern
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 0. Comms check (always first)

See `lib/comms-check.md`. If any `to: user` comms are open, surface and let user decide before proceeding.

### 1. Workspace shape

Verify `plans/` exists at workspace root. If not, suggest running `/core:reallocate` first.

## When to Use

Use for:
- Substantial restructuring or refactoring
- Architectural decisions with trade-offs
- Multi-part work that needs the *why* recorded
- Establishing context Claude Code should read when working

Do not use for:
- Small obvious fixes the user just asked for explicitly
- Read-only queries
- Pure conversation / brainstorming (unless that converges into a plan)

## Workflow

### 1. Discuss

Surface what the user wants to plan. Ask only what's needed to fill the schema:
- Problem (what pain or opportunity)
- Decision (what we're going to do)
- Why now (the trigger)
- Scope (in / out)
- Trade-offs
- Alternatives considered
- References

Iterate in chat until the user converges.

### 2. Propose slug

Generate a short kebab-case slug from the title. Verify it's unique within `plans/active/`. If collision, append `-2`.

### 3. Show draft

Show the proposed `plan.md` content per `plan-format.md`. Frontmatter:

```yaml
---
slug: <kebab-slug>
status: open
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: <user>
supersedes: []
related: []
tickets: []
---
```

Body uses the canonical sections from `plan-format.md`.

### 4. Get consent

Ask: "Save this plan to `plans/active/<slug>/plan.md`?"

Wait for explicit approval ("yes", "save it", "create the plan", "make it"). Do not write without consent.

### 5. Write

Create:
```
plans/active/<slug>/
├── plan.md           the plan
├── decisions.md      empty stub with H2 ready for entries
└── refs/             empty dir
```

`decisions.md` stub:
```markdown
# Decisions for <slug>

Append-only log of decisions made under this plan.

## YYYY-MM-DD — <decision title>
**What:** ...
**Why:** ...
**Participants:** ...
```

### 6. Report

```
✓ Plan created
plans/active/<slug>/plan.md
status: open
```

If the workspace is atlassian-enabled (if the workspace is atlassian-enabled, per the runesmith-sprint plugin), suggest:
> Next: run `/atlassian:plan-to-tickets` to draft Jira tickets from this plan.

Otherwise:
> Next: when ready, write a task comm to CC via comms/, or invoke a publish skill to push to Confluence.

## Guard Rails

- [ ] Comms check ran first
- [ ] Slug is kebab-case, unique within active/
- [ ] All required schema sections present
- [ ] User explicitly consented to write
- [ ] No file written without consent
- [ ] Plan dir contains plan.md, decisions.md stub, refs/

## Error Cases

**`plans/` missing:** "Workspace doesn't have plans/ yet. Run `/core:reallocate` first to set up the structure."
**Slug collision:** Auto-append `-2`, surface to user, get re-confirmation.
**User keeps editing without converging:** After ~3 rounds, ask "Should we save this draft now and iterate from disk, or keep refining first?"
**Empty required section:** "Section <name> is empty. Plans must have all of Problem, Decision, Why now, Scope. Add content or skip the plan."
