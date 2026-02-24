# src/dworshak_config/core.py
from pathlib import Path
import json
import logging
from typing import Any, List

logger = logging.getLogger("dworshak_config")

DEFAULT_CONFIG_PATH = Path.home() / ".dworshak" / "config.json"

class DworshakConfig:
    def __init__(self, path: str | Path | None = None):
        if path and Path(path).exists() and str(path).endswith(".json"):
            self.path = Path(path)
        else:
            self.path = DEFAULT_CONFIG_PATH

    def _load(self) -> dict:
        """Loads the nested JSON config."""
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"⚠️ Warning: Config file '{self.path}' is corrupted: {e}")
            return {}

    def _save(self, config: dict):
        """Saves the nested JSON config."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"⚠️ Failed to save configuration to {self.path}: {e}")

    def get(self, service: str, item: str) -> str | None:
        """Pure I/O: Retrieve from JSON, return None if missing."""
        config = self._load()
        return config.get(service, {}).get(item)

    def set(self, service: str, item: str, value: Any, overwrite: bool = True):
        """Pure I/O: Store value in JSON."""
        config = self._load()

        if not overwrite and service in config and item in config[service]:
            logger.warning(
                f"Skipping set of {service}/{item} — already exists and overwrite=False"
            )
            return
        """
        if not overwrite:
            if service in config and item in config[service]:
                raise FileExistsError(
                    f"Configuration for {service}/{item} already exists "
                    f"(use overwrite=True to update)."
                )
        """        
        # config.setdefault(service, {})[item] = value
        if service not in config:
            config[service] = {}
        config[service][item] = value
        self._save(config)

    def remove(self, service: str, item: str) -> bool:
        """
        Remove a specific service/item entry if it exists.

        Returns:
            True if an entry was removed, False if it didn't exist.
        """
        config = self._load()
        if service not in config or item not in config[service]:
            return False

        del config[service][item]

        # Clean up empty service dicts (optional but nice)
        if not config[service]:
            del config[service]

        self._save(config)
        return True

    def list_configs(self) -> List[tuple[str, str]]:
        """
        Return a list of all (service, item) pairs that exist in the config.
        """
        config = self._load()
        result = []
        for service, items in config.items():
            if isinstance(items, dict):
                for item in items:
                    result.append((service, item))
        return result