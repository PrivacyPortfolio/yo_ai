# core/routing/capability_map_builder.py
#
# Generates or updates shared/artifacts/capability_map.yaml from:
#   1. Agent extended cards  — supplies skill names, schema URLs, handler paths
#   2. Deployment config     — supplies Lambda function names, API routes, defaults
#
# Uses CapabilityLoader (capabilityLoader.py) for card introspection and
# ManifestLoader (manifest_loader.py) for loading card files from disk.
#
# Why two sources are needed:
#   The agent card knows: skill names, input/output schema $ref URLs,
#   artifact paths (handler .py file).
#   The card does NOT know: Lambda function name, API Gateway route,
#   dryRun defaults — those are deployment topology, not agent identity.
#
# Usage (standalone):
#   python capability_map_builder.py \
#       --cards agents/*/agent_card/extended/agent.json \
#       --deploy-config deploy/capability_deploy_config.yaml \
#       --output shared/artifacts/capability_map.yaml
#
# Usage (programmatic):
#   from shared.tools.loaders.capability_map_builder import CapabilityMapBuilder
#   builder = CapabilityMapBuilder(deploy_config)
#   builder.add_card(extended_card_dict)
#   builder.write("shared/artifacts/capability_map.yaml")
#
# Deployment config shape (capability_deploy_config.yaml) — OPTIONAL:
#   Only needed to override route_prefix. Handler is derived from the card.
#   agents:
#     door-keeper:
#       route_prefix: /agents/door-keeper    # default: /agents/<agent-name>
#   defaults:
#     dryRun: false
#     trace:  false
#
# Handler derivation from handler artifact path:
#   path: "/"                             → "<agent-name>-handler" (internal)
#   path: "/authentication-claim-handler.py" → "authentication-claim-handler.py" (external)
#
# capability_map.yaml output shape (per capability):
#   capabilities:
#     Trust.Assign:
#       agent:        door-keeper
#       handler:      door-keeper-handler              # derived from card
#       handlerType:  internal                         # internal | external
#       inputSchema:  trust.assign.input.schema.json
#       outputSchema: trust.assign.output.schema.json
#       route:        /agents/door-keeper/TrustAssign
#       dryRun:       false
#       trace:        false
#   routes:
#     /agents/door-keeper/TrustAssign: Trust.Assign
#     ...

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # fallback to JSON output if PyYAML not installed

from capabilityLoader import CapabilityLoader
from core.utils.manifest_loader import ManifestLoader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capability_id_to_route_segment(capability_id: str) -> str:
    """
    Convert canonical capability ID to URL path segment.
    "Trust.Assign"         → "TrustAssign"
    "Subscriber.Register"  → "SubscriberRegister"
    "AccessRights.Manage"  → "AccessRightsManage"
    """
    return capability_id.replace(".", "")


def _capability_id_to_schema_name(capability_id: str, direction: str) -> str:
    """
    Derive schema filename from capability ID.
    "Trust.Assign" + "input"  → "trust.assign.input.schema.json"
    Consistent with CapabilityContext.input_schema_name property.
    """
    return f"{capability_id.lower()}.{direction}.schema.json"


def _extract_schema_name_from_ref(ref: str | None) -> str:
    """
    Extract filename from a $ref URL.
    "https://yo-ai.ai/schemas/trust.assign.input.schema.json"
    → "trust.assign.input.schema.json"
    Falls back to empty string if ref is None or malformed.
    """
    if not ref:
        return ""
    return Path(ref).name


# ---------------------------------------------------------------------------
# CapabilityMapBuilder
# ---------------------------------------------------------------------------

