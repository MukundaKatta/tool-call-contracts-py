"""tool_call_contracts -- validate LLM tool-call payloads with small JSON-like contracts.

Public API:
    validate_tool_call(call, contract) -> ValidationResult
    assert_tool_call(call, contract) -> dict (raises ContractError on failure)
"""

import re
from dataclasses import dataclass
from typing import Any, Optional


_TYPE_MAP = {
    "string": str,
    "str": str,
    "number": (int, float),
    "int": int,
    "integer": int,
    "float": float,
    "boolean": bool,
    "bool": bool,
    "object": dict,
    "dict": dict,
    "array": list,
    "list": list,
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str]


class ContractError(Exception):
    """Raised by assert_tool_call when validation fails."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_tool_call(call: dict, contract: dict) -> ValidationResult:
    """Validate a tool call against a contract.

    Contract shape:
        {
            "name": "search",
            "arguments": {
                "query": {"type": "string", "required": True, "pattern": "..."},
                "limit": {"type": "int", "required": False, "enum": [10, 25, 50]},
            },
        }
    """
    errors: list[str] = []

    expected_name = contract.get("name")
    actual_name = call.get("name") if isinstance(call, dict) else None
    if expected_name is not None and actual_name != expected_name:
        errors.append(f"expected tool {expected_name}, got {actual_name}")

    args = (call.get("arguments") if isinstance(call, dict) else None) or {}
    rules = contract.get("arguments") or {}

    for key, rule in rules.items():
        rule = rule or {}
        value = args.get(key)
        if rule.get("required") and value is None and key not in args:
            errors.append(f"{key} is required")
            continue
        if value is None:
            continue
        type_name = rule.get("type")
        if type_name:
            py_type = _TYPE_MAP.get(type_name)
            if py_type and not isinstance(value, py_type):
                errors.append(f"{key} must be {type_name}")
            elif py_type is None:
                errors.append(f"{key} unknown type {type_name}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{key} must be one of {', '.join(map(str, rule['enum']))}")
        if isinstance(value, str) and "pattern" in rule:
            try:
                if not re.search(rule["pattern"], value):
                    errors.append(f"{key} does not match {rule['pattern']}")
            except re.error:
                errors.append(f"{key} pattern invalid: {rule['pattern']}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def assert_tool_call(call: dict, contract: dict) -> dict:
    """Validate or raise ContractError. Returns the call dict on success."""
    result = validate_tool_call(call, contract)
    if not result.valid:
        raise ContractError(result.errors)
    return call


__version__ = "0.1.0"
__all__ = ["validate_tool_call", "assert_tool_call", "ValidationResult", "ContractError"]
