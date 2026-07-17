"""Small command-line wrapper around Alembic's Python API.

Examples:
    python scripts/migration_cli.py upgrade head
    python scripts/migration_cli.py downgrade -1
    python scripts/migration_cli.py revision "add priority to tasks"
    python scripts/migration_cli.py current
    python scripts/migration_cli.py history
    python scripts/migration_cli.py check
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from alembic import command
from alembic.config import Config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def get_alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    return config


def upgrade(revision: str = "head") -> None:
    """Apply migrations up to the requested revision."""
    command.upgrade(get_alembic_config(), revision)


def downgrade(revision: str = "-1") -> None:
    """Revert migrations down to the requested revision."""
    command.downgrade(get_alembic_config(), revision)


def create_revision(message: str, *, autogenerate: bool = True) -> None:
    """Create a migration file, normally by comparing models to MySQL."""
    command.revision(
        get_alembic_config(),
        message=message,
        autogenerate=autogenerate,
    )


def current(verbose: bool = True) -> None:
    """Show the revision currently applied to the database."""
    command.current(get_alembic_config(), verbose=verbose)


def history(verbose: bool = True) -> None:
    """Show the migration chain."""
    command.history(get_alembic_config(), verbose=verbose)


def check() -> None:
    """Fail when model changes exist without a migration file."""
    command.check(get_alembic_config())


def stamp(revision: str = "head") -> None:
    """Set alembic_version without running upgrade or downgrade operations."""
    command.stamp(get_alembic_config(), revision)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Alembic migrations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upgrade_parser = subparsers.add_parser("upgrade")
    upgrade_parser.add_argument("revision", nargs="?", default="head")

    downgrade_parser = subparsers.add_parser("downgrade")
    downgrade_parser.add_argument("revision", nargs="?", default="-1")

    revision_parser = subparsers.add_parser("revision")
    revision_parser.add_argument("message")
    revision_parser.add_argument(
        "--empty",
        action="store_true",
        help="Create an empty migration instead of using autogenerate.",
    )

    subparsers.add_parser("current")
    subparsers.add_parser("history")
    subparsers.add_parser("check")

    stamp_parser = subparsers.add_parser("stamp")
    stamp_parser.add_argument("revision", nargs="?", default="head")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.command == "upgrade":
            upgrade(args.revision)
        elif args.command == "downgrade":
            downgrade(args.revision)
        elif args.command == "revision":
            create_revision(args.message, autogenerate=not args.empty)
        elif args.command == "current":
            current()
        elif args.command == "history":
            history()
        elif args.command == "check":
            check()
        elif args.command == "stamp":
            stamp(args.revision)
        else:
            raise RuntimeError(f"Unsupported command: {args.command}")
    except Exception as exc:
        print(f"Migration command failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
