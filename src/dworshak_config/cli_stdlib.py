import sys
import argparse
import traceback
from pathlib import Path
from typing import Optional

from .dworshak_config import ConfigManager
from ._version import __version__

def stdlib_notify(msg: str):
    """Print to stderr so it doesn't break shell piping."""
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dworshak-config",
        description=f"Store and retrieve plaintext configuration values to JSON (v{__version__})",
        add_help=False # Consistent with your prompt-cli style
    )
    
    # Standard argparse help needs to be added back if add_help=False
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", action="store_true", help="Enable diagnostic stack traces")
    
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # --- GET Command ---
    get_p = subparsers.add_parser("get", help="Retrieve a configuration value", add_help=False)
    get_p.add_argument("service", help="The service name")
    get_p.add_argument("item", help="The item key")
    get_p.add_argument("--path", type=Path, help="Custom config file path")
    get_p.add_argument("-h", "--help", action="help", help="Show this help")

    # --- SET Command ---
    set_p = subparsers.add_parser("set", help="Store a configuration value", add_help=False)
    set_p.add_argument("service", help="The service name")
    set_p.add_argument("item", help="The item key")
    set_p.add_argument("value", help="The value to store")
    set_p.add_argument("--path", type=Path, help="Custom config file path")
    set_p.add_argument("-h", "--help", action="help", help="Show this help")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        manager = ConfigManager(path=args.path)

        if args.command == "get":
            value = manager.get(args.service, args.item)
            if value is not None:
                # Direct match to Typer output
                print(f"[{args.service}] {args.item} = {value}")
                return 0
            else:
                stdlib_notify(f"Error: [{args.service}] {args.item} not found.")
                return 1

        elif args.command == "set":
            manager.set(args.service, args.item, args.value)
            stdlib_notify(f"Stored [{args.service}] {args.item} successfully.")
            print(f"[{args.service}] {args.item} = {args.value}")
            return 0

    except KeyboardInterrupt:
        stdlib_notify("\nInterrupted.")
        return 130
    except Exception as e:
        stdlib_notify(f"Error: {e}")
        if args.debug:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())