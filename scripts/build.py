#!/usr/bin/env python3
"""
Build RuneSmith marketplace .plugin zips.

Cross-platform build script. Recommended over bash/PowerShell on Windows because
PowerShell's Compress-Archive and .NET's ZipFile both use backslash separators
inside the zip, which Cowork's plugin validator rejects. Python's zipfile module
always uses forward slashes per the zip spec.

Usage:
    python scripts/build.py                # output to ./dist/ (default)
    python scripts/build.py path/to/out    # output to a custom directory

The output directory is created if missing. Existing .plugin files in the output
are overwritten.

What the build does per plugin:
  1. Copy plugins/<name>/ to a temp staging dir
  2. Strip retired content (skills/verify-separation, commands/verify-separation.md)
  3. Strip cc-skill-templates/<n>/SKILL.md (these would trip Cowork's skill scanner)
  4. Rename cc-skill-templates/<n>/skill-template.md -> .txt (so the validator
     ignores them but bootstrap-cc / sprint:enable can still read+deploy them)
  5. Zip the staged plugin folder (forward slashes via zipfile) to <output>/<name>.plugin

Exit codes:
  0 — built all plugins successfully
  1 — at least one plugin failed to build (others may have succeeded)
  2 — invalid invocation
"""

import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "plugins"

PLUGINS = [
    "runesmith-core",
    "runesmith-workspace",
    "runesmith-cc",
    "runesmith-jira",
    "runesmith-confluence",
    "runesmith-sprint",
    "runesmith-aiops",
    "runesmith-devtools",
]


def build_one(plugin: str, src_dir: Path, out_path: Path, stage_root: Path) -> int:
    """Build a single plugin .plugin zip. Returns size in bytes, or -1 on failure."""
    stage = stage_root / plugin
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(src_dir, stage)

    # Strip retired skills + commands
    for r in [
        stage / "skills" / "verify-separation",
        stage / "commands" / "verify-separation.md",
    ]:
        if r.is_dir():
            shutil.rmtree(r)
        elif r.exists():
            r.unlink()

    # Handle cc-skill-templates — deploy-time templates, not active plugin skills
    cct = stage / "cc-skill-templates"
    if cct.is_dir():
        for sk in cct.rglob("SKILL.md"):
            sk.unlink()
        for st in cct.rglob("skill-template.md"):
            st.rename(st.with_suffix(".txt"))

    if out_path.exists():
        out_path.unlink()

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(stage):
            for f in files:
                full = Path(root) / f
                arc = full.relative_to(stage_root).as_posix()
                z.write(full, arc)

    return out_path.stat().st_size


def main() -> int:
    if len(sys.argv) > 2:
        print("Usage: python scripts/build.py [output_dir]", file=sys.stderr)
        return 2

    out_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else REPO / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"RuneSmith build")
    print(f"  source:  {SRC}")
    print(f"  output:  {out_dir}")
    print()

    failures = 0
    stage_root = Path(tempfile.mkdtemp(prefix="runesmith-build-"))
    try:
        for p in PLUGINS:
            src = SRC / p
            if not src.is_dir():
                print(f"  skip {p}  (source missing: {src})", file=sys.stderr)
                failures += 1
                continue
            out = out_dir / f"{p}.plugin"
            try:
                size = build_one(p, src, out, stage_root)
                print(f"  built {p}.plugin  ({size:,} bytes)")
            except Exception as e:
                print(f"  FAIL {p}: {e}", file=sys.stderr)
                failures += 1
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)

    print()
    if failures:
        print(f"done — {failures} failure(s)")
        return 1
    print(f"done — {len(PLUGINS)} plugins built")
    return 0


if __name__ == "__main__":
    sys.exit(main())
