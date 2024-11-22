import os
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from loguru import logger


class Params(dict):
    def __getattr__(self, key) -> Any:
        try:
            value = self[key]
            return Params(value) if isinstance(value, dict) else value
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute '{key}'",
            ) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k) from None


@cache
def load_params_yaml(path: Path) -> Params:
    logger.info(f"Loading params from {path} file.")
    if not path.exists():
        raise FileNotFoundError("params.yaml not found at path.")
    with path.open() as f:
        params = yaml.safe_load(f)
    return Params(params)


_params_file_path = os.getenv("PARAMS_YAML_PATH", "params.yaml")
params = load_params_yaml(Path(_params_file_path))
