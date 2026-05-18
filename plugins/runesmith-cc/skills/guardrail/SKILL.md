---
name: guardrail
description: "Install, verify, or uninstall the CC project-boundary guardrail with a single command. Copies a self-contained PowerShell (Windows) or bash (macOS/Linux) installer to the workspace root that handles the entire user-level setup — writes ~/.claude/settings.json permission block, hook scripts, runs synthetic verification. Constrains every Claude Code session on the machine to its launch project's root. Run once per machine. Use when the user says \"install the guardrail\", \"set up CC boundaries\", \"lock CC to project root\", \"guardrail install\", \"guardrail verify\", \"uninstall the guardrail\"."
compatibility: Requires Cowork desktop app environment.
---

# CC Project-Boundary Guardrail (one-shot installer)

The guardrail is **user-level config** (`~/.claude/settings.json` permission rules + `PreToolUse` hook). Cowork's sandbox can't write to user-home. CC's own session can't either (its own permissions block the install of its own boundary — chicken-and-egg). So this skill takes a different approach: **copy a self-contained installer script to the workspace root and tell the user to run it once.**

One user action: run `.\install-guardrail.ps1` (Windows) or `./install-guardrail.sh` (macOS/Linux). The script does everything.

## References

- `templates/install-guardrail.ps1` — full self-contained Windows installer
- `templates/install-guardrail.sh` — full self-contained Unix installer

## What the installer does

When the user runs the copied installer:

1. **Detects environment** — Git Bash + jq on Windows (chooses hook variant), or `jq` on Unix (required).
2. **Creates `~/.claude/hooks/`** if absent.
3. **Writes the hook script** — `enforce-project-boundary.sh` (and `.ps1` on Windows). The hook body is embedded in the installer; no extra files to copy.
4. **Reads existing `~/.claude/settings.json`** if present. Fails loudly on invalid JSON; never overwrites unreadable files.
5. **Merges the guardrail block** — marker key, `permissions.defaultMode: "dontAsk"`, curated allow/deny arrays (union with any user-managed entries), `hooks.PreToolUse` matcher. User-managed keys outside the guardrail block survive.
6. **Synthetic-tests the hook** — pipes one allow case and one deny case through, confirms exit codes (0 / 2).
7. **Reports** — paths, status, known residual risks, restart-CC reminder.

## What this skill does (Cowork-side, one shot)

When invoked from Cowork, this skill:

1. **Comms check on entry** (per `lib/comms-check.md`).
2. **OS detection** — structured prompt: Windows / macOS / Linux / "auto-detect both."
3. **Confirms action** — structured prompt: install / verify / uninstall / cancel.
4. **Copies the appropriate installer** from this skill's `templates/` folder to the user's workspace root:
   - Windows: `install-guardrail.ps1`
   - macOS/Linux: `install-guardrail.sh` (with `chmod +x`)
   - "Both": copies both files
5. **Reports the single command** the user runs to complete the action.

That's it. No multi-step copy-paste. No "where is jq." No JSON merge by hand.

## Action mapping

The installer script accepts a mode argument:

| User intent | PowerShell command | Bash command |
|---|---|---|
| Install | `.\install-guardrail.ps1` | `./install-guardrail.sh` |
| Verify | `.\install-guardrail.ps1 -Mode verify` | `./install-guardrail.sh verify` |
| Uninstall | `.\install-guardrail.ps1 -Mode uninstall` | `./install-guardrail.sh uninstall` |

This skill copies the installer once. The user runs whichever mode they need.

## Pre-flight checks

### 0. Comms check (always first)

See `lib/comms-check.md`.

### 1. Confirm action (structured prompt)

Single-pick: `install` / `verify` / `uninstall` / `cancel`.

### 2. Detect target OS (structured prompt)

Single-pick: `Windows` / `macOS` / `Linux` / `copy both (Windows + Unix)`.

Defaults to the OS the user's session indicates if known. If the user is dogfooding across machines, "copy both" puts the installer in workspace root for either platform.

### 3. Pick destination (structured prompt, optional)

Default: workspace root. Alternative: `_INBOX/` if the workspace's root keep-list is strict and the user prefers not to track temp installers there. The installer is gitignored by default if the workspace has a RuneSmith-canonical `.gitignore` (it matches `install-guardrail.*`).

## Install flow

1. Copy `templates/install-guardrail.ps1` and/or `templates/install-guardrail.sh` to the chosen destination (workspace root by default).
2. On Unix, `chmod +x install-guardrail.sh`.
3. Report:
   ```
   Installer copied:
     Windows: <workspace>/install-guardrail.ps1
     Unix:    <workspace>/install-guardrail.sh

   Next: run the installer.

   PowerShell:
     cd <workspace>
     .\install-guardrail.ps1

   Bash:
     cd <workspace>
     ./install-guardrail.sh

   Once it completes successfully, restart any open Claude Code sessions.
   ```

No structured-prompt consent for the copy step itself — the consent for the install action already happened in step 1 of pre-flight. Copying a file to workspace root is trivially reversible and doesn't touch user-home.

## Verify flow

Same copy step. User runs the installer with `verify` / `-Mode verify`. Skill reports the verify command:

```
.\install-guardrail.ps1 -Mode verify
./install-guardrail.sh verify
```

## Uninstall flow

Same copy step. User runs the installer with `uninstall` / `-Mode uninstall`:

```
.\install-guardrail.ps1 -Mode uninstall
./install-guardrail.sh uninstall
```

The installer removes its marker keys from settings.json, removes the hook scripts. Does NOT strip permission rule entries by content (the user may have added their own copies of the same rules). Prints a warning and lists what stayed for manual review.

## Known residual risks (documented, not solved by this skill)

- **Subagents bypass the hook and permission rules** (platform bugs #27661, #23983). Layer 1 advisory rules in CLAUDE.md are the only protection inside a subagent.
- **Bash on Windows is unsandboxed.** Substring matchers in the hook are evadeable via PowerShell pipes, indirect invocation, shell escaping. Hook catches accidents, not adversarial Bash.
- **MCP tool calls are not boundary-aware.** Any installed MCP can be called from any project regardless of which project enabled the workflow. Follow-up plan tracked separately.

## Why this design (and what changed)

Earlier versions tried to install the guardrail from inside Claude Code. That failed because CC's own permission system blocks writes to `~/.claude/` from a CC session (it's enforcing the boundary it doesn't yet have, against itself). The previous CC-side install skill (`cc-skill-templates/guardrail/skill-template.md`) is retained for reference but no longer the recommended path — it falls back to printing manual install commands, which is the same content but multi-step.

The one-shot installer eliminates the multi-step manual path. User opens PowerShell or Terminal, runs one command, done.

## Output reporting (all flows)

End every flow with a single structured summary. No prose preamble.

```
Guardrail action:  install | verify | uninstall
Installer copied:  <workspace>/install-guardrail.ps1
                   <workspace>/install-guardrail.sh
Command to run:    .\install-guardrail.ps1
                   ./install-guardrail.sh

Next step: open PowerShell / Terminal, cd to the workspace, run the
command above. Then restart any open Claude Code sessions.
```
