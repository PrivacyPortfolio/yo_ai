# core/messages/validator.py

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
from a2a_schemaLoader import A2ASchemaLoader


class A2AValidator:
    """
    Validates A2A v1.0 messages using Draft 2020-12 schemas.
    Supports local $ref resolution for flattened schema bundles.
    """
    
    def __init__(self, version: str = "v1.0"):
        # Point the loader to the specific version directory
        self.loader = A2ASchemaLoader(schema_dir=f"schemas/{version}")
        self._validators = {
            "request": self.loader.get_validator("request"),
            "response": self.loader.get_validator("response"),
            "error": self.loader.get_validator("error")
        }
            
    def validate_request(self, data: Dict[str, Any]) -> bool:
        """Validate an A2A request (e.g., send_message, stream_message)."""
        try:
            self._validators["request"].validate(data)
            return True
        except Exception:
            return False
    
    def validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate an A2A response with v1.0 metadata and status."""
        try:
            self._validators["response"].validate(data)
            return True
        except Exception:
            return False
    
    def validate_error(self, data: Dict[str, Any]) -> bool:
        """Validate standardized v1.0 error objects."""
        try:
            self._validators["error"].validate(data)
            return True
        except Exception:
            return False

    def get_validation_errors(self, data: Dict[str, Any], schema_type: str) -> List[Dict[str, Any]]:
        """
        Retrieves detailed errors, essential for debugging mandatory v1.0 
        fields like taskID and correlationID.
        """
        errors = []
        validator = self._validators.get(schema_type)
        
        if not validator:
            return [{"error": f"Unknown or uninitialized schema type: {schema_type}"}]
        
        # iter_errors handles the 2020-12 validation tree via the registry
        for error in validator.iter_errors(data):
            errors.append({
                "path": list(error.path),
                "message": error.message,
                "context": [e.message for e in error.context] if error.context else [],
                "validator": error.validator,
            })
        
        return errors
