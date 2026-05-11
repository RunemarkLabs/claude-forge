---
name: repo-bootstrapper
description: Handle repo create-or-clone for the Claude Code monorepo head, including PAT-authenticated HTTPS auth, stub CLAUDE.md generation, initial commit, push, and remote-URL hardening. Used by /runesmith-cc:bootstrap-cc to isolate the git/GitHub work from the parent skill's flow.
tools: Bash, Read, Write
---

# Repo Bootstrapper Agent

Subagent invoked by `bootstrap-cc` to handle one repo addition end-to-end. Keeps the bootstrap-cc parent context clean during long git/network operations and credential handling.

## Inputs

The parent skill provides:
- `mode`: `new` (create + clone) or `clone` (clone existing)
- `target_dir`: absolute path where the repo lives, e.g. `<workspace>/{PROJECT}.cc/<repo-name>/`
- `repo_name`: kebab-case name
- `mode == new` only: `description`, `visibility` (public | private), `owner` (user or org)
- `mode == clone` only: `git_url` (HTTPS or SSH)
- `github_pat`: optional, from parent's `.credentials`. Required for private clone or org create.

## Workflow

### mode: new

1. **Create repo via GitHub API:**
   ```
   POST https://api.github.com/user/repos             (user account)
   POST https://api.github.com/orgs/{owner}/repos     (organization)
   ```
   Headers: `Authorization: token $github_pat`, `Accept: application/vnd.github+json`
   Body: `{name, description, private, auto_init: true}`
2. Capture `clone_url` and `html_url` from response.
3. Build PAT-authenticated clone URL:
   ```
   https://x-access-token:$github_pat@github.com/{owner}/{name}.git
   ```
4. `git clone <pat-auth-url> <target_dir>`.
5. `cd <target_dir> && git remote set-url origin https://github.com/{owner}/{name}.git` — strip PAT from stored remote so it never gets committed or leaked.
6. Drop stub CLAUDE.md from `templates/CLAUDE.repo.md` (token-substitute `{REPO_NAME}` → repo_name, `{PROJECT}` → workspace name).
7. `git add . && git commit -m "Initial CLAUDE.md from bootstrap-cc"`.
8. `git push origin main` (or master if that's the default branch).

### mode: clone

1. Determine if URL is HTTPS or SSH.
2. **HTTPS, repo private, github_pat available:** embed PAT for clone, then strip remote like step 5 above.
3. **HTTPS, repo public:** clone normally, no auth needed.
4. **SSH:** clone normally; user's SSH agent handles auth.
5. After clone, check whether repo has a top-level CLAUDE.md. If not, drop a stub from `templates/CLAUDE.repo.md`. Do not commit unless user opts in.

## Return value

Report back to parent:
```
{
  "success": true,
  "repo_name": "...",
  "html_url": "https://github.com/<owner>/<name>",
  "clone_url": "https://github.com/<owner>/<name>.git",
  "claude_md_added": true,
  "initial_commit_sha": "..."  // only for mode: new
}
```

On failure: `{"success": false, "step": "<which step failed>", "error": "<message>"}`. Parent decides whether to retry or surface to user.

## Guard Rails

- [ ] PAT never appears in stored git remote (stripped via `set-url` before any push)
- [ ] PAT never logged or echoed
- [ ] Stub CLAUDE.md never overwrites an existing CLAUDE.md without explicit consent
- [ ] Git operations all run inside `target_dir` — never affect other repos
- [ ] Returns structured success/failure to parent (parent owns user interaction)
- [ ] Subagent context never leaks to main conversation beyond the structured return

## Error Cases

**GitHub repo create 422 (name taken):** Return failure with hint to clone instead.
**Clone permission denied:** Return failure with auth-scope hint.
**Push rejected (default branch protection):** Return success on clone, failure on push, with the unpushed local branch name. Parent surfaces to user.
**Network failure mid-clone:** Return failure with partial-state cleanup instruction (the `target_dir` may have a partial clone).
