# # core/utils/validators/input_validator.py -- Validate incoming payloads against JSON Schemas
"""
Thin wrapper around jsonschema.validate with your platform conventions.

This module validates incoming payloads against the declared Input schema.
"""

from jsonschema import validate, ValidationError
from ..schema_loader import load_schema


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_input(payload: dict, schema_name: str) -> None:
    """
    Validate the incoming payload against the given schema.

    Raises InputValidationError on failure.
    """
    try:
        schema = load_schema(schema_name)
        validate(instance=payload, schema=schema)
    except ValidationError as e:
        raise InputValidationError(str(e)) from e