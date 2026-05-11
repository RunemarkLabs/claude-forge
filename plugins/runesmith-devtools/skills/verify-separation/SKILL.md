---
name: verify-separation
description: >
  Verify the boundary between source repos and workspace files. Checks that source keywords route changes correctly, project-specific config doesn't leak into repos, and Cowork plugin skills live in plugins (not loose in .claude/skills/). Triggers on: "verify separation", "check boundaries", "audit workspace", "are my files in the right place", or when suspicious that the repo/workspace boundary is blurred.
model: haiku
---

# Separation Auditor

Verify workspace/repo boundaries are correctly maintained.

Audit: Are repo files separate from workspace config? Are keywords routing correctly? Is project-specific config leaking into source?

## References

- `agents/workspace-scanner.md` — subagent for directory walk + categorized findings

- `lib/install-paths.md` — runtime detection
- `lib/credentials.md` — `.credentials` location rules
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

No pre-flight checks needed. This is a read-only audit.

## When to Use

Use for:
- After adding files, verify they're in the right location
- Proactive audit after major changes
- Troubleshooting "which copy am I editing?"
- Ensuring source repos stay deployable

Do **not** use for:
- Automated file movement (always ask first)
- Changing folder structure (use planning)

## Workflow

### 1. Audit Directory Structure

Check for correct separation:

**Workspace Root (should exist):**
- /.claude/skills/ — cowork skills ✓
- /.credentials — API tokens (gitignored) ✓
- /CLAUDE.md — workspace config ✓
- /claude-code/ — source repos (separate)

**Source Repos (should NOT have workspace config):**
```
Check /claude-code/*/ for:
- .claude/ (project-specific? move to workspace)
- CLAUDE.md (project-specific? move to workspace)
- .credentials (NEVER here! Should be workspace-level)
- Cowork skills (should be in workspace, not repo)
```

**Plugin Structure (should be correct):**
```
Check installed plugin dir (per `lib/install-paths.md`)*/
for each plugin:
  - .claude-plugin/plugin.json exists? ✓
  - skills/ directory exists? ✓
  - All skill files in skills/, not root? ✓
```

### 2. Check Keyword Routing

Verify keywords work correctly:

**"source" / "repo" keyword:**
- Edits only touch /claude-code/*/ ✓
- Never modify workspace files

**"local" / "workspace" / "cowork" keyword:**
- Edits only touch workspace root ✓
- Never modify files under /claude-code/

**No keyword:**
- Clarification asked before touching either

### 3. Identify Violations

Look for:
- Project-specific CLAUDE.md in /claude-code/{repo}/
- Credentials in /claude-code/
- Plugin skills loose in .claude/skills/
- Source files in workspace root
- Workspace config in /claude-code/

### 4. Report Findings

Output format:

```
✓ Separation Audit

✓ Workspace Structure
  ✓ /.claude/skills/ — organized
  ✓ /CLAUDE.md — at root
  ✓ .credentials — workspace-level
  ✓ /claude-code/ — isolated

✓ Source Repos
  ✓ /claude-code/* — clean
  ✓ No workspace config in repos
  ✓ No credentials in repos

✓ Plugins
  ✓ installed plugin dir (per `lib/install-paths.md`) — correct structure
  ✓ All skills in skills/ directories

Boundary Status: CLEAN ✓
```

Or, if violations found:

```
⚠️ Separation Issues Found

Issues:
1. /claude-code/cowork-bootstrap/CLAUDE.md exists (should be workspace root)
   → Move to /CLAUDE.md? (Project-specific config shouldn't be in source)

2. /claude-code/claude-code-bootstrap/.credentials exists
   → Delete immediately (credentials leaked to source!)

3. installed plugin dir (per `lib/install-paths.md`)plugin-name/skills/ is empty
   ✓ (OK if skills are elsewhere, but verify intentional)

Action Items:
- [ ] Move /claude-code/*/CLAUDE.md to workspace root
- [ ] Delete any .credentials from /claude-code/
- [ ] Verify plugin structure is intentional
```

### 5. Offer Fixes

For each violation, ask:
- "Move {file} from {current} to {correct}?"
- "Delete {leaked_credentials}?"
- "Review {unclear_structure}?"

Wait for user approval before making changes.

## Guard Rails

- [ ] All workspace files at root (not in /claude-code/)
- [ ] All source files isolated in /claude-code/
- [ ] No credentials outside workspace root
- [ ] No workspace config in repos
- [ ] Plugin structure correct
- [ ] User approves before moving files
- [ ] No destructive changes without confirmation

## Error Cases

**Boundary is blurred:** "Found project config in source repos. Review before moving."

**Credentials leaked:** "Found .credentials in {repo}. Delete immediately!"

**Unclear structure:** "Some files don't fit the pattern. Review manually."

**User cancels audit:** "No files moved. Audit complete."
