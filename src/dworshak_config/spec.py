# src/dworshak_config/spec.py

from __future__ import annotations

from pathlib import Path
from typing import Optional, Callable, Any, Iterable

from .core import DworshakConfig


# ────────────────────────────
# Command metadata (lightweight, framework-agnostic)
# ────────────────────────────

class CommandSpec:
    """
    Declarative command specification.

    Renderers (Typer, argparse, etc.) should:
      - inspect `handler` signature + annotations
      - use `help` as command help
      - respect flags like `needs_confirmation`
    """
    def __init__(
        self,
        *,
        name: str,
        help: str,
        handler: Callable[..., Any],
        needs_confirmation: bool = False,
    ):
        self.name = name
        self.help = help
        self.handler = handler
        self.needs_confirmation = needs_confirmation


# ────────────────────────────
# Command handlers (THIS is the spec)
# ────────────────────────────

def get(
    service: str,
    item: str,
    path: Optional[Path] = None,
    debug: bool = False,
    verbose: bool = False,
):
    """
    Retrieve a configuration value (vault-style, two-key).
    """
    cfg = DworshakConfig(path=path)
    value = cfg.get(service, item)

    if value is not None:
        # stdout-only for scripting
        print(value)


def set(
    service: str,
    item: str,
    value: str,
    path: Optional[Path] = None,
    overwrite: bool = True,
    debug: bool = False,
    verbose: bool = False,
):
    """
    Store a configuration value (vault-style, two-key).
    """
    cfg = DworshakConfig(path=path)

    cfg.set(
        service=service,
        item=item,
        value=value,
        overwrite=overwrite,
    )

    # Read back the stored value and emit to stdout
    final_value = cfg.get(service, item)
    if final_value is not None:
        print(final_value)
    else:
        raise RuntimeError("Failed to read back stored value")


def remove(
    service: str,
    item: str,
    path: Optional[Path] = None,
    fail: bool = False,
    yes: bool = False,
    debug: bool = False,
    verbose: bool = False,
):
    """
    Remove a configuration value.
    """
    cfg = DworshakConfig(path=path)

    deleted = cfg.remove(service, item)
    if not deleted and fail:
        raise KeyError(f"No value found for {service}/{item}")

    return deleted


def list_entries(
    path: Optional[Path] = None,
    debug: bool = False,
    verbose: bool = False,
) -> Iterable[tuple[str, str, str]]:
    """
    List all stored configuration values.

    Returns iterable rows so renderers can decide formatting.
    """
    cfg = DworshakConfig(path=path)
    data = cfg.load()

    for service in sorted(data.keys()):
        items = data.get(service, {})
        if not isinstance(items, dict):
            continue
        for item in sorted(items.keys()):
            yield service, item, str(items[item])


# ────────────────────────────
# Registry (what renderers consume)
# ────────────────────────────

COMMANDS: list[CommandSpec] = [
    CommandSpec(
        name="get",
        help="Retrieve a configuration value",
        handler=get,
    ),
    CommandSpec(
        name="set",
        help="Store a configuration value",
        handler=set,
    ),
    CommandSpec(
        name="remove",
        help="Remove a configuration value",
        handler=remove,
        needs_confirmation=True,  # renderer decides how to ask
    ),
    CommandSpec(
        name="list",
        help="List all stored configuration values",
        handler=list_entries,
    ),
]
