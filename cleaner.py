#!/usr/bin/env python3
"""Clean the current directory using patterns from ~/.cleaner/cleaner.conf."""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import sys
from pathlib import Path

CONFIG = Path.home() / ".cleaner" / "cleaner.conf"


def load_patterns(config: Path) -> list[str]:
    if not config.is_file():
        raise FileNotFoundError(
            f"Config not found: {config}\n"
            "Run the installer again or create the config file."
        )
    patterns = []
    for line in config.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def matches(path: Path, root: Path, patterns: list[str], is_dir: bool) -> bool:
    rel = path.relative_to(root).as_posix()
    name = path.name

    for raw in patterns:
        directory_only = raw.endswith("/")
        pattern = raw.rstrip("/")
        if not pattern:
            continue
        if directory_only and not is_dir:
            continue

        anchored = pattern.startswith("/")
        pattern = pattern.lstrip("/")

        # Patterns containing "/" match paths relative to the project root.
        # Patterns without "/" match a name at any depth.
        if "/" in pattern:
            if fnmatch.fnmatchcase(rel, pattern):
                return True
            # Also allow a directory rule to match all descendants.
            if is_dir and fnmatch.fnmatchcase(rel, pattern):
                return True
        elif fnmatch.fnmatchcase(name, pattern):
            return True

        # A leading slash anchors a simple pattern to the project root.
        if anchored and "/" not in pattern and rel == pattern:
            return True

    return False


def collect_targets(root: Path, patterns: list[str]) -> list[Path]:
    targets: list[Path] = []
    root = root.resolve()

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)

        # Check directories first. Matching directories are removed from
        # traversal, so their contents are not separately listed.
        kept_dirs = []
        for dirname in dirs:
            candidate = current_path / dirname
            if candidate.is_symlink() or matches(candidate, root, patterns, True):
                targets.append(candidate)
            else:
                kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        for filename in files:
            candidate = current_path / filename
            if matches(candidate, root, patterns, False):
                targets.append(candidate)

    return sorted(set(targets), key=lambda p: (len(p.parts), str(p)))


def remove_target(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove files and directories matching ~/.cleaner/cleaner.conf"
    )
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would be deleted without deleting")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="delete without confirmation")
    parser.add_argument("--config", type=Path, default=CONFIG,
                        help=f"config path (default: {CONFIG})")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    try:
        patterns = load_patterns(args.config)
    except (OSError, FileNotFoundError) as exc:
        print(f"cleaner: {exc}", file=sys.stderr)
        return 1

    targets = collect_targets(root, patterns)
    if not targets:
        print(f"Nothing to clean in: {root}")
        return 0

    print(f"Project: {root}")
    print(f"Matched items: {len(targets)}")
    for path in targets:
        kind = "DIR " if path.is_dir() and not path.is_symlink() else "FILE"
        print(f"  [{kind}] {path.relative_to(root)}")

    if args.dry_run:
        print("\nDry run: no files were deleted.")
        return 0

    if not args.yes:
        try:
            answer = input("\nDelete these items? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return 130
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    removed = 0
    for path in targets:
        try:
            remove_target(path)
            removed += 1
        except OSError as exc:
            print(f"Failed: {path}: {exc}", file=sys.stderr)

    print(f"\nRemoved {removed}/{len(targets)} item(s).")
    return 0 if removed == len(targets) else 2


if __name__ == "__main__":
    raise SystemExit(main())
