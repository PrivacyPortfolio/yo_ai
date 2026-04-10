# core/messages/a2a_schemaLoader.py

import json
import os
from typing import Dict, Any
from referencing import Registry, Resource
from jsonschema.validators import validator_for

class A2ASchemaLoader:
    """
    Loads and resolves flattened A2A v1.0 schemas from local storage.
    Optimized for AWS Lambda layers and local repository migration.
    """
    
    def __init__(self, schema_dir: str = "schemas/v1.0"):
        self.schema_dir = schema_dir
        self.registry = Registry()
        self._schemas = {}
        self._load_all_files()

    def _load_all_files(self):
        """
        Crawls the schema directory to build a registry of all A2A v1.0 definitions.
        """
        for filename in os.listdir(self.schema_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.schema_dir, filename)
                with open(filepath, 'r') as f:
                    schema_content = json.load(f)
                    
                    # Register the schema by its $id (e.g., https://yo-ai.ai/schemas/v1/...)
                    # and by its local filename for relative resolution.
                    resource = Resource.from_contents(schema_content)
                    self.registry = resource.at(filename).at(self.registry)
                    
                    # Store main entry points for the Validator
                    if "a2a-request" in filename:
                        self._schemas["request"] = schema_content
                    elif "a2a-response" in filename:
                        self._schemas["response"] = schema_content
                    elif "standard-error" in filename:
                        self._schemas["error"] = schema_content

    def get_validator(self, schema_type: str):
        """
        Returns a pre-configured validator that knows how to resolve local A2A v1.0 references.
        """
        schema = self._schemas.get(schema_type)
        if not schema:
            raise ValueError(f"Schema type {schema_type} not found in {self.schema_dir}")
        
        # Automatically detects Draft 2020-12
        validator_cls = validator_for(schema)
        
        # Return validator instance with the pre-populated registry for $ref resolution
        return validator_cls(schema, registry=self.registry)

    def get_all_schemas(self) -> Dict[str, Any]:
        return self._schemas
