# src/dworshak_config/cli_argparse.py
"""
Argparse renderer for dworshak-config.

This module intentionally:
- Depends only on the Python standard library
- Is generated entirely from the declarative spec layer
- Preserves strict stdout/stderr contracts for scripting
- Serves as a robust fallback when Typer / Click are unavailable

This file should contain *no domain logic*.
"""

from __future__ import annotations

import argparse
import inspect
import sys
import traceback
from typing import Any, Callable
from typing import get_type_hints, get_origin, get_args
from collections.abc import Iterable

from .spec import COMMANDS, CommandSpec
from ._version import __version__

# ────────────────────────────────────────────────────────────────
# I/O helpers (never leak to stdout unintentionally)
# ────────────────────────────────────────────────────────────────

def stderr(msg: str) -> None:
    """Emit a message to stderr (safe for shell pipelines)."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def confirm(prompt: str) -> bool:
    """
    Minimal confirmation prompt.

    Uses [y/N] semantics and fails closed on EOF
    (important for non-interactive environments).
    """
    try:
        reply = input(f"{prompt} [y/N]: ").strip().lower()
        return reply in {"y", "yes"}
    except EOFError:
        return False


# ────────────────────────────────────────────────────────────────
# Argument inference
# ────────────────────────────────────────────────────────────────
def add_parameter(
    parser: argparse.ArgumentParser,
    param: inspect.Parameter,
    type_hints: dict[str, Any],
) -> None:
    """
    Translate a single function parameter into an argparse argument.

    Uses resolved runtime type hints (safe with __future__ annotations).
    """
    name = param.name
    default = param.default

    hinted_type = type_hints.get(name)
    has_default = default is not inspect.Parameter.empty

    # Resolve Optional[T] → T
    origin = get_origin(hinted_type)
    args = get_args(hinted_type)
    if origin is list or origin is tuple:
        arg_type = args[0]
    elif origin is not None and args:
        arg_type = args[0]
    else:
        arg_type = hinted_type

    is_bool = arg_type is bool

    if has_default:
        long_flag = f"--{name.replace('_', '-')}"
        short_flag = f"-{name[0]}"

        kwargs: dict[str, Any] = {
            "dest": name,
            "default": default,
        }

        if is_bool:
            kwargs["action"] = (
                "store_true" if default is False else "store_false"
            )
        else:
            kwargs["type"] = arg_type if callable(arg_type) else str

        parser.add_argument(long_flag, short_flag, **kwargs)

    else:
        parser.add_argument(
            name,
            type=arg_type if callable(arg_type) else str,
        )

def add_parameter_(
    parser: argparse.ArgumentParser,
    param: inspect.Parameter,
) -> None:
    """
    Translate a single function parameter into an argparse argument.

    Rules:
    - No default  → positional argument
    - Has default → optional flag
    - bool        → store_true / store_false
    """
    name = param.name
    annotation = param.annotation
    default = param.default

    has_default = default is not inspect.Parameter.empty
    is_bool = annotation is bool

    if has_default:
        long_flag = f"--{name.replace('_', '-')}"
        short_flag = f"-{name[0]}"

        kwargs: dict[str, Any] = {
            "dest": name,
            "default": default,
        }

        if is_bool:
            kwargs["action"] = (
                "store_true" if default is False else "store_false"
            )
        else:
            kwargs["type"] = annotation if annotation is not None else str

        parser.add_argument(long_flag, short_flag, **kwargs)

    else:
        parser.add_argument(
            name,
            type=annotation if annotation is not None else str,
        )


# ────────────────────────────────────────────────────────────────
# Parser construction
# ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argparse parser from the command spec.

    This function should remain free of domain knowledge.
    """
    parser = argparse.ArgumentParser(
        prog="dworshak-config",
        description="Store and retrieve plaintext configuration values",
        add_help=False,
    )

    # Global options (apply to all commands)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("--debug","-d", action="store_true", help="Enable diagnostic stack traces")
    parser.add_argument("--verbose","-v", action="store_true", help="Show details.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"dworshak-config {__version__}",
        help="Show the version and exit",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
    )

    for cmd in COMMANDS:
        sub = subparsers.add_parser(
            cmd.name,
            help=cmd.help,
            description=cmd.help,
            add_help=False,
        )

        sub.add_argument("-h", "--help", action="help", help="Show this help message and exit")

        #signature = inspect.signature(cmd.handler)
        #for param in signature.parameters.values():
        #    add_parameter(sub, param)

        signature = inspect.signature(cmd.handler)
        type_hints = get_type_hints(cmd.handler)

        for param in signature.parameters.values():
            add_parameter(sub, param, type_hints)

        # Attach spec object for dispatch
        sub.set_defaults(_command_spec=cmd)

    return parser


# ────────────────────────────────────────────────────────────────
# Dispatcher
# ────────────────────────────────────────────────────────────────

def dispatch(cmd: CommandSpec, args: argparse.Namespace) -> int:
    """
    Execute a command spec with parsed arguments.

    Returns an appropriate POSIX exit code.
    """
    kwargs = vars(args).copy()
    debug = kwargs.pop("debug", False)

    # Internal argparse fields
    kwargs.pop("_command_spec", None)
    kwargs.pop("command", None)

    # Confirmation gate (policy lives in spec, UI lives here)
    if cmd.needs_confirmation and not kwargs.get("yes", False):
        if not confirm(f"Are you sure you want to run '{cmd.name}'?"):
            stderr("Operation cancelled.")
            return 0

    try:
        result = cmd.handler(**kwargs)

        # Convention: iterable return values are rendered line-by-line
        """if result is not None:
            for row in result:
                if isinstance(row, (tuple, list)):
                    print("  ".join(map(str, row)))
                else:
                    print(row)
        """

        if result is not None:
            # Strings and bools are iterable-ish but not row data
            if isinstance(result, Iterable) and not isinstance(result, (str, bytes, bool)):
                for row in result:
                    if isinstance(row, (tuple, list)):
                        print("  ".join(map(str, row)))
                    else:
                        print(row)
            # Non-iterable return values are treated as status only

        return 0

    except KeyboardInterrupt:
        stderr("Interrupted.")
        return 130

    except Exception as exc:
        stderr(f"Error: {exc}")
        if debug:
            traceback.print_exc()
        return 1


# ────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "_command_spec"):
        parser.print_help()
        return 0

    return dispatch(args._command_spec, args)


if __name__ == "__main__":
    sys.exit(main())
