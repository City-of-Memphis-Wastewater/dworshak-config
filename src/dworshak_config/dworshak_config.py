# src/dworshak_config/dworshak_config.py
from pathlib import Path
import json
import logging
from typing import Any

logger = logging.getLogger("dworshak_config")

DEFAULT_CONFIG_PATH = Path.home() / ".dworshak" / "config.json"

class ConfigManager:
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

    def set(self, service: str, item: str, value: Any):
        """Pure I/O: Store value in JSON."""
        config = self._load()
        # config.setdefault(service, {})[item] = value
        if service not in config:
            config[service] = {}
        config[service][item] = value
        self._save(config)
