# core/base_agent.py

import json
import types
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple


class BaseAgent:
    """
    A minimal runtime implementation of an A2A agent whose behavior is defined
    entirely by its AgentCard. This class operationalizes what the AgentCard
    declares and provides the identity fragment that seeds YoAiContext.

    Responsibilities:
      - Identity (name, agent_id, description, provider)
      - Protocol + interfaces
      - Capabilities
      - Security schemes and request validation
      - Default input/output modes
      - Skill spec registry (declared) and handler registry (executable)
      - as_actor_stub() — identity contribution to YoAiContext

    Contract exported upward:
      1. All identity fields are final. No layer above reassigns self.name,
         self.agent_id, self.description, or self.provider.
      2. self.card is a read-only MappingProxyType. Mutation raises TypeError.
         Upper layers that need card fields use the extracted flat attrs.
      3. self.skill_specs is the canonical declared-skill manifest. YoAiAgent
         loads executables against it — it does not re-read self.card["skills"].
      4. No ctx of any kind exists at this layer. The first ctx is built
         in YoAiAgent._build_context() per request, never stored.
    """

    def __init__(self, agent_card: Dict[str, Any]):

        # Freeze the raw card immediately — no layer above can mutate it.
        # Use self.card only as a serialization escape hatch (to_json).
        # All runtime access goes through the extracted flat attrs below.
        self.card: types.MappingProxyType = types.MappingProxyType(agent_card)

        # ── Identity ───────────────────────────────────────────────────────
        # Extracted once at construction. Final — never reassigned above.
        self.name:        str               = agent_card.get("name")
        self.agent_id:    str               = agent_card.get("id")
        self.description: str               = agent_card.get("description")
        self.provider:    Dict[str, Any]    = agent_card.get("provider", {})

        # ── Protocol + interfaces ──────────────────────────────────────────
        self.protocol_version:    str                  = agent_card.get("protocolVersion")
        self.supported_interfaces: List[Dict[str, Any]] = agent_card.get("supportedInterfaces", [])

        # ── Capabilities ───────────────────────────────────────────────────
        self.capabilities: Dict[str, bool] = agent_card.get("capabilities", {})

        # ── Security ───────────────────────────────────────────────────────
        self.security_schemes: Dict[str, Any]      = agent_card.get("securitySchemes", {})
        self.security:         List[Dict[str, Any]] = agent_card.get("security", [])

        # ── I/O modes ─────────────────────────────────────────────────────
        self.default_input_modes:  List[str] = agent_card.get("defaultInputModes", [])
        self.default_output_modes: List[str] = agent_card.get("defaultOutputModes", [])

        # ── Skill registry ─────────────────────────────────────────────────
        # skill_specs: declared shape from card — immutable after init.
        # skill_handlers: registered executables — populated via register_skill().
        self.skill_specs: Dict[str, Dict[str, Any]] = {
            skill["name"]: skill
            for skill in agent_card.get("skills", [])
        }
        self.skill_handlers: Dict[str, Callable] = {}

    # ── YoAiContext identity contribution ─────────────────────────────────

    def as_actor_stub(self) -> Dict[str, Any]:
        # ── actor_kind, actor ──────────────────────────────────────────────
        # BaseAgent owns name and agent_id only. instance_id is a YoAiAgent
        # concept and is supplied by _build_context() separately.
        return {
            "actor_kind": "Agent",
            "actor": {
                "agent_id":    self.agent_id,
                "name":        self.name,
                "description": self.description,
                "provider":    dict(self.provider),  # copy — provider is mutable
            },
        }

    # ── A2A message identifier generation ─────────────────────────────────

    def generate_message_ids(
        self,
        request_id: str | None = None,
        task_id: str | None = None,
    ) -> Tuple[str, str]:
        # ── correlation_id, task_id ────────────────────────────────────────
        # correlation_id: request_id when supplied (JSON-RPC alignment),
        #                 otherwise a fresh uuid4.
        # task_id:        caller-supplied task_id when present,
        #                 otherwise falls back to correlation_id.
        # Returns (correlation_id, task_id) — pure, no side effects.
        # Subclasses that need a different format override this method;
        # set_correlation() in YoAiAgent delegates here instead of
        # generating ids inline.
        correlation_id = request_id or str(uuid.uuid4())
        resolved_task_id = task_id or correlation_id
        return correlation_id, resolved_task_id



    def register_skill(self, skill_name: str, handler: Callable) -> None:
        """
        Register an executable that implements a declared skill.
        Raises ValueError if the skill is not declared in the AgentCard.
        """
        if skill_name not in self.skill_specs:
            raise ValueError(
                f"Skill '{skill_name}' is not declared in the AgentCard."
            )
        self.skill_handlers[skill_name] = handler

    # ── Security ───────────────────────────────────────────────────────────

    def validate_security(self, headers: Dict[str, str]) -> None:
        """
        Validate incoming request headers against the AgentCard's security
        schemes. Minimal implementation: checks for required API key headers.
        Raises PermissionError on the first missing key.
        """
        for scheme in self.security:
            for scheme_name in scheme.keys():
                scheme_def = self.security_schemes.get(scheme_name)
                if not scheme_def:
                    continue
                if scheme_def.get("type") == "apiKey":
                    key_name = scheme_def.get("name")
                    if key_name not in headers:
                        raise PermissionError(
                            f"Missing required API key header: {key_name}"
                        )

    # ── Skill dispatch ─────────────────────────────────────────────────────

    def invoke(
        self,
        skill_name: str,
        payload: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Invoke a skill by name after validating security, skill existence,
        and handler registration.
        """
        headers = headers or {}
        self.validate_security(headers)

        if skill_name not in self.skill_specs:
            raise ValueError(
                f"Skill '{skill_name}' is not declared in the AgentCard."
            )
        if skill_name not in self.skill_handlers:
            raise RuntimeError(
                f"Skill '{skill_name}' has no registered handler."
            )

        return self.skill_handlers[skill_name](payload)

    # ── Metadata accessors ─────────────────────────────────────────────────

    def get_agent_card(self) -> types.MappingProxyType:
        """
        Return the frozen AgentCard.
        Callers that need a mutable copy must call dict(agent.get_agent_card()).
        """
        return self.card

    def list_skills(self) -> List[str]:
        """Return the list of declared skill names."""
        return list(self.skill_specs.keys())

    def describe_skill(self, skill_name: str) -> Dict[str, Any]:
        """Return the spec for a declared skill."""
        if skill_name not in self.skill_specs:
            raise ValueError(f"Skill '{skill_name}' is not declared.")
        return self.skill_specs[skill_name]

    # ── Serialization ──────────────────────────────────────────────────────

    def to_json(self) -> str:
        """
        Return a JSON representation of the AgentCard.
        MappingProxyType is not directly JSON-serializable — unwrap to dict first.
        """
        return json.dumps(dict(self.card), indent=2)
