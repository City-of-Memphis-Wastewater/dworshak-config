# src/dworshak_config/logging_setup.py
from __future__ import annotations
import logging
import sys
from rich.logging import RichHandler
from rich.console import Console
console = Console(stderr=True)

def configure_root_logging_for_application(debug: bool):
    INTENT="app"
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    level = logging.DEBUG if debug else logging.WARNING
    root_logger.setLevel(level)
    handler = RichHandler(console=console, show_time=debug, show_path=debug,log_time_format="[%H:%M:%S]")
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    root_logger.debug(f"Debug logging enabled for {INTENT}.")
