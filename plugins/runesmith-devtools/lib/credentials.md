# Credentials Resolution

How every skill in this marketplace finds and reads `.credentials`.

## File location

`${WORKSPACE_ROOT}/.credentials`

`WORKSPACE_ROOT` resolution order:
1. `BOOTSTRAP_WORKSPACE` env var, if set
2. Cwd of the running session
3. Project root if Claude Code (`~/.claude/projects/<id>/` parent)

If none of the above contain `.credentials`, prompt user to run `/core:setup`.

## Required keys

```
ATLASSIAN_API_URL=https://<site>.atlassian.net
ATLASSIAN_API_EMAIL=<account email>
ATLASSIAN_API_TOKEN=<api token from id.atlassian.com>
GITHUB_PAT=<github personal access token>
```

## Optional keys

```
PLUGIN_SOURCES=<comma-separated marketplace URLs>
ATLASSIAN_CONFLUENCE_SPACE_ID=<numeric id, default project space>
ATLASSIAN_JIRA_PROJECT_KEY=<default project key>
ATLASSIAN_DEFAULT_ASSIGNEE_ACCOUNT_ID=<accountId>
ATLASSIAN_BUG_SEVERITY_FIELD=<custom field id, e.g. customfield_10001>
```

## Auth header

Atlassian REST API expects HTTP Basic with `email:token` base64-encoded:

```
Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_API_EMAIL" "$ATLASSIAN_API_TOKEN" | base64 -w0)
Accept: application/json
Content-Type: application/json
```

## Rules

- Never echo credential values in chat. Mask after first 4 chars.
- Never write credentials to logs, drafts, or commits.
- `.credentials` must be gitignored at repo root.
- On any 401/403 from Atlassian, re-read `.credentials` once, then surface "Run `/core:setup`."
