---
name: workspace-scanner
description: Walk a directory tree and return categorized findings — stale files, orphaned artifacts, file-size outliers. Used by /runesmith-devtools:tech-debt to share the scan layer; the parent skill applies its own classification rules to the agent's raw findings.
tools: Bash, Read
---

# Workspace Scanner Agent

Subagent that walks a directory tree under controlled depth limits, applies path/name filters, and returns structured findings. Read-only — never modifies files.

`tech-debt` uses this scan layer (recursive directory walk, file metadata gather, pattern match) and applies its own classification rules on top. This agent does the walk and gather; the parent skill does the rules.

## Inputs

Parent skill provides:
- `roots`: list of absolute paths to scan
- `max_depth`: integer (default 6) — caps recursion
- `include_patterns`: list of glob patterns to include (default: all)
- `exclude_patterns`: list of glob patterns to skip (default: `.git/`, `node_modules/`, `__pycache__/`, etc.)
- `gather_metadata`: bool — if true, capture file size, mtime, and basic content hints (first line, file type)

## Workflow

### 1. Walk

For each root in `roots`:
- Recurse depth-first up to `max_depth`
- Apply include/exclude filters at each level
- For each file matched, gather:
  - Path (absolute)
  - Size (bytes)
  - mtime (ISO timestamp)
  - File type heuristic (text / binary / known extension)
  - If `gather_metadata`: first non-blank line of text files (used for header detection)

### 2. Categorize

Bucket findings by simple heuristics that ANY scan-skill might use:
- **Empty** files (0 bytes)
- **Stale** files (mtime older than 90 days, marked but not auto-acted)
- **Orphaned** files (path/extension doesn't match any expected pattern from parent's input)
- **Large** files (> 1 MB, candidate for binary or accidentally-committed asset)
- **Hidden** dirs the parent didn't exclude (warn, since they may be intentional)

Parent skill adds its own categorization on top (e.g. `tech-debt` flags `_pre-migration/` snapshots older than 30 days, `archive/superseded/` content older than 90 days, etc.).

### 3. Return

Structured JSON:
```json
{
  "scanned_files": 247,
  "by_root": {
    "/path/to/root1": { "files": 200, ... },
    ...
  },
  "findings": [
    {
      "path": "/full/path/to/file",
      "size": 12345,
      "mtime": "2026-04-15T...",
      "type": "text",
      "buckets": ["stale"]
    },
    ...
  ],
  "errors": []
}
```

Parent skill walks `findings` and applies its own rules.

## Guard Rails

- [ ] Read-only — never opens a file in write mode, never deletes
- [ ] Honors `max_depth` to prevent runaway recursion
- [ ] Honors `exclude_patterns` strictly (default list always applied)
- [ ] Returns errors per-file if a path is unreadable; never bails out of the whole scan
- [ ] No content of files is included in the return value beyond the optional first-line heuristic — keeps return size bounded
- [ ] Subagent context never contains file contents in chat history beyond the structured return

## Why this is an agent

- `tech-debt` scans the full workspace; without the agent, the parent skill carries the walk loop and categorization inline — more context bloat, less reuse if a future scan-driven skill arrives.
- Walking large directories (workspace root with many subdirs) generates lots of intermediate context. Isolating in a subagent keeps the parent's chat clean.
- Read-only nature is enforced by the agent's tool restrictions (`Bash`, `Read` only — no `Write`).

## Error Cases

**Permission denied on a path:** Skip that path, log to `errors[]`, continue.
**Symlink loop:** Detect via realpath comparison; abort the loop and log to `errors[]`.
**Root path doesn't exist:** Return early with the missing root in `errors[]`.
**`max_depth` reached:** Stop recursing at that level; mark in scan summary.
