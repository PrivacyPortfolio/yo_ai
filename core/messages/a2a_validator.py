# core/messages/a2a_validator.py

"""
A2A v1.0 Validator

Validates A2A protocol messages against official schemas from:
https://a2a-protocol.org/latest/spec/a2a.json

Usage:
    from a2a_validator import A2AValidator
    
    validator = A2AValidator()
    
    if validator.validate_request(data):
        # Valid A2A request
    else:
        errors = validator.get_validation_errors(data, "request")
"""

from typing import Dict, Any, List
from jsonschema import ValidationError
from .a2a_schema import A2ASchemaLoader


class A2AValidator:
    def __init__(self, version: str = "v1.0"):
        self.loader = A2ASchemaLoader(version=version)

    def validate_request(self, data: Dict[str, Any]) -> None:
        self.loader.validate("request", data)

    def validate_response(self, data: Dict[str, Any]) -> None:
        self.loader.validate("response", data)

    def validate_error(self, data: Dict[str, Any]) -> None:
        self.loader.validate("error", data)

    def get_validation_errors(self, schema_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.loader.iter_errors(schema_type, data)
