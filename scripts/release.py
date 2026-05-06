from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
VERSION_RE = re.compile(r'^version = "([^"]+)"$', re.MULTILINE)
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def run(command: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )

    if result.returncode != 0:
        if capture:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)

    return (result.stdout or "").strip()


def require_clean_tracked_changes() -> None:
    run(["git", "diff", "--quiet"])
    run(["git", "diff", "--cached", "--quiet"])


def current_branch() -> str:
    branch = run(["git", "branch", "--show-current"], capture=True)
    if not branch:
        raise SystemExit("Cannot release from a detached HEAD")
    return branch


def latest_semver_tag() -> tuple[int, int, int] | None:
    run(["git", "fetch", "--tags", "origin"])
    tags = run(["git", "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"], capture=True).splitlines()
    versions: list[tuple[int, int, int]] = []

    for tag in tags:
        match = TAG_RE.fullmatch(tag)
        if match:
            major, minor, patch = match.groups()
            versions.append((int(major), int(minor), int(patch)))

    if not versions:
        return None

    return max(versions)


def read_project_version() -> str:
    match = VERSION_RE.search(PYPROJECT.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit("Could not find project version in pyproject.toml")
    return match.group(1)


def write_project_version(version: str) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    updated = VERSION_RE.sub(f'version = "{version}"', text, count=1)
    PYPROJECT.write_text(updated, encoding="utf-8")


def next_patch_version() -> str:
    latest = latest_semver_tag()
    if latest is None:
        return read_project_version()

    major, minor, patch = latest
    return f"{major}.{minor}.{patch + 1}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and push the next patch release tag.")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable to use for Makefile verification targets.",
    )
    args = parser.parse_args()

    branch = current_branch()
    require_clean_tracked_changes()

    version = next_patch_version()
    tag = f"v{version}"

    if run(["git", "tag", "--list", tag], capture=True):
        raise SystemExit(f"Tag already exists: {tag}")

    write_project_version(version)

    run(["make", "lint", f"PYTHON={args.python}"])
    run(["make", "typecheck", f"PYTHON={args.python}"])
    run(["make", "test", f"PYTHON={args.python}"])
    run(["make", "clean", "package", f"PYTHON={args.python}"])

    run(["git", "add", "pyproject.toml"])
    run(["git", "commit", "-m", f"Release {tag}"])
    run(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
    run(["git", "push", "origin", branch])
    run(["git", "push", "origin", tag])

    print(f"Released {tag}")


if __name__ == "__main__":
    main()
