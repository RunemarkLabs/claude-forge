# Release process - Runemark internal

This document describes how to ship a release of RuneSmith from this private development workspace to the public marketplace repo.

**Audience:** Runemark Labs internal contributors. The public marketplace repo (e.g. `github.com/runemarklabs/runesmith`) is the consumer-facing artifact.

## Repo topology

```
PRIVATE (this workspace, internal-only)
├── .claude-plugin/              ← public
├── plugins/                     ← public
├── dist/                        ← public
├── scripts/                     ← public (audit.py, md-to-storage.py)
├── .github/workflows/           ← public
├── README, INSTALL, CHANGELOG,  ← public
│   CONTRIBUTING, LICENSE, NOTICE
├── .credentials.example         ← public
├── .gitignore                   ← public
│
├── CLAUDE.md                    ← private (workspace rules for Runemark dev)
├── notes/                       ← private (Ben's session notes)
├── drafts/                      ← private (pre-publish Atlassian drafts)
├── plans/                       ← private (project plans, supersedes/related)
├── _INBOX/                      ← private (drop zone)
├── tickets/                     ← private (Jira drafts)
├── research/                    ← private (analysis docs)
├── source-docs/                 ← private (external uploads)
├── archive/                     ← private (reallocate / bootstrap-cc snapshots)
├── claude-code/                 ← private (Ben's CC workspaces)
├── *.cc/                        ← private (per-project CC heads)
├── .credentials                 ← private (real creds, gitignored)
├── atlassian-index.json         ← private (workspace index)
├── bootstrap-setup-templates.md ← private (legacy)
├── Screenshot*.png              ← private (workflow screenshots)
└── PUBLIC.manifest.txt          ← controls what release.sh ships
└── RELEASE.md                   ← this file
└── scripts/release.sh           ← Runemark internal release tool

PUBLIC (e.g. github.com/runemarklabs/runesmith)
└── (only the subset listed in PUBLIC.manifest.txt)
```

## How to release

Prerequisite: have a local clone of the public marketplace repo somewhere on disk:

```bash
git clone git@github.com:runemarklabs/runesmith.git ~/Code/runesmith
```

From this private workspace:

```bash
# 1. Bump version in marketplace.json + each plugin.json if releasing a new version
# 2. Update CHANGELOG.md
# 3. Run the audit locally
python3 scripts/audit.py

# 4. Run release script pointing at your public clone
bash scripts/release.sh ~/Code/runesmith

# 5. Review the diff in the public clone, then commit + push
cd ~/Code/runesmith
git status
git add -A
git commit -m "release: runesmith v0.4.0"
git push origin main
```

The release script:
- Runs `scripts/audit.py` first; refuses to ship if audit fails.
- Reads `PUBLIC.manifest.txt` to determine what to copy.
- Refuses to overwrite uncommitted changes in the public clone without confirmation.
- Copies each manifest entry from this private workspace to the destination.
- Never copies anything not on the manifest.

## What the public sees

- The packaged `dist/*.plugin` files (drag-and-drop install)
- The plugin source in `plugins/` (forkable, modifiable)
- Reference scripts: `scripts/audit.py` (validation), `scripts/md-to-storage.py` (converter)
- CI workflow: `.github/workflows/build.yml`
- Documentation: README, INSTALL, CHANGELOG, CONTRIBUTING
- Legal: LICENSE (Apache-2.0), NOTICE
- `.credentials.example` template

The public never sees:
- Internal session notes, drafts, plans, research
- Workspace CLAUDE.md (the rules for *this* dev environment)
- Any real credentials, screenshots, or per-project `.cc/` workspaces
- The release script itself (it's Runemark internal tooling)
- This RELEASE.md (also Runemark internal)
- PUBLIC.manifest.txt (Runemark internal)

## Forks

Anyone (Sapient, third parties, anyone who finds the repo) can fork the public marketplace and modify for their own use. Runemark does not maintain forks. Sapient-specific or other tenant-specific customizations live in their own forks, not in this dev workspace and not in the public marketplace.

The public marketplace is **generic and single-tenant configurable per project** - that's a design invariant enforced by `scripts/audit.py`. Forks may override that for internal use.

## Version policy

Single version across the marketplace (`marketplace.json` `metadata.version` + every plugin.json `version`). Bump together on each release. Semver:
- **MAJOR** - breaking changes to lib conventions, skill names, or marketplace structure
- **MINOR** - new skills, new plugins, new agent files
- **PATCH** - fixes, doc updates, internal refactors

Update `CHANGELOG.md` under `## [<version>] - <date>` with the change list before running release.

## Common workflow patterns

**Hotfix a published plugin:**
1. Make the fix in this private workspace, in `plugins/<plugin>/`
2. Bump PATCH version in `marketplace.json` and the affected plugin.json
3. Add CHANGELOG entry
4. `python3 scripts/audit.py`
5. `bash dist/build.sh`  (rebuilds `.plugin` zips)
6. `bash scripts/release.sh ~/Code/runesmith`
7. cd to public clone, commit, push

**Add a new plugin:**
1. Develop under `plugins/<new-plugin>/`
2. Add entry to `marketplace.json` `plugins[]`
3. Add new plugin to `PUBLIC.manifest.txt`? - already covered (`plugins/` is a recursive copy)
4. Update `dist/build.sh` PLUGINS array? - yes, add to the array
5. Bump MINOR version everywhere
6. Audit, rebuild, release

**Working session that should stay private:**
1. Use this private workspace freely. Write notes, drafts, plans. None of it ships.
2. When ready to publish, run `scripts/release.sh` - only the public subset goes.
