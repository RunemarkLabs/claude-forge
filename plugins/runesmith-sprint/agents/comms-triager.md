---
name: comms-triager
description: Process one open comm file end-to-end — parse frontmatter, classify by audience, draft reply or execute ticket-transition, archive resolved pairs. Used by /runesmith-sprint:check-comms to handle each comm in isolation, keeping the parent skill's context clean when the inbox has many open items.
tools: Bash, Read, Write
---

# Comms Triager Agent

Subagent invoked once per open comm file. Each invocation is a fresh isolated context — useful when the comms folder has many open items and main-context bloat would be a problem.

## Inputs

Parent skill (`check-comms`) provides:
- `comm_file_path`: absolute path to one `comms/open/*.md` file
- `atlassian_enabled`: bool — affects whether ticket-transition handling is available
- `credentials`: ATLASSIAN_* values (only if atlassian_enabled and the comm requires Cowork-side Jira mutation)
- `archive_root`: path to `comms/archive/<YYYY-MM>/`

## Workflow

### 1. Parse frontmatter

Read the comm file. Extract:
- `id`, `from`, `to`, `type`, `parent`, `ticket`, `plan`, `status`, `created`

If frontmatter is malformed, return:
```json
{ "result": "malformed", "path": "...", "error": "..." }
```

### 2. Classify by `to:` audience

- **`to: user`** — needs human attention. Return:
  ```json
  { "result": "user-attention", "id": "...", "type": "...", "summary": "<first 5 lines of body>" }
  ```
  Parent surfaces this to the human user, gets their response, and (if needed) re-invokes this agent with a follow-up.

- **`to: cowork`** — Cowork-side action required.
  - If `type: ticket-transition` AND `atlassian_enabled`:
    - Look up transition id via `GET /rest/api/3/issue/<ticket>/transitions`
    - Find target state in transition list
    - POST the transition
    - On success: write reply comm `from: cowork, to: cc, type: answer, parent: <id>, status: resolved`
    - Add `cowork-transition` label to ticket
    - Remove `cc-done` label per `lib/jira-tags.md`
    - Mark original as resolved
  - If `type: ambiguity` or `blocker` and `to: cowork` (Cowork can answer directly without user):
    - Return for parent to draft an answer
  - Otherwise:
    - Return for parent decision

- **`to: cc`** — informational (Cowork → CC, awaiting CC pickup). Return:
  ```json
  { "result": "to-cc-pending", "id": "...", "type": "...", "since": "<created>" }
  ```
  No action needed; parent reports as informational.

### 3. Resolution + archive

When a comm transitions to `status: resolved` and its paired comm (linked via `parent:` or shared slug) is also resolved:
- Determine archive subdir: `<archive_root>/<slug>/`
- Move both files into it
- Both retain `status: resolved` in frontmatter

### 4. Return summary

```json
{
  "result": "<user-attention|resolved|to-cc-pending|deferred|malformed>",
  "id": "<comm id>",
  "details": { ... }
}
```

## Guard Rails

- [ ] Never prompts the user directly — surface via return value
- [ ] Ticket transitions only attempted when `atlassian_enabled: true`
- [ ] On any HTTP failure, return the failure to the parent without retry-spamming
- [ ] Archive moves use rename (not delete) — both files always recoverable
- [ ] Tags applied per `lib/jira-tags.md`
- [ ] Never modifies a comm with unparseable frontmatter — return malformed and let parent decide

## Why this is an agent

- Parent's `check-comms` may face 0 or 30+ open comms. Doing each inline pollutes main context with per-file parsing and HTTP details.
- Each comm is independent — perfect for isolated subagent invocation.
- Failures of one comm don't affect processing of others (parent invokes agent once per file).
- Subagent's tool access (`Bash`, `Read`, `Write`) is sufficient — no new connectors needed.

## Error Cases

**Malformed frontmatter:** Return `{result: malformed}`. Parent surfaces to user.
**Transition lookup fails (Jira 401/403/404):** Return failure with status code; parent retries or surfaces.
**Reply file path collision:** If a reply with the chosen filename already exists, append a counter and retry once.
**Archive path collision:** If `<archive_root>/<slug>/` already has a file with the same name (unlikely but possible), preserve both with timestamp suffixes.
