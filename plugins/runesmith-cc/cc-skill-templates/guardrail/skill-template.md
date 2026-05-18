---
name: guardrail
description: "Install, uninstall, or verify the CC project-boundary guardrail at user level. Writes ~/.claude/settings.json with default-deny permissions and a PreToolUse hook that blocks cross-project filesystem reads (the credential-leak class of bug). Run once per machine from any CC session. Use when the user says \"install the guardrail\", \"set up CC boundaries\", \"lock CC to project root\", \"guardrail install\", \"guardrail verify\", \"uninstall the guardrail\"."
---

# CC Project-Boundary Guardrail (install skill)

User-level install for the CC project-boundary guardrail. This skill runs INSIDE Claude Code because it needs to write outside the project workspace (`~/.claude/settings.json` and `~/.claude/hooks/`) — Cowork's sandbox can't reach those paths.

Layer 2 of the two-layer model. Layer 1 (the behavioral refusal rules in CLAUDE.md) is already deployed by bootstrap-cc; you're here to install the harness enforcement.

## References

- `templates/user-settings-block.json` — the JSON block this skill merges into the user's `~/.claude/settings.json`.
- `templates/enforce-project-boundary.sh` — bash hook script (primary).
- `templates/enforce-project-boundary.ps1` — PowerShell shim (Windows without Git Bash).

## What this enforces

**File access boundary** — user-level permission rules with `defaultMode: "dontAsk"` and project-relative `Read(/**)` / `Edit(/**)` / `Write(/**)` allow rules. Permission system auto-denies any file op outside the active project's root.

**Categorical secret deny** — `Read(//**/.credentials*)`, `Read(//**/.env*)`, `Read(//**/id_rsa*)`, `Read(//**/*.key)`, `Read(//**/*.pem)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)`. Wins over any allow rule (deny-first precedence).

**Bash exfil deny** — `Bash(curl *)`, `Bash(wget *)`, `Bash(nc *)`, `Bash(ssh *)`, `Bash(scp *)`. Best-effort against accidents.

**Bash file-access hook** — for cases the permission system can't see (Python/Node scripts that open files), `PreToolUse` hook inspects Bash commands and blocks reads of known sensitive paths or paths outside `$CLAUDE_PROJECT_DIR`.

## Known residuals

- **Subagents bypass the hook and permission rules** (platform bugs #27661, #23983). Layer 1 advisory rules are the only protection inside a subagent.
- **Bash on Windows is unsandboxed.** Substring matchers evadeable via PowerShell pipes, shell escaping. Hook catches accidents.
- **MCP tool calls are not boundary-aware.** Tracked separately.

## Pre-flight checks

### 1. Confirm CC has terminal access

This skill writes outside the project. CC sessions launched in CLI mode have this. CC sessions inside other harnesses (Claude Desktop's Code tab, restricted environments) may not. If terminal write capabilities are absent, the skill prints the install commands for the user to run manually instead.

### 2. OS detection

Use `uname -s` (macOS/Linux) or `$env:OS` (Windows). Sets:
- User settings file path: `~/.claude/settings.json` on macOS/Linux, `%USERPROFILE%\.claude\settings.json` on Windows.
- Hook script extension: `.sh` with bash on macOS/Linux, `.sh` via Git Bash if available else `.ps1` on Windows.
- jq availability: required for bash variant. If absent on Linux/macOS, install with `brew install jq` (macOS), `apt install jq` (Debian), `choco install jq` (Windows).

### 3. Confirm action

Structured prompt — single-pick: `install` / `uninstall` / `verify` / `cancel`. Never proceed without an explicit selection.

For `install`: if the settings file already contains the marker key `_runesmith_guardrail_marker`, prompt: `update existing install` / `reinstall fresh` / `cancel`.

## Install flow

### Step 1 — Resolve target settings file

```
macOS/Linux:  ~/.claude/settings.json
Windows:      %USERPROFILE%\.claude\settings.json
```

If the file doesn't exist, create it as `{}`. If it exists, parse as JSON. Fail loudly on invalid JSON; never overwrite an unreadable file.

### Step 2 — Merge the guardrail block

The block lives under marker key `_runesmith_guardrail_marker` (UUID generated at install time). A parallel `_runesmith_guardrail_keys` array lists every key path the skill added under `permissions` and `hooks` so uninstall removes only what it owns.

Merge semantics:
- `permissions.defaultMode` — set to `"dontAsk"`. If the user already has a different value, prompt: `keep yours` / `use dontAsk` / `cancel`.
- `permissions.allow` — array union. Add the curated allow rules, dedupe.
- `permissions.deny` — array union. Add the curated deny rules, dedupe.
- `hooks.PreToolUse` — array append. Add the boundary hook matcher entry.

See `templates/user-settings-block.json` for the literal block.

### Step 3 — Write the hook script

```
macOS/Linux:  ~/.claude/hooks/enforce-project-boundary.sh
Windows:      %USERPROFILE%\.claude\hooks\enforce-project-boundary.sh (Git Bash present)
              %USERPROFILE%\.claude\hooks\enforce-project-boundary.ps1 (no Git Bash)
```

Copy from `templates/enforce-project-boundary.sh` and `templates/enforce-project-boundary.ps1`. `chmod +x` on Unix.

### Step 4 — Verify

Pipe a synthetic event into the hook (allow case + deny case). Confirm exit codes match (2 and 0). If either fails, abort and roll back the settings merge.

### Step 5 — Report

Single structured summary: settings file path, hook script path, what's covered, residual risks. Tell the user to restart any open Claude Code sessions for the new settings to load.

## Uninstall flow

### Step 1 — Locate marker

Parse user settings file. Find `_runesmith_guardrail_marker` and `_runesmith_guardrail_keys`. If absent, report nothing to remove and exit clean.

### Step 2 — Remove owned entries

Walk `_runesmith_guardrail_keys`. For each key path, remove only the value the skill added. User-managed keys in `permissions.allow` etc. survive.

### Step 3 — Remove marker

Delete `_runesmith_guardrail_marker` and `_runesmith_guardrail_keys`.

### Step 4 — Remove hook script

Delete `enforce-project-boundary.sh` and `enforce-project-boundary.ps1` from `~/.claude/hooks/`.

### Step 5 — Report

Confirm what was removed. Warn that CC sessions no longer have a project boundary.

## Verify flow

### Step 1 — Check marker

Confirm `_runesmith_guardrail_marker` exists in user settings. If absent, report "not installed."

### Step 2 — Smoke-test hook

Pipe synthetic events into the hook (allow + deny). Confirm exit codes are 0 and 2.

### Step 3 — Confirm settings shape

Parse settings file. Confirm:
- `permissions.defaultMode === "dontAsk"`
- All entries in the install block's `permissions.allow` are present
- All entries in the install block's `permissions.deny` are present
- `hooks.PreToolUse` includes the boundary matcher

### Step 4 — Report

Structured report. Each check pass/fail. If any fail, suggest `install` to repair.

## Output reporting (all flows)

End every flow with a single structured summary block. No prose preamble. No questions about whether to proceed — those happened in the structured-prompt step.

```
Guardrail action: install | uninstall | verify
Settings file:    /Users/<user>/.claude/settings.json
Hook script:      /Users/<user>/.claude/hooks/enforce-project-boundary.sh
Status:           OK | FAIL
Details:          ...
Next step:        Restart any open Claude Code sessions.
```
