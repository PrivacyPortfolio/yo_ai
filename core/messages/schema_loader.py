# /core/messages/schema_loader.py -- Lightweight JSON Schema loader with caching

"""
Lightweight JSON Schema loader with caching.

Loads schemas from the local filesystem (your published schema folder)
and returns parsed dicts for validation or shaping.
"""

import json
from functools import lru_cache
from pathlib import Path


SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"


@lru_cache(maxsize=256)
def load_schema(schema_name: str) -> dict:
    """
    Load a JSON schema by filename (e.g., 'purchase.create.input.json').

    Raises FileNotFoundError if the schema does not exist.
    """
    schema_path = SCHEMA_ROOT / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)