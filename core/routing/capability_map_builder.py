# core/routing/capability_map_builder.py
#
# Generates or updates shared/artifacts/capability_map.yaml from:
#   1. Agent extended cards  — skill names, schema URLs, handler paths
#   2. Deployment config     — Lambda function names, API routes, defaults
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
#       handler:      door-keeper-handler
#       handlerType:  internal
#       inputSchema:  trust.assign.input.schema.json
#       outputSchema: trust.assign.output.schema.json
#       route:        /agents/door-keeper/TrustAssign
#       dryRun:       false
#       trace:        false
#   routes:
#     /agents/door-keeper/TrustAssign: Trust.Assign

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

from capabilityLoader import CapabilityLoader
from core.utils.manifest_loader import ManifestLoader


# ── Helpers ────────────────────────────────────────────────────────────────

def _capability_id_to_route_segment(capability_id: str) -> str:
    # ── "Trust.Assign" → "TrustAssign" ────────────────────────────────────
    return capability_id.replace(".", "")


def _capability_id_to_schema_name(capability_id: str, direction: str) -> str:
    # ── "Trust.Assign" + "input" → "trust.assign.input.schema.json" ───────
    # Consistent with input_schema_name(ctx) / output_schema_name(ctx)
    # in core/yoai_context.py.
    return f"{capability_id.lower()}.{direction}.schema.json"


def _extract_schema_name_from_ref(ref: str | None) -> str:
    # ── Extract filename from a $ref URL ───────────────────────────────────
    # "https://yo-ai.ai/schemas/trust.assign.input.schema.json"
    # → "trust.assign.input.schema.json"
    if not ref:
        return ""
    return Path(ref).name


# ── CapabilityMapBuilder ───────────────────────────────────────────────────

class CapabilityMapBuilder:
    # ── Builds capability_map.yaml from agent extended cards + deploy config ─

    def __init__(self, deploy_config: Dict[str, Any]) -> None:
        self.deploy_config = deploy_config
        self.agent_configs = deploy_config.get("agents", {})
        self.defaults      = deploy_config.get("defaults", {})
        self.capabilities: Dict[str, Any] = {}
        self.routes:       Dict[str, str] = {}
        self.warnings:     List[str] = []

    def add_card(self, extended_card: Dict[str, Any]) -> None:
        # ── Extract capabilities from one extended agent card ───────────────
        agent_name = extended_card.get("name", "")
        if not agent_name:
            self.warnings.append("Skipped card with no 'name' field.")
            return

        agent_key = agent_name.lower()
        agent_cfg = self.agent_configs.get(agent_key, {})

        if not agent_cfg:
            self.warnings.append(
                f"No deployment config for agent '{agent_key}' — "
                f"handler and route will be placeholder values."
            )

        route_prefix    = agent_cfg.get("route_prefix", f"/agents/{agent_key}")
        default_handler = f"{agent_key}-handler"

        loader = CapabilityLoader(extended_card)
        loaded = loader.load()

        for skill_name, skill_data in loaded.items():
            skill     = skill_data.get("skill", {})
            artifacts = skill_data.get("artifacts", [])

            input_schema  = ""
            output_schema = ""
            handler_path  = None
            handler_type  = "internal"

            for artifact in artifacts:
                art_type = artifact.get("artifactType", "")
                schema   = artifact.get("schema", {})
                ref      = schema.get("$ref", "") if isinstance(schema, dict) else ""
                name     = artifact.get("name", "")

                if art_type == "messageType":
                    extracted = _extract_schema_name_from_ref(ref)
                    if name.endswith(".Input") or "input" in name.lower():
                        input_schema = extracted or _capability_id_to_schema_name(skill_name, "input")
                    elif name.endswith(".Output") or "output" in name.lower():
                        output_schema = extracted or _capability_id_to_schema_name(skill_name, "output")

                elif art_type == "handler":
                    handler_path = artifact.get("path", "/")

            if handler_path is None or handler_path == "/":
                resolved_handler = default_handler
                handler_type     = "internal"
            else:
                resolved_handler = handler_path.lstrip("/")
                handler_type     = "external"

            if not input_schema:
                input_schema  = _capability_id_to_schema_name(skill_name, "input")
            if not output_schema:
                output_schema = _capability_id_to_schema_name(skill_name, "output")

            route_segment = _capability_id_to_route_segment(skill_name)
            route         = f"{route_prefix}/{route_segment}"

            entry = {
                "agent":       agent_key,
                "handler":     resolved_handler,
                "handlerType": handler_type,
                "inputSchema": input_schema,
                "outputSchema": output_schema,
                "route":       route,
                "dryRun":      self.defaults.get("dryRun", False),
                "trace":       self.defaults.get("trace", False),
            }

            if skill_name in self.capabilities:
                existing_agent = self.capabilities[skill_name].get("agent")
                self.warnings.append(
                    f"Capability '{skill_name}' already registered for agent "
                    f"'{existing_agent}' — overwriting with '{agent_key}'."
                )

            self.capabilities[skill_name] = entry
            self.routes[route]            = skill_name

    def add_card_from_file(self, path: str | Path) -> None:
        card = ManifestLoader.load_manifest(path)
        self.add_card(card)

    def build(self) -> Dict[str, Any]:
        return {
            "capabilities": self.capabilities,
            "routes":       self.routes,
        }

    def write(self, output_path: str | Path) -> None:
        import json as _json

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.build()

        if yaml is not None:
            content = yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)
            output_path.with_suffix(".yaml").write_text(content, encoding="utf-8")
            print(f"Written: {output_path.with_suffix('.yaml')}")
        else:
            json_path = output_path.with_suffix(".json")
            json_path.write_text(_json.dumps(data, indent=2), encoding="utf-8")
            print(f"PyYAML not available — written as JSON: {json_path}")

        if self.warnings:
            print(f"\n{len(self.warnings)} warning(s):")
            for w in self.warnings:
                print(f"  {w}")

        print(f"\nCapabilities: {len(self.capabilities)}")
        print(f"Routes:       {len(self.routes)}")


# ── Standalone CLI ─────────────────────────────────────────────────────────

def main():
    import argparse
    import glob

    parser = argparse.ArgumentParser(
        description="Generate capability_map.yaml from agent extended cards."
    )
    parser.add_argument("--cards", nargs="+", required=True)
    parser.add_argument("--deploy-config", required=True)
    parser.add_argument("--output", default="shared/artifacts/capability_map.yaml")
    args = parser.parse_args()

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

    card_paths = []
    for pattern in args.cards:
        matched = glob.glob(pattern, recursive=True)
        card_paths.extend(matched if matched else [pattern])

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
