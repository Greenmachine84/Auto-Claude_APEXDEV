"""Schema validation for structured data.

World-Class Standards:
- JSON Schema validation
- Custom schema support
- Nested object validation
- Clear error messages
"""
import json
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from ..models import ValidationResult


@dataclass
class SchemaField:
    """Definition of a schema field."""
    name: str
    field_type: str  # string, number, integer, boolean, array, object
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None
    enum: Optional[List[Any]] = None
    items: Optional["SchemaField"] = None  # For arrays
    properties: Dict[str, "SchemaField"] = field(default_factory=dict)


class SchemaValidator:
    """Validates data against schemas.
    
    Supports:
    - JSON Schema-like validation
    - Custom schema definitions
    - Nested object validation
    - Array validation
    
    Example:
        validator = SchemaValidator()
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0},
            },
            "required": ["name"],
        }
        
        result = validator.validate({"name": "John", "age": 30}, schema)
    """
    
    # Type validators
    TYPE_VALIDATORS = {
        "string": lambda x: isinstance(x, str),
        "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "boolean": lambda x: isinstance(x, bool),
        "array": lambda x: isinstance(x, list),
        "object": lambda x: isinstance(x, dict),
        "null": lambda x: x is None,
    }
    
    def validate(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str = "$",
    ) -> ValidationResult:
        """Validate data against schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema-like schema
            path: Current path for error messages
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # Get expected type
        expected_type = schema.get("type")
        if expected_type:
            if not self._validate_type(data, expected_type):
                errors.append(
                    f"{path}: Expected type '{expected_type}', got '{type(data).__name__}'"
                )
                return ValidationResult(valid=False, errors=errors)
        
        # Type-specific validation
        if isinstance(data, str):
            errors.extend(self._validate_string(data, schema, path))
        elif isinstance(data, (int, float)) and not isinstance(data, bool):
            errors.extend(self._validate_number(data, schema, path))
        elif isinstance(data, list):
            result = self._validate_array(data, schema, path)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        elif isinstance(data, dict):
            result = self._validate_object(data, schema, path)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        
        # Enum validation
        if "enum" in schema:
            if data not in schema["enum"]:
                errors.append(
                    f"{path}: Value must be one of {schema['enum']}"
                )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_type(self, data: Any, expected_type: Union[str, List[str]]) -> bool:
        """Check if data matches expected type."""
        if isinstance(expected_type, list):
            return any(
                self.TYPE_VALIDATORS.get(t, lambda x: False)(data)
                for t in expected_type
            )
        return self.TYPE_VALIDATORS.get(expected_type, lambda x: False)(data)
    
    def _validate_string(self, data: str, schema: Dict, path: str) -> List[str]:
        """Validate string constraints."""
        errors = []
        
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(
                f"{path}: String length {len(data)} is less than minimum {schema['minLength']}"
            )
        
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(
                f"{path}: String length {len(data)} exceeds maximum {schema['maxLength']}"
            )
        
        if "pattern" in schema:
            if not re.match(schema["pattern"], data):
                errors.append(
                    f"{path}: String does not match pattern '{schema['pattern']}'"
                )
        
        return errors
    
    def _validate_number(self, data: float, schema: Dict, path: str) -> List[str]:
        """Validate number constraints."""
        errors = []
        
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(
                f"{path}: Value {data} is less than minimum {schema['minimum']}"
            )
        
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(
                f"{path}: Value {data} exceeds maximum {schema['maximum']}"
            )
        
        if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
            errors.append(
                f"{path}: Value {data} must be greater than {schema['exclusiveMinimum']}"
            )
        
        if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
            errors.append(
                f"{path}: Value {data} must be less than {schema['exclusiveMaximum']}"
            )
        
        if "multipleOf" in schema:
            if data % schema["multipleOf"] != 0:
                errors.append(
                    f"{path}: Value {data} must be multiple of {schema['multipleOf']}"
                )
        
        return errors
    
    def _validate_array(self, data: list, schema: Dict, path: str) -> ValidationResult:
        """Validate array constraints."""
        errors = []
        warnings = []
        
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(
                f"{path}: Array length {len(data)} is less than minimum {schema['minItems']}"
            )
        
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(
                f"{path}: Array length {len(data)} exceeds maximum {schema['maxItems']}"
            )
        
        if "uniqueItems" in schema and schema["uniqueItems"]:
            # Check for duplicates (simple values only)
            try:
                if len(data) != len(set(json.dumps(item, sort_keys=True) for item in data)):
                    errors.append(f"{path}: Array must contain unique items")
            except TypeError:
                pass  # Can't serialize, skip check
        
        # Validate items
        if "items" in schema:
            for i, item in enumerate(data):
                item_result = self.validate(item, schema["items"], f"{path}[{i}]")
                errors.extend(item_result.errors)
                warnings.extend(item_result.warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_object(self, data: dict, schema: Dict, path: str) -> ValidationResult:
        """Validate object constraints."""
        errors = []
        warnings = []
        
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)
        
        # Check required fields
        for field in required:
            if field not in data:
                errors.append(f"{path}: Missing required field '{field}'")
        
        # Validate properties
        for key, value in data.items():
            if key in properties:
                prop_result = self.validate(
                    value,
                    properties[key],
                    f"{path}.{key}",
                )
                errors.extend(prop_result.errors)
                warnings.extend(prop_result.warnings)
            elif not additional:
                errors.append(f"{path}: Additional property '{key}' not allowed")
            elif isinstance(additional, dict):
                # Additional properties must match schema
                prop_result = self.validate(value, additional, f"{path}.{key}")
                errors.extend(prop_result.errors)
                warnings.extend(prop_result.warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def validate_json(self, json_string: str, schema: Dict) -> ValidationResult:
        """Validate a JSON string against schema.
        
        Args:
            json_string: JSON string to validate
            schema: Schema to validate against
            
        Returns:
            ValidationResult
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {e.msg} at position {e.pos}"],
            )
        
        return self.validate(data, schema)
    
    def create_schema_from_sample(self, sample: Any) -> Dict:
        """Create a schema from a sample data structure.
        
        Args:
            sample: Sample data to infer schema from
            
        Returns:
            Inferred schema
        """
        if sample is None:
            return {"type": "null"}
        elif isinstance(sample, bool):
            return {"type": "boolean"}
        elif isinstance(sample, int):
            return {"type": "integer"}
        elif isinstance(sample, float):
            return {"type": "number"}
        elif isinstance(sample, str):
            return {"type": "string"}
        elif isinstance(sample, list):
            if sample:
                # Infer from first item
                return {
                    "type": "array",
                    "items": self.create_schema_from_sample(sample[0]),
                }
            return {"type": "array"}
        elif isinstance(sample, dict):
            properties = {
                key: self.create_schema_from_sample(value)
                for key, value in sample.items()
            }
            return {
                "type": "object",
                "properties": properties,
                "required": list(sample.keys()),
            }
        else:
            return {}
