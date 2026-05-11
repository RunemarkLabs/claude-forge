# Install

This marketplace ships four plugins: **core**, **atlassian**, **aiops**, **devtools**.

Two install paths: marketplace (recommended for Claude Code / Teams) and manual `.plugin` files (for Cowork or air-gapped setups).

## Path A — Marketplace (Claude Code / Teams)

In any Claude Code session:

```
/plugin marketplace add <owner>/<repo>
/plugin install core@bootstrap
/plugin install atlassian@bootstrap
/plugin install aiops@bootstrap
/plugin install devtools@bootstrap
```

`<owner>/<repo>` is the git remote where this marketplace lives (e.g. `https://github.com/your-org/your-repo` or `your-org/your-repo` shorthand).

For Claude Teams, an admin runs the same commands; plugins distribute to the org.

After install, restart your client (or reload plugins) and run `/core:setup`.

## Path B — Manual `.plugin` files (Cowork)

1. Download the four `.plugin` files from `dist/` in this repo (or from a release):
   - `core.plugin`
   - `atlassian.plugin`
   - `aiops.plugin`
   - `devtools.plugin`
2. Drag each file into the Cowork sidebar's plugin install area.
3. Restart the Cowork session.
4. Run `/core:setup`.

## Path C — Manual git clone (advanced)

Clone the repo somewhere your client can read it, then point your client at the plugin folders:

```
git clone https://github.com/<owner>/<repo>.git
# Cowork: copy plugins/* into your session's rpm/ directory
# Claude Code: copy plugins/* into ~/.claude/plugins/
```

## Configure credentials

After install, run `/core:setup`. You'll be prompted for:

| Key | Required | Where to get it |
|---|---|---|
| `ATLASSIAN_API_URL` | yes | Your Atlassian site URL (e.g. `https://acme.atlassian.net`) |
| `ATLASSIAN_API_EMAIL` | yes | Email of the account that minted the token |
| `ATLASSIAN_API_TOKEN` | yes | https://id.atlassian.com/manage-profile/security/api-tokens |
| `GITHUB_PAT` | for sync | https://github.com/settings/tokens (needs `repo` scope) |
| `PLUGIN_SOURCES` | optional | Comma-separated marketplace URLs |
| `ATLASSIAN_CONFLUENCE_SPACE_ID` | optional | Default Confluence space numeric id |
| `ATLASSIAN_JIRA_PROJECT_KEY` | optional | Default Jira project key |
| `ATLASSIAN_DEFAULT_ASSIGNEE_ACCOUNT_ID` | optional | Default ticket assignee accountId |
| `ATLASSIAN_BUG_SEVERITY_FIELD` | optional | Custom field id (e.g. `customfield_10001`) |

`.credentials` lives at the workspace root (gitignored). Override location with `BOOTSTRAP_WORKSPACE` env var.

## Verify install

```
/devtools:help
```

Should list all four plugins and 23 skills.

```
/atlassian:project-status
```

Read-only check that Jira credentials work.

## Set up a project workspace

After install, normalize the workspace structure:

```
/core:reallocate
```

Creates `_INBOX/`, `plans/`, `notes/`, `drafts/`, `tickets/`, and snapshot dirs. Idempotent — safe to re-run.

Then bootstrap the Claude Code subspace:

```
/devtools:bootstrap-cc
```

Creates `<project>.cc/` (your Claude Code monorepo head) with `CLAUDE.md`, `.claude/`, `comms/`, marker file. Optionally clones or creates repos for you (uses `GITHUB_PAT` from `.credentials` for private repos).

## Optional: enable Atlassian for the project

```
/atlassian:enable
```

Walks you through capturing your Jira project key, board id, and Confluence space id. Injects sprint workflow rules into both CLAUDE.md files. Deploys CC-side skills (sprint-pull, ticket-document, blocker-write, ticket-done) into `<project>.cc/.claude/skills/atlassian/`. Disable any time with `/atlassian:disable`.

## Bootstrap an AIOPS space

The space must already exist in Confluence (Cloud's v2 API does not expose space creation). Create it in the UI, then:

```
/aiops:bootstrap-aiops
```

You'll be asked for `{COMPANY}`, `{SITE}`, `{SPACE_KEY}`, `{SPACE_ID}`, `{PROJECT_KEY}`. The skill substitutes those into six template pages and publishes them.

## Troubleshooting

**`401` on every Atlassian call:** Email and token must match. The token's owning account email goes in `ATLASSIAN_API_EMAIL`.

**`400` on Confluence page create:** Body must be Confluence storage XHTML, not markdown. Skills handle this. If you're calling the API directly, see `plugins/core/lib/confluence-format.md`.

**`409` on Confluence page update:** GET the page first, read `version.number`, PUT with `number + 1`. Skills handle this automatically.

**`404` on `/rest/api/3/search`:** Deprecated. Use `POST /rest/api/3/search/jql`. Skills already do.

**Plugin not loading after manual install:** Restart your Claude client. For Cowork, end and restart the session.

**Severity custom field rejected:** Severity is rarely a default Jira field. Either map to `priority` or set `ATLASSIAN_BUG_SEVERITY_FIELD` in `.credentials`.
