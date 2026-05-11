# Comms-Check Helper

Check-on-entry pattern for every Cowork-side planning skill. Applies in both base config and atlassian-enabled config.

## When to run

Every planning-relevant skill MUST run this check at the **start** of its workflow, before gathering details or making changes:

- `core:plan`
- `atlassian:check-comms`
- `atlassian:start-sprint`
- `atlassian:sprint-status`
- `atlassian:plan-to-tickets`
- All atlassian publish skills (`feature-doc`, `architecture-doc`, `project-overview`, `decisions-log`, `known-issues`, `roadmap`, `session-log`)

If the workspace has no `{PROJECT}.cc/` or no `comms/open/` directory, skip silently.

## Check sequence

### 1. Locate comms

Find `{PROJECT}.cc/comms/open/` by:
1. Check for marker file `<workspace-root>/{PROJECT}.cc/.claude-code-workspace`. The `{PROJECT}.cc/` folder name is the marker's parent.
2. If multiple `*.cc/` folders exist (rare), pick the one matching the workspace root folder name. Skip if none match.
3. If no `comms/open/` dir, skip.

### 2. Read open comms

List every `*.md` in `comms/open/`. Parse YAML frontmatter for each:
- `id`, `from`, `to`, `type`, `parent`, `ticket`, `status`, `created`

Skip files where `status: resolved` (shouldn't normally be in `open/`, but tolerate it).

### 3. Group by audience

Bucket open comms by `to:`:
- `to: user` — surface to the user FIRST. These are blockers / user-actions / handshakes that need human attention.
- `to: cowork` — surface to the user as informational, then handle programmatically.
- `to: cc` — these are messages waiting for CC to read. Inform user that CC has pending work.

### 4. Surface to user

If any `to: user` items exist, pause the parent skill's workflow and present:

```
{N} open comms need your attention before we proceed:

  [from cc, blocker]  <slug>
  parent ticket: <KEY> (if atlassian-enabled)
  body: <first 2 lines>

  [from cc, user-action]  <slug>
  body: <first 2 lines>

What do you want to do?
  1. Resolve them now (work through them one at a time)
  2. Acknowledge and continue with the original request
  3. Cancel
```

Wait for user choice. On choice 1, hand off to `atlassian:check-comms` workflow. On choice 2, continue. On choice 3, abort.

### 5. Handle `to: cowork` items

For each `to: cowork` item:
- If `type: ticket-transition` (atlassian-only) and the parent skill has Jira access — execute the transition via Cowork's MCP and write a `type: answer` reply.
- Otherwise — surface to user as "Cowork-bound: <slug>" and let the user decide whether to handle inline or defer.

### 6. Continue parent workflow

After handling (or deferring all), continue with the parent skill's actual job. The check-on-entry has happened; it does not run again within the same skill invocation.

## Performance

The check is cheap (read directory, parse frontmatter). Skip cases (no `{PROJECT}.cc/`, no comms/open/) exit in microseconds. Real cost only when there are many open comms — which is itself a signal worth surfacing.

## Implementation note

Skills that cite this lib include the section:

```markdown
### 0. Comms check (always first)

See `lib/comms-check.md`. Run check on entry. Surface any `to: user`
items to the user before proceeding.
```

Do not skip this step. Skills that omit it leave CC's blockers and user-actions invisible to the user, breaking the workflow contract.
