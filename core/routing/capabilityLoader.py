# core/routing/capabilityLoader.py
#
# Universal Capability Loader (Skill Bundle Model)

class CapabilityLoader:
    """
    Indexes skills, capability bundles, and artifacts from an agent card
    and produces a unified capability object per skill.

    Reusable across all agent classes. Used by capability_map_builder.py
    to generate capability_map.yaml entries from extended agent cards.

    x-capabilities entry shape (from ExtendedAgentCard):
        [
          {
            "Visitor.Identify": {
              "artifacts": [
                {"artifact": {"type": "skill",       "name": "Visitor.Identify"}},
                {"artifact": {"type": "messageType", "name": "Visitor.Identify.Input"}},
                {"artifact": {"type": "messageType", "name": "Visitor.Identify.Output"}}
              ]
            }
          },
          ...
        ]

    x-artifacts entry shape:
        [
          {
            "name":         "Visitor.Identify",
            "version":      "1.0.0",
            "artifactType": "messageType",
            "schema":       {"$ref": "https://yo-ai.ai/schemas/visitor.identify.input.schema.json"},
            "description":  "Input schema for visitor identification."
          },
          ...
        ]
    """

    def __init__(self, card: dict):
        self.card = card

        # Index skills by name
        self.skills = {
            s["name"]: s
            for s in card.get("skills", [])
            if isinstance(s, dict) and "name" in s
        }

        # Index capability bundles by skill name.
        # x-capabilities is a list of single-key dicts:
        #   [{"Trust.Assign": {"artifacts": [...]}}, ...]
        # NOT a list of dicts with a "name" field.
        self.capability_bundles: dict = {}
        for entry in card.get("x-capabilities", []):
            if not isinstance(entry, dict):
                continue
            for skill_name, bundle in entry.items():
                self.capability_bundles[skill_name] = bundle

        # Index artifacts by (name, artifactType) — there can be multiple
        # artifacts with the same name but different types (skill, task, tool,
        # handler, messageType). Use (name, type) as the composite key.
        self.artifacts: dict = {}
        for a in card.get("x-artifacts", []):
            if not isinstance(a, dict):
                continue
            name = a.get("name", "")
            atype = a.get("artifactType", "")
            if name and atype:
                self.artifacts[(name, atype)] = a

        # Also index by name alone for cases where type is not needed
        self.artifacts_by_name: dict = {}
        for a in card.get("x-artifacts", []):
            if not isinstance(a, dict):
                continue
            name = a.get("name", "")
            if name:
                # Last write wins for name-only lookup — use for messageType
                self.artifacts_by_name[name] = a

    def load(self) -> dict:
        """
        Produce a unified capability object per skill.

        Returns:
            {
                "Visitor.Identify": {
                    "skill": { ... },           # from skills[]
                    "artifacts": [              # resolved from x-artifacts
                        {
                            "artifactType": "messageType",
                            "name":         "Visitor.Identify.Input",
                            "version":      "1.0.0",
                            "schema":       {"$ref": "..."},
                            "description":  "..."
                        },
                        ...
                    ]
                },
                ...
            }
        """
        loaded = {}

        for skill_name, skill in self.skills.items():
            bundle = self.capability_bundles.get(skill_name)

            if not bundle:
                loaded[skill_name] = {"skill": skill, "artifacts": []}
                continue

            resolved_artifacts = []

            for ref in bundle.get("artifacts", []):
                if not isinstance(ref, dict):
                    continue

                # Unwrap the "artifact" wrapper:
                # {"artifact": {"type": "messageType", "name": "Visitor.Identify.Input"}}
                artifact_ref = ref.get("artifact", {})
                artifact_name = artifact_ref.get("name", "")
                artifact_type = artifact_ref.get("type", "")

                if not artifact_name or not artifact_type:
                    continue

                # Look up in x-artifacts by (name, type) first, then name alone
                artifact = self.artifacts.get(
                    (artifact_name, artifact_type)
                ) or self.artifacts_by_name.get(artifact_name)

                if artifact:
                    resolved_artifacts.append({
                        "artifactType": artifact_type,
                        "name":         artifact_name,
                        "version":      artifact.get("version"),
                        "schema":       artifact.get("schema"),
                        "description":  artifact.get("description"),
                    })

            loaded[skill_name] = {
                "skill":     skill,
                "artifacts": resolved_artifacts,
            }

        return loaded

    def list_skills(self) -> list:
        """Return list of skill names declared in the card."""
        return list(self.skills.keys())

    def list_artifacts(self, artifact_type: str | None = None) -> list:
        """
        Return list of artifact entries, optionally filtered by artifactType.
        e.g. list_artifacts("messageType") returns all message schema entries.
        """
        if artifact_type is None:
            return list(self.artifacts_by_name.values())
        return [
            a for a in self.artifacts_by_name.values()
            if a.get("artifactType") == artifact_type
        ]
