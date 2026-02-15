#!/usr/bin/env python3
"""Scaffold your project after cloning from the autobots-agents-jarvis template.

Run this script from the root of your newly cloned repo to rename everything
to your project name. The script handles two naming levels:

  1. Source root: autobots_agents_jarvis -> autobots_<project>
  2. Primary domain: concierge -> <domain> (defaults to project name)

Usage:
    python3 sbin/scaffold.py kbe-pay
    python3 sbin/scaffold.py kbe-pay --primary-domain nurture
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

# Demo content to remove (paths relative to project root).
# Only removes the extra demo domains; keeps the primary domain (concierge).
PATHS_TO_REMOVE = [
    "src/autobots_agents_jarvis/domains/customer_support",
    "src/autobots_agents_jarvis/domains/sales",
    "agent_configs/customer-support",
    "agent_configs/sales",
    "sbin/run_customer_support.sh",
    "sbin/run_sales.sh",
    "sbin/run_all_domains.sh",
    "tests/unit/domains/customer_support",
    "tests/unit/domains/sales",
    "tests/integration/domains/customer_support",
    "tests/integration/domains/sales",
    "tests/sanity/domains/customer_support",
    "tests/sanity/domains/sales",
]

_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def derive_names(name: str) -> dict[str, str]:
    """Derive all project name variants from the input name (e.g., 'kbe-pay')."""
    if not _NAME_RE.match(name):
        print(f"Error: name '{name}' must be lowercase with hyphens (e.g., 'kbe-pay', 'my-app')")
        sys.exit(1)

    # Strip 'autobots-' prefix if the user already included it to avoid doubling
    if name.startswith("autobots-"):
        name = name[len("autobots-") :]

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


def derive_domain_names(domain_name: str) -> dict[str, str]:
    """Derive domain-level name variants from a domain name (e.g., 'nurture')."""
    if not _NAME_RE.match(domain_name):
        print(
            f"Error: domain name '{domain_name}' must be lowercase with hyphens "
            f"(e.g., 'nurture', 'lead-gen')"
        )
        sys.exit(1)

    snake = domain_name.replace("-", "_")
    parts = domain_name.split("-")
    pascal = "".join(p.capitalize() for p in parts)
    display = " ".join(p.capitalize() for p in parts)
    upper = snake.upper()

    return {
        "domain_name": domain_name,
        "domain_snake": snake,
        "domain_pascal": pascal,
        "domain_display": display,
        "domain_upper": upper,
    }


def _build_source_root_replacements(names: dict[str, str]) -> list[tuple[str, str]]:
    """Replacements for the source-root / package level (autobots_agents_jarvis -> new pkg)."""
    return [
        ("autobots-agents-jarvis", names["repo_name"]),
        ("autobots_agents_jarvis", names["package_name"]),
    ]


def _build_domain_replacements(domain_names: dict[str, str]) -> list[tuple[str, str]]:
    """Replacements for the domain level (concierge -> new domain)."""
    sn = domain_names["domain_snake"]
    pascal = domain_names["domain_pascal"]
    display = domain_names["domain_display"]
    upper = domain_names["domain_upper"]

    return [
        # Class names (most specific first)
        ("ConciergeSettings", f"{pascal}Settings"),
        # Function names
        ("get_concierge_settings", f"get_{sn}_settings"),
        ("init_concierge_settings", f"init_{sn}_settings"),
        ("register_concierge_tools", f"register_{sn}_tools"),
        ("_get_concierge_batch_agents", f"_get_{sn}_batch_agents"),
        ("concierge_tools_registered", f"{sn}_tools_registered"),
        ("concierge_registered", f"{sn}_registered"),
        # App/service names
        ("concierge_batch", f"{sn}_batch"),
        ("concierge_chat", f"{sn}_chat"),
        ("concierge-chat", f"{sn}-chat"),
        ("concierge_tools", f"{sn}_tools"),
        ("concierge-invoke-demo", f"{sn}-invoke-demo"),
        # File/path references
        ("run_concierge", f"run_{sn}"),
        ("concierge_dir", f"{sn}_dir"),
        ("concierge_agents", f"{sn}_agents"),
        # Uppercase references (shell variables like _CONCIERGE_CONFIG, CONCIERGE_DIR)
        ("_CONCIERGE_CONFIG", f"_{upper}_CONFIG"),
        ("CONCIERGE_DIR", f"{upper}_DIR"),
        ("CONCIERGE", upper),
        # Display name (capitalized in docs/comments)
        ("Concierge", display),
        # Catch-all for remaining lowercase references (config paths, env vars, etc.)
        ("concierge", sn),
    ]


def build_replacements(
    names: dict[str, str], domain_names: dict[str, str]
) -> list[tuple[str, str]]:
    """Build ordered list of (old, new) string replacements.

    Source-root replacements go first (longer, more specific strings) followed
    by domain-level replacements. This ordering prevents partial-match issues.
    """
    return _build_source_root_replacements(names) + _build_domain_replacements(domain_names)


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
    domain_names: dict[str, str],
    *,
    dry_run: bool = False,
) -> None:
    """Rename directories and files for both naming levels.

    Handles two levels:
      - Source root: autobots_agents_jarvis -> new package name
      - Domain: concierge -> new domain name (dirs and files)

    Works bottom-up (deepest paths first) to avoid breaking parent paths.
    """
    pkg = names["package_name"]
    domain_sn = domain_names["domain_snake"]

    paths_to_rename: list[tuple[Path, Path]] = []

    for root, _, files in os.walk(project_dir, topdown=False):
        root_path = Path(root)

        # Skip .git and other protected dirs
        if any(part in SKIP_DIRS for part in root_path.relative_to(project_dir).parts):
            continue

        # Rename files containing "concierge" in their name
        for filename in files:
            if "concierge" in filename:
                old_path = root_path / filename
                new_name = filename.replace("concierge", domain_sn)
                new_path = root_path / new_name
                paths_to_rename.append((old_path, new_path))

        # Rename directories
        dir_name = root_path.name
        if dir_name == "autobots_agents_jarvis":
            # Source-root level rename
            new_path = root_path.parent / pkg
            paths_to_rename.append((root_path, new_path))
        elif dir_name == "concierge" and root_path.parent.name in ("domains", "agent_configs"):
            # Domain-level rename (src/.../domains/concierge, agent_configs/concierge,
            # and also tests/*/domains/concierge since parent.name == "domains")
            new_path = root_path.parent / domain_sn
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


_STANDALONE_PYRIGHT_ENTRY = "entry: bash -c '.venv/bin/pyright src'"


def apply_standalone_repo_config(project_dir: Path, *, dry_run: bool = False) -> None:
    """Apply standalone-repo config: local .venv, no shared-lib, pyright from repo root.

    Edits .pre-commit-config.yaml, Makefile, and pyproject.toml so the project
    uses a venv in the repo root and does not depend on a parent monorepo.
    """
    # 1. .pre-commit-config.yaml: set pyright hook to .venv/bin/pyright src
    precommit = project_dir / ".pre-commit-config.yaml"
    if precommit.exists():
        try:
            content = precommit.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            pass
        else:
            new_lines = []
            for line in content.splitlines():
                if (
                    "entry:" in line
                    and "pyright" in line
                    and ("cd " in line or "/src'" in line or '/src"' in line)
                ):
                    indent = line[: len(line) - len(line.lstrip())]
                    new_lines.append(indent + _STANDALONE_PYRIGHT_ENTRY)
                else:
                    new_lines.append(line)
            new_content = "\n".join(new_lines) + ("\n" if content.endswith("\n") else "")
            if new_content != content:
                if dry_run:
                    print(
                        "[DRY RUN] Would update .pre-commit-config.yaml: pyright entry -> standalone"
                    )
                else:
                    precommit.write_text(new_content, encoding="utf-8")
                    print("Updated: .pre-commit-config.yaml (pyright entry)")

    # 2. Makefile: VENV = ../.venv -> VENV = .venv
    makefile = project_dir / "Makefile"
    if makefile.exists():
        try:
            content = makefile.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            pass
        else:
            if "VENV = ../.venv" in content:
                if dry_run:
                    print("[DRY RUN] Would update Makefile: VENV -> .venv")
                else:
                    content = content.replace("VENV = ../.venv", "VENV = .venv")
                    makefile.write_text(content, encoding="utf-8")
                    print("Updated: Makefile (VENV)")

    # 3. pyproject.toml: comment shared-lib dep; switch pyright to standalone block
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            pass
        else:
            changed = False
            # Comment out shared-lib path dependency if not already commented
            shared_lib_line = 'autobots-devtools-shared-lib = {path = "../autobots-devtools-shared-lib", develop = true}'
            if shared_lib_line in content and "# " + shared_lib_line not in content:
                content = content.replace(shared_lib_line, "# " + shared_lib_line)
                changed = True
            # In [tool.pyright]: comment monorepo lines, uncomment standalone lines
            in_pyright = False
            result_lines = []
            monorepo_uncommented = (
                'venvPath = ".."',
                'venv = ".venv"',
                'extraPaths = ["src", "../autobots-devtools-shared-lib/src"]',
            )
            standalone_commented = (
                '# venvPath = "."',
                '# venv = ".venv"',
                '# extraPaths = ["src"]',
            )
            for line in content.splitlines():
                if line.strip() == "[tool.pyright]":
                    in_pyright = True
                    result_lines.append(line)
                    continue
                if in_pyright and line.strip().startswith("["):
                    in_pyright = False
                if in_pyright:
                    stripped = line.strip()
                    if stripped in monorepo_uncommented:
                        indent = line[: len(line) - len(line.lstrip())]
                        result_lines.append(indent + "# " + stripped)
                        changed = True
                        continue
                    if stripped in standalone_commented:
                        indent = line[: len(line) - len(line.lstrip())]
                        result_lines.append(indent + stripped[2:].lstrip())  # drop "# "
                        changed = True
                        continue
                result_lines.append(line)
            if changed:
                content = "\n".join(result_lines) + ("\n" if content.endswith("\n") else "")
                if dry_run:
                    print("[DRY RUN] Would update pyproject.toml: standalone venv and pyright")
                else:
                    pyproject.write_text(content, encoding="utf-8")
                    print("Updated: pyproject.toml (standalone config)")


def scaffold(args: argparse.Namespace) -> None:
    """Main scaffolding logic — transforms the repo in-place."""
    names = derive_names(args.name)
    if args.display_name:
        names["display_name"] = args.display_name

    # Domain names: use --primary-domain if given, else same as project name
    domain_input = args.primary_domain if args.primary_domain else args.name
    domain_names = derive_domain_names(domain_input)

    project_dir = Path(__file__).resolve().parent.parent

    # Verify we're in the template repo
    if not (project_dir / "src" / "autobots_agents_jarvis").is_dir():
        print(
            "Error: scaffold.py must be run from a repo cloned from the autobots-agents-jarvis template."
        )
        sys.exit(1)

    dry_run = args.dry_run

    print(f"Scaffolding project: {names['repo_name']}")
    print(f"  Package:        {names['package_name']}")
    print(f"  Display:        {names['display_name']}")
    print(f"  Primary domain: {domain_names['domain_snake']}")
    if args.description:
        print(f"  Desc:           {args.description}")
    if args.port != 2337:
        print(f"  Port:           {args.port}")
    print()

    # Step 1: Clean template artifacts
    clean_artifacts(project_dir, dry_run=dry_run)

    # Step 2: Remove demo content (customer_support, sales)
    remove_demo_content(project_dir, dry_run=dry_run)

    # Step 3: Content replacements (source-root + domain level)
    replacements = build_replacements(names, domain_names)
    replace_in_files(project_dir, replacements, dry_run=dry_run)

    # Step 4: Rename directories and files
    rename_paths(project_dir, names, domain_names, dry_run=dry_run)

    # Step 4.5: Apply standalone-repo config (local .venv, no shared-lib, pyright from repo root)
    apply_standalone_repo_config(project_dir, dry_run=dry_run)

    # Step 5: Post-processing overrides
    if not dry_run:
        # Update description if provided
        if args.description:
            pyproject = project_dir / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                # Match the template's default description
                old_desc = "Jarvis - Multi-agent AI Assistant Demo"
                content = content.replace(old_desc, args.description)
                pyproject.write_text(content)
                print("Updated description in pyproject.toml")

        # Update port if non-default
        if args.port != 2337:
            makefile = project_dir / "Makefile"
            if makefile.exists():
                content = makefile.read_text()
                content = content.replace("CHAINLIT_PORT = 2337", f"CHAINLIT_PORT = {args.port}")
                makefile.write_text(content)

            for settings_file in project_dir.rglob("settings.py"):
                content = settings_file.read_text()
                content = content.replace("default=2337", f"default={args.port}")
                settings_file.write_text(content)

            domain_sn = domain_names["domain_snake"]
            run_script = project_dir / "sbin" / f"run_{domain_sn}.sh"
            if run_script.exists():
                content = run_script.read_text()
                content = content.replace("PORT:-2337", f"PORT:-{args.port}")
                run_script.write_text(content)
            print(f"Updated port to {args.port}")

    # Step 6: Self-delete (last step)
    script_path = Path(__file__).resolve()
    if dry_run:
        print("[DRY RUN] Would delete: sbin/scaffold.py")
    else:
        script_path.unlink()
        print("Removed: sbin/scaffold.py")

    domain_display = domain_names["domain_display"]
    print()
    print("Done! Your project is ready.")
    print()
    print("Next steps:")
    print("  cp .env.example .env")
    print("  # Edit .env with your API keys")
    print("  make install-dev")
    print("  make all-checks")
    print(f"  make chainlit-dev   # starts {domain_display} on port {args.port}")


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
        "--primary-domain",
        default=None,
        help="Primary domain name (e.g., 'nurture'). Defaults to the project name. "
        "Controls the domain-level rename (concierge -> your domain).",
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
        default=2337,
        help="Default Chainlit port (default: 2337).",
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
