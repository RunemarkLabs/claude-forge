---
name: guardrail
description: >
  Explain the CC project-boundary guardrail and point the user to the actual install path. The install runs inside Claude Code (not Cowork) because it writes to ~/.claude/ which is outside Cowork's sandbox. Use when the user says "install the guardrail", "set up CC boundaries", "lock CC to project root", "guardrail install", "guardrail verify", "uninstall the guardrail" from a Cowork session.
---

# CC Project-Boundary Guardrail (Cowork pointer)

The actual install runs inside **Claude Code**, not Cowork. Cowork's sandbox doesn't have write access to `~/.claude/settings.json` or `~/.claude/hooks/` — those live outside the mounted workspace. This skill exists to explain the design and point the user to the CC-side install path.

## What to do (the user-facing instructions this skill emits)

### Prerequisites

- Workspace has been bootstrapped with `/runesmith-cc:bootstrap-cc` (deploys the CC-side guardrail skill template into `{PROJECT}.cc/.claude/skills/guardrail/`).
- A code repo exists under `{PROJECT}.cc/<repo>/`.

### Install (one-time per machine)

1. **Open Claude Code** in any CC-headed repo under `{PROJECT}.cc/<repo>/`. From the terminal:
   ```
   cd ~/Projects/<your-project>/<your-project>.cc/<repo>/
   claude
   ```
   Or use Claude Desktop's Code tab pointed at the same folder.

2. **Inside the CC session, run:**
   ```
   /guardrail install
   ```

3. **Confirm via the structured prompt.** CC writes:
   - `~/.claude/settings.json` block (default-deny + curated allow/deny + PreToolUse hook entry)
   - `~/.claude/hooks/enforce-project-boundary.sh` (and `.ps1` on Windows without Git Bash)

4. **Restart Cowork and any open CC sessions** for the new permissions to load.

### Verify

From inside CC:
```
/guardrail verify
```

Confirms the install marker, smoke-tests the hook against synthetic allow + deny events, validates the permission rules are present.

### Uninstall

From inside CC:
```
/guardrail uninstall
```

Removes only the entries the skill added. User-managed keys in `~/.claude/settings.json` survive.

## Why not Cowork

Three reasons:

1. **Cowork sandbox.** Cowork mounts the project workspace folder and a small set of system paths. `~/.claude/` is not in that set. Cowork can read scripts that ship with the plugin (the templates) but cannot write user-home settings.
2. **CC owns the consumer side.** The settings the guardrail installs are read by CC. CC is the natural installer for its own config — it has the right permissions and runs in the right context.
3. **One install, every project.** The guardrail is user-level. Run it once from any CC session and every CC session on the machine inherits the boundary thereafter.

If the install runs from a Sapient-mirror workspace, the marker key is `_runesmith_guardrail_marker` regardless of marketplace branding — the key name is stable across forks so uninstall always finds what install wrote.

## What this skill does

This skill produces an instructional report:
- Detects the OS (macOS / Linux / Windows) and lists target paths the install will touch.
- Confirms whether a `{PROJECT}.cc/<repo>/` exists in the current workspace (so the user has somewhere to launch CC from).
- Surfaces the exact commands above with paths substituted for the current host.
- Optionally launches Claude Code via subprocess for the user (if `claude` is on PATH) — structured prompt for consent first.

This skill does NOT:
- Write to `~/.claude/`.
- Mutate any user-home file.
- Bypass the sandbox.

The actual install logic lives in the CC-side skill at `plugins/runesmith-cc/cc-skill-templates/guardrail/skill-template.md` (deployed by bootstrap-cc as `{PROJECT}.cc/.claude/skills/guardrail/SKILL.md`).
