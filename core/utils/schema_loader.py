# schema_loader.py - utilities for loading and validating JSON schemas
# yo_ai/core/utils/schema_loader.py

import json
from pathlib import Path
from typing import Dict, Any


class SchemaLoader:
    """
    Loads JSON Schemas for:
    - A2A request/response
    - Capability input/output schemas
    MVP version:
    - Reads JSON files
    - Caches them in memory
    """

    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def load(cls, path: str | Path) -> Dict[str, Any]:
        path = Path(path)

        if path in cls._cache:
            return cls._cache[path]

        if not path.exists():
            raise FileNotFoundError(f"Schema not found: {path}")

        schema = json.loads(path.read_text())
        cls._cache[path] = schema
        return schema

    @classmethod
    def load_directory(cls, directory: str | Path) -> Dict[str, Dict[str, Any]]:
        directory = Path(directory)
        schemas = {}

        for file in directory.glob("*.json"):
            schemas[file.stem] = cls.load(file)

        return schemas