# src/dworshak_config/cli.py
import typer
from typer.models import OptionInfo
from rich.console import Console
import os
from pathlib import Path
from typing import Optional

from .dworshak_config import ConfigManager
from ._version import __version__


console = Console() # to be above the tkinter check, in case of console.print
app = typer.Typer()

# Force Rich to always enable colors, even when running from a .pyz bundle
os.environ["FORCE_COLOR"] = "1"
# Optional but helpful for full terminal feature detection
os.environ["TERM"] = "xterm-256color"

app = typer.Typer(
    name="dworshak-config",
    help=f"Store and retrieve plaintext configuration values to JSON. (v{__version__})",
    no_args_is_help=True,
    add_completion=False,
    context_settings={"ignore_unknown_options": True,
                      "help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context,
    version: Optional[bool] = typer.Option(
    None, "--version", is_flag=True, help="Show the version."
    )
    ):
    """
    Enable --version
    """
    if version:
        typer.echo(__version__)
        raise typer.Exit(code=0)


@app.command()
def config(
    service: str = typer.Argument(..., help="The service name (e.g., Maxson)."),
    item: str = typer.Argument(..., help="The item key (e.g., port)."),
    value: str = typer.Option(None, "--set", help="Directly set a value."),
    message: str = typer.Option(None, "--message", help="Custom prompt message."),
    path: Path = typer.Option(None, "--path", help="Custom config file path."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Force a new prompt."),
    hide: bool = typer.Option(False, "--hide", help="Mask input for sensitive info."),
):
    """
    Get or set a configuration value using Service and Item (Vault-style).
    """
    manager = ConfigManager(path=path)
    
    if value is not None:
        manager.set_value(service, item, value)
        display_val = "***" if hide else value
        typer.echo(f"Stored: [{service}] {item} = {display_val}")
    else:
        result = manager.get(
            service=service,
            item=item,
            prompt_message=message,
            overwrite=overwrite,
            hide_input=hide
        )
        if result:
            # Only print the result to stdout for piping/capture
            print(result)

if __name__ == "__main__":
    app()

