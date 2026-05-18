---
name: plugin-builder
description: "Create Cowork plugins and install them into Claude Desktop. Replaces the old create-skill workflow. Use when the user says \"create a plugin\", \"new plugin\", \"add a skill\", \"make a plugin\", \"build a plugin\", \"I need a new skill\", or \"create a skill\". Also triggers on \"package this plugin\" or \"install this plugin\"."
compatibility: Requires Cowork desktop app environment.
---

# Plugin Builder

Create new Cowork plugins from scratch with full skill scaffolding.

Guided workflow: describe capability → generate skill structure → test → package → install.


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## Pre-Flight Checks

No pre-flight checks needed. This skill creates local plugin files.

## When to Use

Use for:
- Creating brand new plugins with custom skills
- Packaging custom workflows
- Building org-specific capabilities
- Creating skills beyond bootstrap plugins

Do **not** use for:
- Modifying existing plugins (edit directly)
- Installing plugins from catalog (use /core:install)
- Creating simple one-off scripts (use chat instead)

## Workflow

### 1. Describe the Plugin

Ask user:
- Plugin name (kebab-case, e.g., my-plugin)
- Description (one-line: what does it do?)
- Author/organization
- How many skills? (1-10 recommended)

### 2. For Each Skill

Ask:
- Skill name (kebab-case, e.g., my-skill)
- Description (when to use it)
- Trigger keywords (what words invoke it?)
- What should it do? (workflow description)

### 3. Generate Plugin Structure

Create directory in workspace:

```
/plugins/{plugin-name}/
  .claude-plugin/
    plugin.json
  skills/
    {skill-1}/
      SKILL.md
    {skill-2}/
      SKILL.md
  README.md
```

Generate:
- plugin.json with metadata
- SKILL.md files with guard rails pattern
- README.md with plugin overview

### 4. Review & Iterate

Show generated files in chat:
- Ask user to review skill workflows
- Adjust descriptions or triggers
- Refine guard rails if needed

### 5. Package Plugin

Zip plugin directory:
```
/plugins/{plugin-name}/ → /plugins/{plugin-name}.plugin
```

Create .plugin file (zipped archive) in workspace root.

### 6. Install Plugin

Instructions for user:
- Drag .plugin file into Cowork sidebar
- Restart Claude if needed
- Skills now available as /plugin-name:skill-name

Report:

```
✓ Plugin created and packaged

Plugin: {plugin-name}
Skills: {skill-1}, {skill-2}, ...

Package: {plugin-name}.plugin
Location: /plugins/

To install:
1. Drag {plugin-name}.plugin into Cowork sidebar
2. Restart Claude
3. Try: /{plugin-name}:help
```

## Guard Rails

- [ ] Plugin name is unique
- [ ] All skills have descriptions and triggers
- [ ] Guard rails pattern applied to all skills
- [ ] plugin.json is valid JSON
- [ ] Skills reviewed and approved
- [ ] .plugin file is created and packaged
- [ ] Installation instructions provided

## Error Cases

**Invalid plugin name:** "Use kebab-case (lowercase, hyphens). No spaces or special characters."

**Duplicate plugin:** "Plugin name already exists. Choose a different name."

**Invalid SKILL.md:** "Each skill needs name, description, and workflow."

**Packaging failed:** "Could not create .plugin file. Check file permissions."
