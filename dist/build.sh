#!/usr/bin/env bash
# Build .plugin files for the runesmith marketplace.
# Run from repo root: bash dist/build.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$REPO_ROOT/dist"
SRC="$REPO_ROOT/plugins"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$DIST"

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
    echo "skip $p — $SRC/$p not found" >&2
    continue
  fi
  rm -rf "$STAGE/$p" "$DIST/$p.plugin"
  mkdir -p "$STAGE/$p"
  # IMPORTANT: copy with /. so dotfiles (like .claude-plugin/) come along
  cp -r "$SRC/$p/." "$STAGE/$p/"
  # Strip retired/orphan content that shouldn't ship.
  # runesmith-devtools: verify-separation was retired in v0.5.0; some workspaces
  # may have lingering source files from a failed delete in dev sandboxes. Exclude.
  rm -rf "$STAGE/$p/skills/verify-separation"
  rm -f  "$STAGE/$p/commands/verify-separation.md"
  # Zip from staging parent so the plugin folder is the top-level entry inside the zip.
  # zip -r recurses and includes dotfiles automatically.
  (cd "$STAGE" && zip -qr "$STAGE/$p.plugin" "$p")
  cp "$STAGE/$p.plugin" "$DIST/$p.plugin"
  size=$(stat -c%s "$DIST/$p.plugin" 2>/dev/null || stat -f%z "$DIST/$p.plugin")
  echo "built dist/$p.plugin ($size bytes)"
done

echo "done."
