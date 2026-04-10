# core/messages/schema_validator.py

"""
Unified JSON Schema validation utilities for Yo-AI agents.

This module provides:
  - Input validation
  - Output validation
  - Schema loading (URL or local)
  - Schema self-validation
  - Caching for performance

It is designed to be used by the unified Lambda entrypoint.
"""

import json
import urllib.request
from functools import lru_cache
from jsonschema import Draft202012Validator, ValidationError, RefResolver


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SchemaLoadError(Exception):
    """Raised when a schema cannot be fetched or parsed."""
    pass

class InputValidationError(Exception):
    """Raised when input envelope validation fails."""
    pass

class OutputValidationError(Exception):
    """Raised when output envelope validation fails."""
    pass

class SchemaValidationError(Exception):
    """Raised when a schema itself is invalid."""
    pass


# ---------------------------------------------------------------------------
# Schema loading + caching
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def load_schema(schema_url: str) -> dict:
    """
    Load a JSON Schema from an absolute URL or local file path.
    Cached for performance.
    """
    try:
        if schema_url.startswith("http://") or schema_url.startswith("https://"):
            with urllib.request.urlopen(schema_url) as response:
                return json.loads(response.read().decode("utf-8"))
        else:
            # Local file path
            with open(schema_url, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        raise SchemaLoadError(f"Failed to load schema '{schema_url}': {e}") from e


# ---------------------------------------------------------------------------
# Schema self-validation (optional but recommended)
# ---------------------------------------------------------------------------

def validate_schema(schema: dict) -> None:
    """
    Validate that a schema is itself a valid JSON Schema.
    Raises SchemaValidationError on failure.
    """
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        raise SchemaValidationError(f"Invalid JSON Schema: {e}") from e


# ---------------------------------------------------------------------------
# Validator caching
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def _get_validator(schema_url: str) -> Draft202012Validator:
    """
    Fetch + compile a JSON Schema validator for the given URL.
    """
    schema = load_schema(schema_url)
    validate_schema(schema)  # optional but safe

    resolver = RefResolver(base_uri=schema_url, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_input(schema_url: str, payload: dict) -> None:
    """
    Validate an input envelope against its schema.
    Raises InputValidationError on failure.
    """
    try:
        validator = _get_validator(schema_url)
        validator.validate(payload)
    except ValidationError as e:
        raise InputValidationError(str(e)) from e


def validate_output(schema_url: str, payload: dict) -> None:
    """
    Validate an output envelope against its schema.
    Raises OutputValidationError on failure.
    """
    try:
        validator = _get_validator(schema_url)
        validator.validate(payload)
    except ValidationError as e:
        raise OutputValidationError(str(e)) from e