# dworshak-config

**dworshak-config** is a lightweight, zero-dependency library for managing nested JSON configurations. It serves as the standard storage backend for the Dworshak ecosystem, providing a stable way to persist non-sensitive application settings.

By decoupling storage from user interaction, `dworshak-config` ensures that your scripts can retrieve settings silently when they exist, leaving the "how to ask for them" to its sister package, [dworshak-prompt](https://github.com/City-of-Memphis-Wastewater/dworshak-prompt).

## Features

* **Zero Dependencies:** Pure Python standard library (`json` and `pathlib`).
* **Service-Oriented:** Organizes settings by `service` and `item` (e.g., `config["postgres"]["port"]`).
* **Atomic Persistence:** Automatically handles directory creation and pretty-printed JSON writes.
* **Fail-Safe Loading:** Gracefully handles corrupted or missing configuration files.

## Installation

```bash
uv add dworshak-config
# or
pip install dworshak-config

```

## Usage

### Basic I/O

The `DworshakConfig` is the primary interface for reading and writing data.

```python
from dworshak_config import DworshakConfig

# Uses default path: ~/.dworshak/config.json
cfg = DworshakConfig()

# Store a value
cfg.set_value("aws", "region", "us-east-1")

# Retrieve a value (returns None if missing)
region = cfg.get_value("aws", "region")
print(f"Targeting: {region}")

```

### Custom Configuration Paths

Perfect for project-specific settings that shouldn't live in the global Dworshak folder.

```python
from dworshak_config import DworshakConfig

# Point to a specific project file
project_cfg = DworshakConfig("./.my_project/config.json")
project_cfg.set_value("internal", "debug_mode", True)

```

## The Ecosystem Integration

While `dworshak-config` handles the **persistence**, it is designed to be orchestrated by `dworshak-prompt` for interactive workflows.

```python
# In your application using dworshak-prompt
from dworshak_prompt import DworshakGet

# This will:
# 1. Check ~/.dworshak/config.json for 'api_url'
# 2. If missing, prompt the user (Console/GUI/Web)
# 3. Save the answer back to config.json automatically
api_url = DworshakGet.config("my_service", "api_url")

```

## Configuration Schema

Data is stored in a clean, human-readable nested JSON format:

```json
{
    "aws": {
        "region": "us-east-1",
        "output": "json"
    },
    "rjn_api": {
        "base_url": "https://api.example.com"
    }
}

```

---

<a id="sister-project-dworshak-secret"></a>

## Sister Projects in the Dworshak Ecosystem

* **CLI/Orchestrator:** [dworshak](https://github.com/City-of-Memphis-Wastewater/dworshak)
* **Interactive UI:** [dworshak-prompt](https://github.com/City-of-Memphis-Wastewater/dworshak-prompt)
* **Secrets Storage:** [dworshak-secret](https://github.com/City-of-Memphis-Wastewater/dworshak-secret)
* **Plaintext Pathed Configs:** [dworshak-secret](https://github.com/City-of-Memphis-Wastewater/dworshak-config)
* **Classic .env Injection:** [dworshak-secret](https://github.com/City-of-Memphis-Wastewater/dworshak-env)

```python
pipx install dworshak
pip install dworshak-secret
pip install dworshak-config
pip install dworshak-env
pip install dworshak-prompt

```
