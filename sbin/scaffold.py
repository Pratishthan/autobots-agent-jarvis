#!/usr/bin/env python3
"""Scaffold your project after cloning from the autobots-agents-jarvis template.

Run this script from the root of your newly cloned repo to rename everything
from "jarvis" to your project name. The script transforms the repo in-place
and deletes itself when done.

Usage:
    python3 sbin/scaffold.py kbe-pay
    python3 sbin/scaffold.py kbe-pay --display-name "KBE Pay" --description "My App"
    python3 sbin/scaffold.py kbe-pay --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

# Directories to skip when walking the file tree
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}

# Binary file extensions to skip during content replacement
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".bmp",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".pdf",
    ".drawio",
    ".lock",
}

# Template artifacts to clean up
ARTIFACTS_TO_CLEAN = [
    ".coverage",
    "coverage.xml",
    "htmlcov",
    ".pytest_cache",
    ".ruff_cache",
    "poetry.lock",
]

# Demo content to remove (paths relative to project root)
PATHS_TO_REMOVE = [
    "src/autobots_agents_jarvis/domains/customer_support",
    "src/autobots_agents_jarvis/domains/sales",
    "agent_configs/customer-support",
    "agent_configs/sales",
    "sbin/run_customer_support.sh",
    "sbin/run_sales.sh",
    "sbin/run_all_domains.sh",
    "tests/unit/domains",
    "tests/sanity",
]


def derive_names(name: str) -> dict[str, str]:
    """Derive all project name variants from the input name (e.g., 'kbe-pay')."""
    if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
        print(f"Error: name '{name}' must be lowercase with hyphens (e.g., 'kbe-pay', 'my-app')")
        sys.exit(1)

    snake = name.replace("-", "_")
    parts = name.split("-")
    pascal = "".join(p.capitalize() for p in parts)
    display = " ".join(p.capitalize() for p in parts)

    return {
        "name": name,
        "repo_name": f"autobots-{name}",
        "pypi_name": f"autobots-{name}",
        "package_name": f"autobots_{snake}",
        "snake_name": snake,
        "pascal_name": pascal,
        "display_name": display,
    }


def build_replacements(names: dict[str, str]) -> list[tuple[str, str]]:
    """Build ordered list of (old, new) string replacements. Most-specific first."""
    sn = names["snake_name"]
    upper_sn = sn.upper()
    pkg = names["package_name"]
    pascal = names["pascal_name"]
    display = names["display_name"]
    repo = names["repo_name"]

    return [
        # Package/project names (most specific first to avoid partial matches)
        ("autobots-agents-jarvis", repo),
        ("autobots_agents_jarvis", pkg),
        # Class names
        ("JarvisSettings", f"{pascal}Settings"),
        # Function names
        ("get_jarvis_settings", f"get_{sn}_settings"),
        ("init_jarvis_settings", f"init_{sn}_settings"),
        ("register_jarvis_tools", f"register_{sn}_tools"),
        ("_get_jarvis_batch_agents", f"_get_{sn}_batch_agents"),
        ("jarvis_registered", f"{sn}_registered"),
        # App/service names
        ("jarvis_batch", f"{sn}_batch"),
        ("jarvis_chat", f"{sn}_chat"),
        ("jarvis-chat", f"{sn}-chat"),
        ("jarvis_tools", f"{sn}_tools"),
        ("jarvis-invoke-demo", f"{sn}-invoke-demo"),
        # File/path references
        ("run_jarvis", f"run_{sn}"),
        ("jarvis_ui", f"{sn}_ui"),
        # Uppercase references (shell variables like JARVIS_DIR, _JARVIS_CONFIG)
        ("JARVIS", upper_sn),
        # Display name (capitalized in docs/comments)
        ("Jarvis", display),
        # Catch-all for remaining lowercase references (config paths, env vars, etc.)
        ("jarvis", sn),
    ]


def is_binary(path: Path) -> bool:
    """Check if a file is binary based on extension."""
    return path.suffix.lower() in BINARY_EXTENSIONS


def apply_replacements(content: str, replacements: list[tuple[str, str]]) -> str:
    """Apply all string replacements to content."""
    for old, new in replacements:
        content = content.replace(old, new)
    return content


def clean_artifacts(project_dir: Path, *, dry_run: bool = False) -> None:
    """Remove template build artifacts and caches."""
    for rel_path in ARTIFACTS_TO_CLEAN:
        target = project_dir / rel_path
        if not target.exists():
            continue
        if dry_run:
            print(f"[DRY RUN] Would clean: {rel_path}")
        elif target.is_dir():
            shutil.rmtree(target)
            print(f"Cleaned: {rel_path}/")
        else:
            target.unlink()
            print(f"Cleaned: {rel_path}")


def remove_demo_content(project_dir: Path, *, dry_run: bool = False) -> None:
    """Remove demo domains and extra scripts."""
    for rel_path in PATHS_TO_REMOVE:
        target = project_dir / rel_path
        if not target.exists():
            continue
        if dry_run:
            print(f"[DRY RUN] Would remove: {rel_path}")
        elif target.is_dir():
            shutil.rmtree(target)
            print(f"Removed directory: {rel_path}")
        else:
            target.unlink()
            print(f"Removed file: {rel_path}")


def replace_in_files(
    project_dir: Path,
    replacements: list[tuple[str, str]],
    *,
    dry_run: bool = False,
) -> None:
    """Apply content replacements to all text files in the project."""
    for root, dirs, files in os.walk(project_dir):
        # Skip directories we shouldn't touch
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            filepath = Path(root) / filename
            if is_binary(filepath):
                continue
            try:
                content = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            new_content = apply_replacements(content, replacements)
            if new_content != content:
                rel = filepath.relative_to(project_dir)
                if dry_run:
                    for old, new in replacements:
                        if old in content:
                            print(f"[DRY RUN] {rel}: '{old}' -> '{new}'")
                else:
                    filepath.write_text(new_content, encoding="utf-8")
                    print(f"Updated: {rel}")


def rename_paths(
    project_dir: Path,
    names: dict[str, str],
    *,
    dry_run: bool = False,
) -> None:
    """Rename directories and files containing 'jarvis' in their name.

    Works bottom-up (deepest paths first) to avoid breaking parent paths.
    """
    sn = names["snake_name"]
    pkg = names["package_name"]

    paths_to_rename: list[tuple[Path, Path]] = []

    for root, _, files in os.walk(project_dir, topdown=False):
        root_path = Path(root)

        # Skip .git and other protected dirs
        if any(part in SKIP_DIRS for part in root_path.relative_to(project_dir).parts):
            continue

        # Rename files
        for filename in files:
            if "jarvis" in filename:
                old_path = root_path / filename
                new_name = filename.replace("jarvis", sn)
                new_path = root_path / new_name
                paths_to_rename.append((old_path, new_path))

        # Rename directories
        dir_name = root_path.name
        if dir_name == "autobots_agents_jarvis":
            new_path = root_path.parent / pkg
            paths_to_rename.append((root_path, new_path))
        elif dir_name == "jarvis" and root_path.parent.name in ("domains", "agent_configs"):
            new_path = root_path.parent / sn
            paths_to_rename.append((root_path, new_path))

    for old_path, new_path in paths_to_rename:
        rel_old = old_path.relative_to(project_dir)
        rel_new = new_path.relative_to(project_dir)
        if dry_run:
            print(f"[DRY RUN] Rename: {rel_old} -> {rel_new}")
        else:
            if old_path.exists():
                old_path.rename(new_path)
                print(f"Renamed: {rel_old} -> {rel_new}")


def scaffold(args: argparse.Namespace) -> None:
    """Main scaffolding logic — transforms the repo in-place."""
    names = derive_names(args.name)
    if args.display_name:
        names["display_name"] = args.display_name
    project_dir = Path(__file__).resolve().parent.parent

    # Verify we're in the template repo
    if not (project_dir / "src" / "autobots_agents_jarvis").is_dir():
        print(
            "Error: scaffold.py must be run from a repo cloned from the autobots-agents-jarvis template."
        )
        sys.exit(1)

    dry_run = args.dry_run

    print(f"Scaffolding project: {names['repo_name']}")
    print(f"  Package:  {names['package_name']}")
    print(f"  Display:  {names['display_name']}")
    print(f"  Domain:   {names['snake_name']}")
    if args.description:
        print(f"  Desc:     {args.description}")
    if args.port != 1337:
        print(f"  Port:     {args.port}")
    print()

    # Step 1: Clean template artifacts
    clean_artifacts(project_dir, dry_run=dry_run)

    # Step 2: Remove demo content
    remove_demo_content(project_dir, dry_run=dry_run)

    # Step 3: Content replacements
    replacements = build_replacements(names)
    replace_in_files(project_dir, replacements, dry_run=dry_run)

    # Step 4 & 5: Rename directories and files
    rename_paths(project_dir, names, dry_run=dry_run)

    # Step 6: Post-processing overrides
    if not dry_run:
        # Update description if provided
        if args.description:
            pyproject = project_dir / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                old_desc = f"{names['display_name']} - Multi-agent AI Assistant Demo"
                content = content.replace(old_desc, args.description)
                pyproject.write_text(content)
                print("Updated description in pyproject.toml")

        # Update port if non-default
        if args.port != 1337:
            makefile = project_dir / "Makefile"
            if makefile.exists():
                content = makefile.read_text()
                content = content.replace("CHAINLIT_PORT = 1337", f"CHAINLIT_PORT = {args.port}")
                makefile.write_text(content)

            for settings_file in project_dir.rglob("settings.py"):
                content = settings_file.read_text()
                content = content.replace("default=1337", f"default={args.port}")
                settings_file.write_text(content)

            run_script = project_dir / "sbin" / f"run_{names['snake_name']}.sh"
            if run_script.exists():
                content = run_script.read_text()
                content = content.replace("PORT:-1337", f"PORT:-{args.port}")
                run_script.write_text(content)
            print(f"Updated port to {args.port}")

    # Step 7: Self-delete (last step)
    script_path = Path(__file__).resolve()
    if dry_run:
        print("[DRY RUN] Would delete: sbin/scaffold.py")
    else:
        script_path.unlink()
        print("Removed: sbin/scaffold.py")

    print()
    print("Done! Your project is ready.")
    print()
    print("Next steps:")
    print("  cp .env.example .env")
    print("  # Edit .env with your API keys")
    print("  make install-dev")
    print("  make all-checks")
    print("  make chainlit-dev")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold your project after cloning from the autobots-agents-jarvis template.",
        epilog="Example: python3 sbin/scaffold.py kbe-pay",
    )
    parser.add_argument(
        "name",
        help="Project name using lowercase and hyphens (e.g., 'kbe-pay', 'my-app'). "
        "The package will be named 'autobots-{name}'.",
    )
    parser.add_argument(
        "--display-name",
        default=None,
        help="Human-readable display name (e.g., 'KBE Pay'). Auto-derived if not set.",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Project description for pyproject.toml.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1337,
        help="Default Chainlit port (default: 1337).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes.",
    )

    args = parser.parse_args()
    scaffold(args)


if __name__ == "__main__":
    main()
