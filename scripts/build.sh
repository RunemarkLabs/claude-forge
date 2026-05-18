#!/usr/bin/env bash
# Build .plugin files for the runesmith marketplace.
#
# Usage:
#   bash scripts/build.sh                # output to ./dist/ (default)
#   bash scripts/build.sh path/to/out    # output to a custom directory
#
# Run from repo root.
#
# On Windows: prefer scripts/build.py instead. PowerShell's Compress-Archive
# and .NET's ZipFile both use backslash separators inside the zip, which Cowork's
# plugin validator rejects. Python's zipfile module uses forward slashes per the
# zip spec.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/plugins"
OUT="${1:-$REPO_ROOT/dist}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$OUT"

PLUGINS=(
  runesmith-core
  runesmith-workspace
  runesmith-cc
  runesmith-jira
  runesmith-confluence
  runesmith-sprint
  runesmith-aiops
  runesmith-devtools
)

for p in "${PLUGINS[@]}"; do
  if [ ! -d "$SRC/$p" ]; then
    echo "skip $p - $SRC/$p not found" >&2
    continue
  fi

  rm -rf "$STAGE/$p" "$OUT/$p.plugin"
  mkdir -p "$STAGE/$p"

  # IMPORTANT: copy with /. so dotfiles (like .claude-plugin/) come along
  cp -r "$SRC/$p/." "$STAGE/$p/"

  # Strip retired content that shouldn't ship
  rm -rf "$STAGE/$p/skills/verify-separation"
  rm -f  "$STAGE/$p/commands/verify-separation.md"

  # Strip cc-skill-templates/<n>/SKILL.md - these would trip Cowork's skill scanner
  # outside of skills/<name>/. The .md content stays under skill-template.md, renamed
  # to .txt below so the validator ignores them.
  find "$STAGE/$p/cc-skill-templates" -type f -name 'SKILL.md' -delete 2>/dev/null || true
  find "$STAGE/$p/cc-skill-templates" -type f -name 'skill-template.md' \
    -exec sh -c 'mv "$1" "${1%.md}.txt"' _ {} \; 2>/dev/null || true

  # Zip from staging parent so the plugin folder is the top-level entry inside the zip.
  (cd "$STAGE" && zip -qr "$STAGE/$p.plugin" "$p")
  cp "$STAGE/$p.plugin" "$OUT/$p.plugin"

  size=$(stat -c%s "$OUT/$p.plugin" 2>/dev/null || stat -f%z "$OUT/$p.plugin")
  echo "built $OUT/$p.plugin ($size bytes)"
done

echo "done."
