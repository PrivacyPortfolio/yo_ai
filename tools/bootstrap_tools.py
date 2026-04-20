# tools/bootstrap_tools.py
#
# x-artifacts tool entry shape (from ExtendedAgentCard):
#   {
#     "name": "AccessAdministrator",
#     "artifactType": "tool",
#     "path": "/access_admin.py",
#     "provider": {
#       "name": "Apache",
#       "product": "Kafka",
#       "config": { "bootstrapServers": "kafka:9092" }
#     },
#     "inputSchema":  { "$ref": "..." },
#     "outputSchema": { "$ref": "..." },
#     "auth": "apiKey"
#   }
#
# Adapter class resolution (provider.name → adapter class):
#   "AP2"              → AP2ClientAdapter
#   "HttpTool"         → HttpToolAdapter
#   "PrivacyPortfolio" → VaultAdapterTool  (manually wired — see note)
#   anything else      → HttpToolAdapter (safe default for HTTP-based tools)
#
# VaultAdapterTool note:
#   VaultAdapterTool requires an injected vault_adapter dependency and cannot
#   be loaded automatically from x-artifacts. Wire it manually after calling
#   build_tool_registry(). See agents that use the vault for the pattern.

import inspect
import json
from importlib import import_module

from tools.tool_registry import ToolAdapter, ToolRegistry
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("bootstrap_tools")

# ── Adapter class registry ─────────────────────────────────────────────────
# Maps provider.name values to (module_path, class_name) tuples.
# Add new adapter types here as they are built.
# VaultAdapterTool is wired manually — not auto-loaded from x-artifacts.

_ADAPTER_CLASS_REGISTRY = {
    "AP2":      ("shared.tools.adapters.ap2_client_adapter",  "AP2ClientAdapter"),
    "HttpTool": ("shared.tools.adapters.http_tool_adapter",    "HttpToolAdapter"),
}

_DEFAULT_ADAPTER = ("shared.tools.adapters.http_tool_adapter", "HttpToolAdapter")


# ── Public API ─────────────────────────────────────────────────────────────

def build_tool_registry(extended_card: dict | None) -> ToolRegistry:
    # ── Build ToolRegistry from x-artifacts in the extended agent card ─────
    # Skips internal capability tools (path="/") and unloadable adapters.
    # Never raises — failed tools are logged and skipped.
    registry = ToolRegistry()

    if not extended_card:
        return registry

    artifacts = extended_card.get("x-artifacts", [])
    tool_artifacts = [
        a for a in artifacts
        if isinstance(a, dict) and a.get("artifactType") == "tool"
    ]

    if not tool_artifacts:
        LOG.write(
            event_type="bootstrap_tools.NoToolArtifacts",
            payload={"message": "no tool artifacts found in extended card"},
            context=None,
        )
        return registry

    for tool_def in tool_artifacts:
        tool_name = tool_def.get("name", "")
        if not tool_name:
            LOG.write(
                event_type="bootstrap_tools.SkippedNoName",
                payload={"tool_def": tool_def},
                context=None,
            )
            continue

        # ── Skip internal capability tools ─────────────────────────────────
        # path="/" means this artifact IS the capability implementation,
        # dispatched by CAPABILITY_DISPATCH — not an external tool adapter.
        path = tool_def.get("path", "")
        if path == "/" or path == "":
            LOG.write(
                event_type="bootstrap_tools.SkippedInternal",
                payload={"tool_name": tool_name, "path": path},
                context=None,
            )
            continue

        _load_one_tool(registry, tool_name, tool_def)

    loaded = list(registry.list_tools())
    LOG.write(
        event_type="bootstrap_tools.RegistryBuilt",
        payload={"tool_count": len(loaded), "tools": loaded},
        context=None,
    )
    return registry


def _load_one_tool(
    registry: ToolRegistry,
    tool_name: str,
    tool_def: dict,
) -> None:
    # ── Resolve, instantiate, and register one tool adapter ────────────────
    # Logs a warning and returns without raising on any failure.
    provider_cfg  = tool_def.get("provider", {})
    config_cfg    = provider_cfg.get("config", {})
    provider_name = provider_cfg.get("name", "")

    module_path, class_name = _ADAPTER_CLASS_REGISTRY.get(
        provider_name, _DEFAULT_ADAPTER
    )

    try:
        module        = import_module(module_path)
        adapter_class = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        LOG.write(
            event_type="bootstrap_tools.AdapterImportFailed",
            payload={
                "tool_name":   tool_name,
                "module_path": module_path,
                "class_name":  class_name,
                "error":       str(exc),
            },
            context=None,
        )
        return

    try:
        adapter_instance: ToolAdapter = adapter_class(
            provider=provider_cfg,
            config=config_cfg,
        )
    except Exception as exc:
        LOG.write(
            event_type="bootstrap_tools.AdapterInstantiateFailed",
            payload={
                "tool_name":  tool_name,
                "class_name": class_name,
                "error":      str(exc),
            },
            context=None,
        )
        return

    try:
        registry.register(tool_name, adapter_instance)
        LOG.write(
            event_type="bootstrap_tools.ToolRegistered",
            payload={"tool_name": tool_name, "adapter": class_name},
            context=None,
        )
    except Exception as exc:
        LOG.write(
            event_type="bootstrap_tools.ToolRegisterFailed",
            payload={"tool_name": tool_name, "error": str(exc)},
            context=None,
        )


# ── Standalone CLI ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python bootstrap_tools.py <extended_agent_card.json>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        extended_card = json.load(f)

    registry = build_tool_registry(extended_card)
    tools    = registry.list_tools()

    if tools:
        print(f"Tools loaded ({len(tools)}):")
        for name in tools:
            print(f"  - {name}")
    else:
        print("No tools loaded.")
