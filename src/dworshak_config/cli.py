# src/dworshak_config/cli.py
import typer
from typer.models import OptionInfo
from rich.console import Console
import os
from pathlib import Path
from typing import Optional
try:
    from typer_helptree import add_typer_helptree
except:
    pass
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

try:
    add_typer_helptree(app=app, console=console, version = __version__,hidden=True)
except:
    pass
@app.command()
def get(
    service: str = typer.Argument(..., help="The service name (e.g., Maxson)."),
    item: str = typer.Argument(..., help="The item key (e.g., port)."),
    value: str = typer.Option(None, "--value", help="Identify a value."),
    path: Path = typer.Option(None, "--path", help="Custom config file path."),
):
    """
    Get or set a configuration value using Service and Item (vault-style, two-key).
    """
    manager = ConfigManager(path=path)
    
    value = manager.get(
        service=service,
        item=item,
    )
    if value:
        # Only print the value to stdout for piping/capture
        typer.echo(f"[{service}] {item} = {value}")

@app.command()
def set(
    service: str = typer.Argument(..., help="The service name (e.g., Maxson)."),
    item: str = typer.Argument(..., help="The item key (e.g., port)."),
    value: str = typer.Option(None, "--value", help="Directly set a value."),
    message: str = typer.Option(None, "--message", help="Custom prompt message."),
    path: Path = typer.Option(None, "--path", help="Custom config file path."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Force a new prompt.")
):
    """
    Get or set a configuration value using Service and Item (vault-style, two-key).
    """
    manager = ConfigManager(path=path)
    
    exisiting_value = manager.get(
        service=service,
        item=item,
    )
    if exisiting_value is not None :
        manager.get_value(service, item, value)
        display_existing_val = value
        typer.echo(f"Existing: [{service}] {item} = {display_existing_val}")

    if (exisiting_value is None) or (exisiting_value is not None and overwrite):
        value = manager.set(
            service=service,
            item=item,
            prompt_message=message,
            overwrite=overwrite
        )
    else:
        value =  exisiting_value
    
    if value:
        # Only print the value to stdout for piping/capture
        typer.echo(f"[{service}] {item} = {value}")

if __name__ == "__main__":
    app()

