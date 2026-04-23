# a2a_schema.py

"""
Loads and resolves flattened A2A v1.0 schemas from local storage.
Optimized for AWS Lambda layers and local repository migration.
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path
from referencing import Registry, Resource
from jsonschema.validators import validator_for
from jsonschema import ValidationError
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("a2a_schema")


class A2ASchemaError(Exception):
    pass


class A2ASchemaLoader:
    def __init__(self, version: str = "v1.0", base_dir: Path | None = None):
        self.version = version
        self.base_dir = base_dir or Path(__file__).resolve().parents[2] / "schemas" / "a2a" / version
        self.registry = Registry()
        self._schemas: Dict[str, dict] = {}
        self._validators: Dict[str, Any] = {}

        self._load_all_files()
        self._build_validators()

    def _load_all_files(self) -> None:
        if not self.base_dir.exists():
            msg = f"A2A schema directory not found: {self.base_dir}"
            LOG.error(msg)
            raise A2ASchemaError(msg)

        for filename in os.listdir(self.base_dir):
            if not filename.endswith(".json"):
                continue

            path = self.base_dir / filename
            try:
                with path.open("r", encoding="utf-8") as f:
                    schema = json.load(f)
            except Exception as e:
                msg = f"Failed to load A2A schema '{path}': {e}"
                LOG.exception(msg)
                raise A2ASchemaError(msg) from e

            resource = Resource.from_contents(schema)
            # Register by filename as a simple, stable key
            self.registry = resource.at(filename).at(self.registry)

            # Map entrypoints by convention
            name = filename.lower()
            if "a2a-request" in name:
                self._schemas["request"] = schema
            elif "a2a-response" in name:
                self._schemas["response"] = schema
            elif "standard-error" in name:
                self._schemas["error"] = schema

        missing = [k for k in ("request", "response", "error") if k not in self._schemas]
        if missing:
            msg = f"Missing required A2A schemas: {missing}"
            LOG.error(msg)
            raise A2ASchemaError(msg)

    def _build_validators(self) -> None:
        for key, schema in self._schemas.items():
            try:
                cls = validator_for(schema)
                self._validators[key] = cls(schema, registry=self.registry)
            except Exception as e:
                msg = f"Failed to build validator for A2A schema '{key}': {e}"
                LOG.exception(msg)
                raise A2ASchemaError(msg) from e

    def validate(self, schema_type: str, data: Dict[str, Any]) -> None:
        """Raise ValidationError on failure."""
        validator = self._validators.get(schema_type)
        if not validator:
            msg = f"Unknown A2A schema type: {schema_type}"
            LOG.error(msg)
            raise A2ASchemaError(msg)

        LOG.debug("Validating A2A %s payload: %s", schema_type, data)
        validator.validate(data)

    def iter_errors(self, schema_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        validator = self._validators.get(schema_type)
        if not validator:
            msg = f"Unknown A2A schema type: {schema_type}"
            LOG.error(msg)
            raise A2ASchemaError(msg)

        errors = []
        for err in validator.iter_errors(data):
            entry = {
                "path": list(err.path),
                "message": err.message,
                "context": [e.message for e in err.context] if err.context else [],
                "validator": err.validator,
            }
            errors.append(entry)
        LOG.debug("A2A %s validation errors: %s", schema_type, errors)
        return errors
