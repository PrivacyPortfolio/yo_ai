# core/utils/ai/output_shaper.py
# This module ensures the AI output conforms to the declared Output schema.
# It does not validate — your existing validator handles that.
# It shapes, normalizes, and fills missing fields when possible.

"""
Output Shaper

Responsibilities:
- Normalize AI output into the structure required by the Output schema
- Fill missing fields with None or defaults
- Ensure predictable, schema-aligned envelopes for A2A governance
"""

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("output_shaper")


def shape_output(ai_result: dict, output_schema: dict) -> dict:
    """
    Shapes the AI result to match the Output schema.

    Parameters:
        ai_result (dict): raw AI output (may be incomplete or unstructured)
        output_schema (dict): JSON Schema for the capability output

    Returns:
        dict: shaped output matching the schema structure
    """

    if not isinstance(ai_result, dict):
        LOG.warning("[OutputShaper] AI result was not a dict; wrapping")
        ai_result = {"value": ai_result}

    shaped = {}

    # ------------------------------------------------------------
    # 1. Extract expected fields from schema
    # ------------------------------------------------------------
    properties = output_schema.get("properties", {})

    for field, definition in properties.items():
        if field in ai_result:
            shaped[field] = ai_result[field]
        else:
            # Fill missing fields with None or default
            default = definition.get("default")
            shaped[field] = default if default is not None else None

    # ------------------------------------------------------------
    # 2. Preserve any extra AI fields (optional)
    # ------------------------------------------------------------
    shaped["_ai"] = {
        "raw": ai_result,
        "note": "Unmapped fields preserved for debugging"
    }

    LOG.info("[OutputShaper] Output shaped successfully")
    return shaped
