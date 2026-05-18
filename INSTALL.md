# Install

The RuneSmith marketplace ships **eight plugins**:

| Plugin | Required | Purpose |
|---|---|---|
| `runesmith-core` | yes | Credentials, plugin management, chat-first planning. Foundation. |
| `runesmith-workspace` | yes | Canonical workspace structure (`_INBOX/`, `plans/`, snapshots). |
| `runesmith-cc` | yes | `{PROJECT}.cc/` Claude Code monorepo head + project-boundary guardrail. |
| `runesmith-jira` | optional | Jira ticket and project workflows. |
| `runesmith-confluence` | optional | Confluence page authoring with markdown → storage XHTML conversion. |
| `runesmith-sprint` | optional | Atlassian sprint workflow + Cowork ↔ CC interconnect. |
| `runesmith-aiops` | optional | Bootstrap an AI Operations Confluence space from templates. |
| `runesmith-devtools` | optional | Developer helpers (skill scaffold, tech-debt, skill-updater). |

Three install paths. Pick one based on your client.

## Path A — Marketplace add (Claude Code CLI users)

```
/plugin marketplace add runemarklabs/runesmith
/plugin install runesmith-core@runesmith
/plugin install runesmith-workspace@runesmith
/plugin install runesmith-cc@runesmith
/plugin install runesmith-jira@runesmith
/plugin install runesmith-confluence@runesmith
/plugin install runesmith-sprint@runesmith
/plugin install runesmith-aiops@runesmith
/plugin install runesmith-devtools@runesmith
```

This works for Claude Code CLI sessions. After install, restart the CLI and run `/runesmith-core:setup` to populate `.credentials`.

## Path B — Manual .plugin files (Cowork desktop)

`.plugin` zips aren't committed; build them on demand:

```
python scripts/build.py        # cross-platform; recommended on Windows
# or:
bash scripts/build.sh          # macOS / Linux
```

Produces `runesmith-*.plugin` files in `./dist/` (gitignored). Custom output dir:

```
python scripts/build.py /path/to/output
```

Then in Cowork desktop:

1. **Customize** in the left sidebar.
2. Drag the eight `.plugin` files from `./dist/` into the upload area.
3. Restart Cowork.
4. Run `/runesmith-core:setup`.

Install `runesmith-core` first — others depend on its lib refs.

## Path C — Cowork Team / Enterprise org-synced marketplace

Cowork's GitHub-synced marketplaces require **private or internal** repos — public repos are not allowed for org marketplaces. Two options:

### C.1 — Mirror to a private repo in your org

```bash
git clone --bare https://github.com/runemarklabs/runesmith.git
cd runesmith.git
git push --mirror https://github.com/<your-org>/<your-private-repo>.git
```

Then in your org admin:

1. **Organization settings → Plugins → Add plugin → GitHub source.**
2. Enter `<your-org>/<your-private-repo>`.
3. Click "Update" to trigger the initial sync.

Make sure the Cowork GitHub App is installed on the private repo. Without that, the sync 404s.

### C.2 — Managed-settings deployment (Enterprise)

Admins on Enterprise plans can ship the marketplace contents as **managed settings**. See Cowork's admin docs for managed-settings file delivery. The marketplace doesn't directly produce managed-settings JSON; use the user-level settings layout (from `runesmith-cc:guardrail`) as a template.

## Configure credentials

Run `/runesmith-core:setup` after install. The skill walks structured prompts for:

| Key | Required for | Where to get it |
|---|---|---|
| `ATLASSIAN_API_URL` | Atlassian skills | Your Atlassian site URL (e.g. `https://acme.atlassian.net`) |
| `ATLASSIAN_API_EMAIL` | Atlassian skills | Email of the account that minted the token |
| `ATLASSIAN_API_TOKEN` | Atlassian skills | https://id.atlassian.com/manage-profile/security/api-tokens |
| `GITHUB_PAT` | runesmith-cc clone/create | https://github.com/settings/personal-access-tokens (fine-grained PAT with `Contents: Read/Write` on target repos) |
| `ATLASSIAN_CONFLUENCE_SPACE_ID` | Confluence skills | Settings → Space Settings → Space details |
| `ATLASSIAN_JIRA_PROJECT_KEY` | Jira / sprint skills | The short uppercase identifier (e.g. `ENG`) |
| `ATLASSIAN_JIRA_BOARD_ID` | sprint skills | Numeric board id from the board URL |
| `ATLASSIAN_DEFAULT_ASSIGNEE_ACCOUNT_ID` | sprint:enable | Your accountId — use `atlassianUserInfo` MCP call |
| `ATLASSIAN_BUG_SEVERITY_FIELD` | bug-report (custom) | Custom field id (e.g. `customfield_10001`) if your tenant uses one |
| `PLUGIN_SOURCES` | optional | Comma-separated additional marketplace URLs |

`.credentials` lives at workspace root (gitignored). Override location with `BOOTSTRAP_WORKSPACE` env var.

