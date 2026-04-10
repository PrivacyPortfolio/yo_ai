# tools/Data_Vault/runtime/vault_adapter_tool.py
#
# Architecture note:
#   VaultAdapterTool is wired manually — it is NOT loaded from x-artifacts
#   by bootstrap_tools.py. The vault adapter requires an injected dependency
#   (the vault client) that cannot be resolved from card config alone.
#
#   Manual wiring pattern (in the agent or its handler):
#       from tools.Data_Vault.runtime.vault_adapter_tool import VaultAdapterTool
#       vault_tool = VaultAdapterTool(vault_adapter=my_vault_client)
#       registry.register("VaultAdapter", vault_tool)
#
#   The calling run() module must follow the LOGGING.md tool boundary pattern:
#       - Log BEFORE the vault call (with correlationId + taskId)
#       - Log AFTER the vault call (with correlationId + taskId + outcome)
#       - Never log the returned data — log shape/field count only

from typing import Any
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("vault_adapter_tool")


_KNOWN_ACTIONS = {"fetch_fields", "list_inventory"}


class VaultAdapterTool:
    """
    Tool adapter wrapping a personal data vault.

    Dispatches to the underlying vault_adapter based on the 'action'
    field in the payload.

    Supported actions:
        fetch_fields     — retrieve a subset of personal data fields
        list_inventory   — list available data categories

    execute() returns a dict. On any failure, returns a structured
    error dict — ToolRegistry wraps this in a ToolResult.
    Never raises.
    """

    def __init__(self, vault_adapter: Any) -> None:
        """
        Args:
            vault_adapter: The underlying vault client instance.
                           Must expose fetch_fields(fields, context) and
                           list_inventory() as async methods.
        """
        self.vault = vault_adapter

    async def execute(self, payload: dict, context: dict) -> dict:
        """
        Dispatch to vault based on payload["action"].
        Returns a dict. Never raises.
        """
        action = payload.get("action")

        if not action:
            return {
                "success": False,
                "error": "VaultAdapterTool: 'action' field missing from payload.",
            }

        if action not in _KNOWN_ACTIONS:
            return {
                "success": False,
                "error": (
                    f"VaultAdapterTool: unknown action '{action}'. "
                    f"Known actions: {sorted(_KNOWN_ACTIONS)}"
                ),
            }

        try:
            if action == "fetch_fields":
                fields = payload.get("fields", [])
                if not fields:
                    return {
                        "success": False,
                        "error": "VaultAdapterTool: 'fields' missing or empty for fetch_fields.",
                    }
                result = await self.vault.fetch_fields(fields, context)
                return result if isinstance(result, dict) else {"data": result}

            if action == "list_inventory":
                result = await self.vault.list_inventory()
                return result if isinstance(result, dict) else {"inventory": result}

        except Exception as exc:
            logger.error(
                "VaultAdapterTool: action '%s' failed — %s", action, exc
            )
            return {
                "success": False,
                "error": f"VaultAdapterTool: action '{action}' failed — {exc}",
            }

        # Should never reach here
        return {
            "success": False,
            "error": f"VaultAdapterTool: unhandled action '{action}'.",
        }
