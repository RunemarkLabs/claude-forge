---
name: skill-updater
description: "Propagate convention changes across skills safely by orchestrating per-skill modifications through Anthropic's skill-creator. Use after a decision changes how the system works - variable renames, workflow changes, lib reference updates, removed features, new conventions. Triggers on: \"update skills\", \"propagate this\", \"skills are stale\", \"sync the change\", \"make sure skills reflect this\", or when a decision contradicts what existing skills describe."
compatibility: Requires Cowork desktop app environment.
---

# Skill Updater

Orchestrator for cross-skill convention propagation. This skill is the **coordinator**: it knows which skills to touch and what change to apply. Anthropic's `skill-creator` skill is the **executor**: it knows how to safely modify one skill at a time, with frontmatter validation and trigger-phrase eval.

This split exists so that bulk changes never corrupt skill files. Every per-skill rewrite goes through skill-creator's modify path and gets validated before the next skill is touched.

## References

- `lib/install-paths.md` - runtime detection and plugin scan paths
- Anthropic's `skill-creator` skill (ships with Claude) - used for per-skill modify + validation
- `lib/user-prompts.md` - structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

### 1. Detect plugin directories

Per `install-paths.md`:
1. `CLAUDE_PLUGINS_DIR` env var if set
2. `~/.claude/plugins/` (Claude Code / Teams)
3. Cowork session `rpm/plugin_*/`
4. Marketplace source: `plugins/*/` in this repo

If none found: "No plugins installed and no marketplace source. Nothing to update."

### 2. Confirm skill-creator availability

`skill-creator` is an Anthropic-shipped skill available in any Claude environment. Verify it can be invoked. If somehow unavailable: degrade to dry-run mode (preview-only, no writes).

## When to Use

Use for:
- Architecture decision changes (e.g. lib reference rename)
- Workflow convention updates (e.g. new guard-rail pattern)
- Variable / token renames (e.g. `{SPACE_KEY}` → `{CONFLUENCE_SPACE}`)
- Deprecated patterns being phased out
- New required checks added across all skills

Do not use for:
- One-off skill edits → use Anthropic's `skill-creator` directly
- Plugin-specific customizations that shouldn't sync across all skills
- Small typo fixes in a single file → fix in place

## Workflow

### 1. Describe the change

Ask user:
- What decision changed?
- What's the old pattern (regex or literal)?
- What's the new pattern?
- Scope - all plugins, specific plugin(s), or specific skills?
- Any per-skill exceptions where the old pattern should remain?

Reject vague changes ("update the skills"). Demand specificity (e.g. "rename any reference from one library file name to another across all runesmith plugins, with the exact old and new names provided").

### 2. Find affected skills

Scan plugin source per `install-paths.md`. For each `SKILL.md`:
- Grep for old pattern
- Capture line number and surrounding context

Build a list:
```
Affected: 12 SKILL.md files across 4 plugins
  runesmith-jira/skills/ticket/SKILL.md  (3 occurrences)
  runesmith-jira/skills/bug-report/SKILL.md  (1 occurrence)
  runesmith-confluence/skills/feature-doc/SKILL.md  (2 occurrences)
  ...
```

### 3. Show plan

For each affected file, show the change preview:
- File path
- Old line(s)
- Proposed new line(s)
- Frontmatter implications (if the change touches `name:`, `description:`, or `model:`)

### 4. Get user consent

Ask: "Apply these