class CapabilityMapBuilder:
    """
    Builds capability_map.yaml from agent extended cards + deployment config.

    Workflow:
      1. Load deployment config (Lambda function names, route prefixes)
      2. For each agent extended card, use CapabilityLoader to extract skills
      3. For each skill, derive schema names from card $refs or capability_id
      4. Merge with deployment config to produce a complete capability entry
      5. Write to capability_map.yaml
    """

    def __init__(self, deploy_config: Dict[str, Any]) -> None:
        """
        Args:
            deploy_config: Optional deployment overrides. Shape:
                {
                    "agents": {
                        "door-keeper": {
                            "route_prefix": "/agents/door-keeper"  # optional override
                        }
                    },
                    "defaults": { "dryRun": False, "trace": False }
                }
            Handler names are derived from the card's handler artifact path:
              path="/"    → internal, handler="<agent-name>-handler"
              path="*.py" → external, handler=that filename
            No separate function_name config needed.
        """
        self.deploy_config  = deploy_config
        self.agent_configs  = deploy_config.get("agents", {})
        self.defaults       = deploy_config.get("defaults", {})
        self.capabilities:  Dict[str, Any] = {}
        self.routes:        Dict[str, str] = {}
        self.warnings:      List[str] = []

    def add_card(self, extended_card: Dict[str, Any]) -> None:
        """
        Extract capabilities from one extended agent card and add to the map.

        Uses CapabilityLoader to join skills + x-capabilities + x-artifacts.
        Looks up deployment config by agent name from the card's "name" field.
        """
        agent_name = extended_card.get("name", "")
        if not agent_name:
            self.warnings.append("Skipped card with no 'name' field.")
            return

        # Normalise agent name for config lookup (card: "Door-Keeper" → key: "door-keeper")
        agent_key = agent_name.lower()
        agent_cfg = self.agent_configs.get(agent_key, {})

        if not agent_cfg:
            self.warnings.append(
                f"No deployment config for agent '{agent_key}' — "
                f"handler and route will be placeholder values."
            )

        # route_prefix can be overridden in deploy config; defaults to /agents/<agent>
        route_prefix  = agent_cfg.get("route_prefix", f"/agents/{agent_key}")
        # handler is derived from the card's handler artifact — resolved per capability below
        default_handler = f"{agent_key}-handler"  # fallback for capabilities with no handler artifact

        # Use CapabilityLoader to extract the unified skill view
        loader = CapabilityLoader(extended_card)
        loaded = loader.load()

        for skill_name, skill_data in loaded.items():
            skill      = skill_data.get("skill", {})
            artifacts  = skill_data.get("artifacts", [])

            # Derive schema names and handler from x-artifacts entries
            input_schema  = ""
            output_schema = ""
            handler_path  = None   # from handler artifact
            handler_type  = "internal"

            for artifact in artifacts:
                art_type = artifact.get("artifactType", "")
                schema   = artifact.get("schema", {})
                ref      = schema.get("$ref", "") if isinstance(schema, dict) else ""
                name     = artifact.get("name", "")

                if art_type == "messageType":
                    # Schema name from card $ref, falling back to derived name
                    extracted = _extract_schema_name_from_ref(ref)
                    if name.endswith(".Input") or "input" in name.lower():
                        input_schema = extracted or _capability_id_to_schema_name(skill_name, "input")
                    elif name.endswith(".Output") or "output" in name.lower():
                        output_schema = extracted or _capability_id_to_schema_name(skill_name, "output")

                elif art_type == "handler":
                    # Handler path declared in the card:
                    #   path="/"       → internal capability (run() module via <agent>_handler.py)
                    #   path="*.py"    → external executable integration script
                    handler_path = artifact.get("path", "/")

            # Resolve handler name and type from the card's handler artifact
            if handler_path is None or handler_path == "/":
                # Internal: handled by the agent's own Lambda handler
                resolved_handler = default_handler
                handler_type     = "internal"
            else:
                # External: specific integration script declared in the card
                # e.g. "/authentication-claim-handler.py" → "authentication-claim-handler.py"
                resolved_handler = handler_path.lstrip("/")
                handler_type     = "external"

            # Fall back to derived schema names if not found in artifacts
            if not input_schema:
                input_schema  = _capability_id_to_schema_name(skill_name, "input")
            if not output_schema:
                output_schema = _capability_id_to_schema_name(skill_name, "output")

            # Build route
            route_segment = _capability_id_to_route_segment(skill_name)
            route         = f"{route_prefix}/{route_segment}"

            # Capability map entry
            entry = {
                "agent":        agent_key,
                "handler":      resolved_handler,
                "handlerType":  handler_type,
                "inputSchema":  input_schema,
                "outputSchema": output_schema,
                "route":        route,
                "dryRun":       self.defaults.get("dryRun", False),
                "trace":        self.defaults.get("trace", False),
            }

            # Warn on duplicate capability IDs across agents
            if skill_name in self.capabilities:
                existing_agent = self.capabilities[skill_name].get("agent")
                self.warnings.append(
                    f"Capability '{skill_name}' already registered for agent "
                    f"'{existing_agent}' — overwriting with '{agent_key}'."
                )

            self.capabilities[skill_name] = entry
            self.routes[route]            = skill_name

    def add_card_from_file(self, path: str | Path) -> None:
        """Load an extended card from disk and add it."""
        card = ManifestLoader.load_manifest(path)
        self.add_card(card)

    def build(self) -> Dict[str, Any]:
        """Return the complete capability map as a dict."""
        return {
            "capabilities": self.capabilities,
            "routes":       self.routes,
        }

    def write(self, output_path: str | Path) -> None:
        """
        Write the capability map to a YAML file (or JSON if PyYAML unavailable).

        Output path: shared/artifacts/capability_map.yaml
        """
        import json as _json

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.build()

        if yaml is not None:
            content = yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)
            output_path.with_suffix(".yaml").write_text(content, encoding="utf-8")
            print(f"Written: {output_path.with_suffix('.yaml')}")
        else:
            # PyYAML not installed — fall back to JSON
            json_path = output_path.with_suffix(".json")
            json_path.write_text(_json.dumps(data, indent=2), encoding="utf-8")
            print(f"PyYAML not available — written as JSON: {json_path}")

        if self.warnings:
            print(f"\n{len(self.warnings)} warning(s):")
            for w in self.warnings:
                print(f"  ⚠️  {w}")

        print(f"\nCapabilities: {len(self.capabilities)}")
        print(f"Routes:       {len(self.routes)}")


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    import glob

    parser = argparse.ArgumentParser(
        description="Generate capability_map.yaml from agent extended cards."
    )
    parser.add_argument(
        "--cards",
        nargs="+",
        required=True,
        help="Glob patterns or paths to extended agent card JSON files.",
    )
    parser.add_argument(
        "--deploy-config",
        required=True,
        help="Path to capability_deploy_config.yaml or .json.",
    )
    parser.add_argument(
        "--output",
        default="shared/artifacts/capability_map.yaml",
        help="Output path for capability_map.yaml (default: shared/artifacts/capability_map.yaml).",
    )
    args = parser.parse_args()

    # Load deploy config
    deploy_cfg_path = Path(args.deploy_config)
    if not deploy_cfg_path.exists():
        print(f"Error: deploy config not found: {deploy_cfg_path}", file=sys.stderr)
        sys.exit(1)

    if yaml is not None and deploy_cfg_path.suffix in (".yaml", ".yml"):
        with deploy_cfg_path.open() as f:
            deploy_config = yaml.safe_load(f)
    else:
        import json as _json
        deploy_config = _json.loads(deploy_cfg_path.read_text())

    builder = CapabilityMapBuilder(deploy_config)

    # Resolve card paths (glob expansion)
    card_paths = []
    for pattern in args.cards:
        matched = glob.glob(pattern, recursive=True)
        if matched:
            card_paths.extend(matched)
        else:
            card_paths.append(pattern)  # treat as literal path

    if not card_paths:
        print("Error: no card files found.", file=sys.stderr)
        sys.exit(1)

    for path in card_paths:
        try:
            builder.add_card_from_file(path)
            print(f"Loaded: {path}")
        except Exception as exc:
            print(f"Warning: failed to load '{path}' — {exc}", file=sys.stderr)

    builder.write(args.output)


if __name__ == "__main__":
    main()
