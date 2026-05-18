---
name: setup
description: "Configure credentials, API endpoints, and plugin sources. Use when \"set up\", \"configure\", \"add credentials\", or need to initialize the workspace."
compatibility: Requires Cowork desktop app environment.
---

# Setup

Configure workspace credentials and API endpoints for all skills in this marketplace.

## References

- `lib/credentials.md` — file location, key list, auth header
- `lib/install-paths.md` — runtime install locations
- `lib/user-prompts.md` — structured-input requirement for any user prompt


## User input rules

This skill follows the marketplace-wide user-prompt standard in `lib/user-prompts.md`. Every user prompt MUST use the host client's structured input UI (single-pick, multi-pick, or text-input form). Never freeform plain-text yes/no questions. The only exception is the consent-trigger gate documented in `lib/consent.md`, which waits for user-initiated phrases like "make the ticket".

## When to Use

Use for:
- First-time workspace setup
- Adding or updating API credentials
- Verifying current credential health

Do not use for:
- Project-specific config (edit CLAUDE.md directly)
- Installing plugins (use `/core:install`)

## Workflow

### 1. Resolve `.credentials` path

Per `credentials.md`:
1. Honor `BOOTSTRAP_WORKSPACE` env var if set.
2. Otherwise look for `.credentials` in cwd, walking up to repo root.
3. If not found, ask user: "Workspace root path?" and create file there.

### 2. Read existing keys (if any)

Mask values after first 4 chars when reporting. Categorize:
- Set: ATLASSIAN_API_URL, ATLASSIAN_API_EMAIL, ATLASSIAN_API_TOKEN
- Set: GITHUB_PAT
- Set: optional keys (PLUGIN_SOURCES, ATLASSIAN_CONFLUENCE_SPACE_ID, ATLASSIAN_JIRA_PROJECT_KEY, ATLASSIAN_DEFAULT_ASSIGNEE_ACCOUNT_ID, ATLASSIAN_BUG_SEVERITY_FIELD)

### 3. Collect missing values

Ask one prompt per missing required key. For each, link to the source:
- API token: <https://id.atlassian.com/manage-profile/security/api-tokens>
- GitHub PAT: <https://github.com/settings/tokens> (needs `repo` scope)

Optional keys: ask whether to set, default skip.

### 4. Confirm before write

Show user the planned `.credentials` content with all values masked. Ask:
"Save these credentials to <path>?"

Wait for explicit yes.

### 5. Write file

Atomic write (temp file + rename). Mode `0600`. Verify `.credentials` is in `.gitignore`; if not, append.

### 6. Verify

Run health checks:
- Atlassian Confluence: `GET {ATLASSIAN_API_URL}/wiki/api/v2/spaces?limit=1` — expect 200.
- Atlassian Jira: `GET {ATLASSIAN_API_URL}/rest/api/3/myself` — expect 200, returns accountId.
- GitHub: `GET https://api.github.com/user` with PAT — expect 200.
- Plugin sources (optional): fetch URL, expect HTTP 200 + valid JSON.

Report which pass / fail.

## Output

```
✓ Credentials saved to <path>

Atlassian Confluence: ok
Atlassian Jira: ok (you = <displayName>)
GitHub: ok (you = <login>)
Plugin sources: ok | not configured

Try /core:install or /atlassian:project-status.
```

## Guard Rails

- [ ] `.credentials` path resolved per `credentials.md`
- [ ] All required keys present after run
- [ ] User explicitly approves before write
- [ ] File mode 0600
- [ ] `.gitignore` contains `.credentials`
- [ ] Values masked in chat output
- [ ] Health checks executed and reported

## Error Cases

**401 on Jira/Confluence:** "Email/token mismatch. Use the email of the account that minted the token."
**403 GitHub:** "PAT missing `repo` scope."
**Plugin sources unreachable:** Warn but don't block; mark as optional.
**`.gitignore` not present:** Create one with `.credentials` entry, ask before committing.
