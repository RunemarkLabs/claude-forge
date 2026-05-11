# Substitution Tokens (canonical)

All templates and skill outputs use this exact set. No synonyms.

| Token | Meaning | Example |
|---|---|---|
| `{COMPANY}` | Organization display name | `Acme Corp` |
| `{SITE}` | Confluence/Jira site host | `acme.atlassian.net` |
| `{ATLASSIAN_API_URL}` | Full base URL | `https://acme.atlassian.net` |
| `{SPACE_KEY}` | Confluence space key | `OPS` |
| `{SPACE_ID}` | Confluence space numeric id | `12345678` |
| `{PROJECT_KEY}` | Jira project key | `PROJ` |
| `{PROJECT_ID}` | Jira project numeric id | `10042` |
| `{LEAD_ACCOUNT_ID}` | Atlassian accountId of project lead | `5b10a2844c20165700ede21g` |

## Forbidden synonyms

Do not introduce: `{ORG}`, `{ORGANIZATION}`, `{TEAM}`, `{COMPANY_NAME}`, `{TENANT}`, `{HOST}`, `{URL}`. Use the canonical token from the table.

## Page title tokens

When a page title needs the company name, embed it inline: `"{COMPANY} — Quick Start"`. Do not introduce `{TITLE_PREFIX}`.

## Replacement is case-sensitive

`{COMPANY}` is not the same as `{company}`. Templates use upper-snake-case inside braces only.
