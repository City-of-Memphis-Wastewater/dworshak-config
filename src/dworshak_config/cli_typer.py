# src/dworshak_config/cli_typer.py
"""
Typer renderer for dworshak-config.

This module:
- Depends on Typer only
- Is generated entirely from the declarative spec layer
- Mirrors argparse behavior and exit codes
- Contains no domain logic
"""

from __future__ import annotations

import inspect
import sys
import traceback
from typing import Any, Callable, get_type_hints
import typer

from .spec import COMMANDS, CommandSpec


# ────────────────────────────────────────────────────────────────
# App
# ────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="dworshak-config",
    help="Store and retrieve plaintext configuration values",
    add_completion=False,
)


# ────────────────────────────────────────────────────────────────
# Utilities
# ────────────────────────────────────────────────────────────────

def stderr(msg: str) -> None:
    typer.echo(msg, err=True)


def confirm(prompt: str) -> bool:
    """Minimal [y/N] confirmation prompt."""
    return typer.confirm(prompt, default=False, abort=False)


def dispatch(
    cmd: CommandSpec,
    handler: Callable[..., Any],
    **kwargs: Any,
) -> None:
    """
    Execute a command handler with shared error / confirmation policy.

    Typer handles exit codes via exceptions.
    """
    debug = kwargs.pop("debug", False)

    if cmd.needs_confirmation and not kwargs.get("yes", False):
        if not confirm(f"Are you sure you want to run '{cmd.name}'?"):
            stderr("Operation cancelled.")
            raise typer.Exit(code=0)

    try:
        result = handler(**kwargs)

        # Iterable results are rendered line-by-line
        if result is not None:
            if isinstance(result, (str, bytes, bool)):
                return

            try:
                for row in result:
                    if isinstance(row, (tuple, list)):
                        typer.echo("  ".join(map(str, row)))
                    else:
                        typer.echo(row)
            except TypeError:
                # Non-iterable return value → status only
                pass

    except KeyboardInterrupt:
        stderr("Interrupted.")
        raise typer.Exit(code=130)

    except Exception as exc:
        stderr(f"Error: {exc}")
        if debug:
            traceback.print_exc()
        raise typer.Exit(code=1)


# ────────────────────────────────────────────────────────────────
# Command registration
# ────────────────────────────────────────────────────────────────

def register_command(cmd: CommandSpec) -> None:
    raw_signature = inspect.signature(cmd.handler)
    type_hints = get_type_hints(cmd.handler)

    parameters = []
    for name, param in raw_signature.parameters.items():
        if name in type_hints:
            param = param.replace(annotation=type_hints[name])
        parameters.append(param)

    signature = raw_signature.replace(parameters=parameters)

    def command_wrapper(**kwargs: Any) -> None:
        return dispatch(cmd, cmd.handler, **kwargs)

    command_wrapper.__name__ = cmd.name
    command_wrapper.__doc__ = cmd.handler.__doc__
    command_wrapper.__signature__ = signature

    app.command(
        name=cmd.name,
        help=cmd.help,
    )(command_wrapper)

def register_command_(cmd: CommandSpec) -> None:
    """
    Register a CommandSpec as a Typer command.

    Signature + annotations are preserved automatically.
    """
    signature = inspect.signature(cmd.handler)

    def command_wrapper(**kwargs: Any) -> None:
        return dispatch(cmd, cmd.handler, **kwargs)

    # Preserve metadata for Typer / help output
    command_wrapper.__name__ = cmd.name
    command_wrapper.__doc__ = cmd.handler.__doc__
    command_wrapper.__signature__ = signature

    app.command(
        name=cmd.name,
        help=cmd.help,
    )(command_wrapper)


for cmd in COMMANDS:
    register_command(cmd)


# ────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────

def main() -> None:
    app()


if __name__ == "__main__":
    main()