`.credentials.example` in this repo lists every key with placeholder values. Copy it and fill in.

## Install the project-boundary guardrail (one-time per machine)

The guardrail installs at user level (`~/.claude/settings.json` + `~/.claude/hooks/`). It must run inside **Claude Code**, not Cowork — Cowork's sandbox can't write to `~/.claude/`.

After a workspace has been bootstrapped (`/runesmith-cc:bootstrap-cc`), bootstrap-cc deploys the CC-side guardrail skill template into `{PROJECT}.cc/.claude/skills/guardrail/`. Launch Claude Code in any CC-headed repo and run:

```
/guardrail install
```

The skill writes `~/.claude/settings.json` block and the hook script at `~/.claude/hooks/enforce-project-boundary.sh` (PowerShell shim on Windows). Every Claude Code session on this machine is then constrained to its launch project's root.

For the Cowork-side walkthrough (paths + commands for your OS, no install):

```
/runesmith-cc:guardrail
```

See `docs/howto/install-guardrail.md` for details and residual risks.

## Set up a project workspace

After install, in any project folder:

```
/runesmith-workspace:reallocate
```

Lays down the canonical structure (`_INBOX/`, `plans/active/`, `plans/archive/`, `notes/`, `drafts/`, `research/`, `source-docs/`, `archive/`). Writes `STRUCTURE.md` and the marker-bounded sections in `CLAUDE.md`. Surfaces a Project Instructions text block for you to paste into Cowork's UI.

Then:

```
/runesmith-cc:bootstrap-cc
```

Creates the `{PROJECT}.cc/` Claude Code monorepo head with `CLAUDE.md`, `.claude/` scaffolding, `comms/`, marker file, and the deployed `code-tech-debt` CC-side skill. Optionally clones existing GitHub repos or creates new ones via PAT auth.

See `docs/howto/new-workspace.md` for the full walkthrough.

## Optional: enable Atlassian for the project

```
/runesmith-sprint:enable
```

Wires Jira + Confluence into the workspace. Walks you through capturing the Jira project key, board id, Confluence space id. Appends the `<!-- runesmith:atlassian-start/end -->` block to both `CLAUDE.md` files. Surfaces a Project Instructions supplement to paste. Drops `.atlassian-enabled` at workspace root.

Disable any time with `/runesmith-sprint:disable`.

See `docs/howto/enable-atlassian.md` for the full walkthrough.

## Optional: bootstrap an AIOPS Confluence space

The space must already exist in Confluence (Cloud's v2 API doesn't expose space creation). Create it in the UI, then:

```
/runesmith-aiops:bootstrap-aiops
```

Structured prompts for `{COMPANY}`, `{SITE}`, `{SPACE_KEY}`, `{SPACE_ID}`, `{PROJECT_KEY}`. The skill substitutes those tokens into six template pages (Quick Start, Full Integration, Architecture, Best Practices, FAQ, Reference) and publishes them.

## Verify install

```
/runesmith-devtools:help
```

Lists every installed plugin and its skills with natural-language triggers.

```
/runesmith-jira:project-status
```

Read-only sanity check that Atlassian credentials work (if you set them).

## Troubleshooting

**`401` on every Atlassian call.** Email and token must match the account that minted the token. The token's owning account email goes in `ATLASSIAN_API_EMAIL`.

**`400` on Confluence page create.** Body must be Confluence storage XHTML, not markdown. The marketplace's `runesmith-confluence` skills handle conversion via `scripts/md-to-storage.py`. If you're calling the API directly, run your markdown through that script first.

**`409` on Confluence page update.** Version conflict — GET the page first, read `version.number`, PUT with `number + 1`. Skills handle this automatically.

**`404` on `/rest/api/3/search`.** Deprecated endpoint. Current Cloud API is `POST /rest/api/3/search/jql`. Skills already use it. If you hit this, you have an outdated plugin — rebuild from `scripts/build.py` and reinstall.

**Plugin not loading after manual install.** Restart Cowork (full quit, not reload). For Claude Code CLI, restart the CLI.

**`/plugin marketplace add` returns "Validation failed".** Two common causes:
1. `plugin.json` contains a `dependencies` field — Cowork's loader silently rejects plugins with this. The marketplace stripped it in v0.6.1+; rebuild from current.
2. Angle-bracket placeholders (`<word>`) in SKILL.md frontmatter or plugin.json descriptions. Use `{WORD}` curly braces. `scripts/audit.py` catches this.

**Severity custom field rejected on `runesmith-jira:bug-report`.** Severity is rarely a default Jira field. Either map to `priority` or set `ATLASSIAN_BUG_SEVERITY_FIELD` in `.credentials` to your tenant's custom field id.

**Slash commands return "Unknown command" after install.** Restart your client. Plugins register at session start. If they still don't resolve, check the plugin folder's `.claude-plugin/plugin.json` — name must match the folder name; description must not be truncated mid-sentence.
