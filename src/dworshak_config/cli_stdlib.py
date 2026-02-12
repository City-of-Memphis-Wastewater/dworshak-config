import sys
import argparse
from pathlib import Path
from typing import Optional

from .dworshak_config import ConfigManager
from ._version import __version__

def print_err(msg: str):
    """Print to stderr so it doesn't break shell piping."""
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def main():
    parser = argparse.ArgumentParser(
        prog="dworshak-config",
        description=f"Store and retrieve plaintext configuration values to JSON (v{__version__})"
    )
    parser.add_argument("--version", action="version", version=__version__)
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # --- GET Command ---
    get_parser = subparsers.add_parser("get", help="Retrieve a configuration value")
    get_parser.add_argument("service", help="The service name (e.g., Maxson)")
    get_parser.add_argument("item", help="The item key (e.g., port)")
    get_parser.add_argument("--path", type=Path, help="Custom config file path")

    # --- SET Command ---
    set_parser = subparsers.add_parser("set", help="Store a configuration value")
    set_parser.add_argument("service", help="The service name")
    set_parser.add_argument("item", help="The item key")
    set_parser.add_argument("value", help="The value to store")
    set_parser.add_argument("--path", type=Path, help="Custom config file path")

    args = parser.parse_args()

    # Handle no command provided
    if not args.command:
        parser.print_help()
        sys.exit(0)

    manager = ConfigManager(path=args.path)

    if args.command == "get":
        value = manager.get(args.service, args.item)
        if value is not None:
            # Print format matches your Typer CLI for consistency
            print(f"[{args.service}] {args.item} = {value}")
        else:
            print_err(f"Error: [{args.service}] {args.item} not found.")
            sys.exit(1)

    elif args.command == "set":
        manager.set(args.service, args.item, args.value)
        # Status message to stderr
        print_err(f"Stored [{args.service}] {args.item} successfully.")
        # Final output to stdout
        print(f"[{args.service}] {args.item} = {args.value}")

if __name__ == "__main__":
    main()