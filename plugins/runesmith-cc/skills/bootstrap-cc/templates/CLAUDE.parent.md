# Claude Code Workspace - {PROJECT}

Monorepo head for the {PROJECT} Claude Code workspace. Repos live as
subdirectories. Each repo has its own CLAUDE.md.

## Workflow

You receive tasks via `comms/open/` files written by Cowork. You DO NOT
contact the user directly.

For ambiguity, blockers, or user-only actions, write a comm file:

```
comms/open/<ISO>-<slug>.md
```

with frontmatter:

```yaml
---
id: <id>
from: cc
to: cowork | user
type: ambiguity | blocker | user-action
parent: <id of comm you're responding to, if any>
status: open
created: <ISO>
---
```

Block on that work item until a reply arrives in `comms/open/` with
`parent: <your-id>, type: answer`. Then archive both files to
`comms/archive/<YYYY-MM>/<slug>/`.

The user is reached only through Cowork. You communicate with Cowork via
files in `comms/`.

## Memory hierarchy

- This file: monorepo-level rules (always loaded)
- `./<repo>/CLAUDE.md`: repo-shared
- `./<repo>/<subfolder>/CLAUDE.md`: scoped

## Reference

- Active plans: `@../plans/active/`  (read-only - Cowork owns these)
- Active comms: `@comms/open/`
- Comms protocol: `@comms/README.md`

<!-- atlassian-section:start -->
<!-- This block is empty until /runesmith-sprint:enable runs and applies sprint workflow rules. -->
<!-- atlassian-section:end -->

<!-- agent-ops:start -->
## Agent operating principles

**File operations**
- Project root is real; bash sandbox is a shadow. Default to direct file tools (Read/Write/Edit/Glob). Bash is for scripts and shell pipelines.
- When bash fails with "No such file" on an existing path, the shadow is stale. Switch vectors - direct tools, parent-dir-replace, or copy-to-/tmp/-and-back. Don't retry the same bash command.
- File ops in this CC head are agent territory. Delete, move, rename - do it. Don't defer file chores to the user. (Repo internals - inside `{repo}/` - are handled by repo-scoped tooling and per-repo CLAUDE.md rules.)

**Destructive operations**
- Confirm scope before mutating external systems (Jira, Confluence, git push). Wait for the trigger phrase from your task comm.
- Never commit or push unless told. Stop at staged.

**User interaction**
- You communicate with the user only via Cowork through `comms/`. Never address the user directly.
- For ambiguity, blockers, or user-only actions, write a `comms/open/{ISO}-{slug}.md` comm with the appropriate `to:` and `type:`.

**Placeholder syntax**
- Curly braces `{PLACEHOLDER}` only when authoring plugin metadata. Never angle brackets `<placeholder>` - Cowork's upload validator rejects them.

**Workspace boundaries**
- The CC head (this directory) is yours to organize. Repos under `<repo>/` are yours to work in. The workspace root (the parent directory) is Cowork's territory - don't reach into it.
- For repo-level cleanup (dead code, unused exports, unused deps), use `/code-tech-debt` (deployed in `.claude/skills/code-tech-debt/`).

**Sandbox vs permissions**
- "Permission denied" → request permission.
- "No such file" on an existing path → sandbox bug. Switch vector.
- Don't conflate the two.

This section is skill-managed. Re-running `/runesmith-cc:bootstrap-cc` (from Cowork) refreshes the content between markers. User additions belong outside the marker pair.
<!-- agent-ops:end -->

<!--
  Deployed from RuneSmith marketplace.
  Copyright 2026 Runemark Labs. Licensed under Apache-2.0.
  Source: https://github.com/runemarklabs/runesmith
-->
