import json
from typing import Any, Callable, Dict, List, Optional

class BaseAgent:
    """
    A minimal runtime implementation of an A2A agent whose behavior is defined
    entirely by its AgentCard. This class simply operationalizes what the AgentCard declares:
    
    - Identity (name, id, description, provider)
    - Supported interfaces (protocolBinding, protocolVersion, URL)
    - Capabilities (streaming, pushNotifications, extendedAgentCard)
    - Security schemes and required authentication
    - Default input/output modes
    - Skills (name, description, schemas, examples)
    
    Skills must be registered with executables that implement the declared
    behavior. The BaseAgent handles dispatching skill calls and validating that
    the skill exists.
    """

    def __init__(self, agent_card: Dict[str, Any]):
        self.card = agent_card

        # Basic identity
        self.name: str = agent_card.get("name")
        self.agent_id: str = agent_card.get("id")
        self.description: str = agent_card.get("description")
        self.provider: Dict[str, Any] = agent_card.get("provider", {})

        # Protocol + interfaces
        self.protocol_version: str = agent_card.get("protocolVersion")
        self.supported_interfaces: List[Dict[str, Any]] = agent_card.get("supportedInterfaces", [])

        # Capabilities
        self.capabilities: Dict[str, bool] = agent_card.get("capabilities", {})

        # Security
        self.security_schemes: Dict[str, Any] = agent_card.get("securitySchemes", {})
        self.security: List[Dict[str, Any]] = agent_card.get("security", [])

        # I/O modes
        self.default_input_modes: List[str] = agent_card.get("defaultInputModes", [])
        self.default_output_modes: List[str] = agent_card.get("defaultOutputModes", [])

        # Skills declared in the card
        self.skill_specs: Dict[str, Dict[str, Any]] = {
            skill["name"]: skill for skill in agent_card.get("skills", [])
        }

        # Runtime skill implementations (executables)
        self.skill_handlers: Dict[str, Callable] = {}

    # ----------------------------------------------------------------------
    # Registration
    # ----------------------------------------------------------------------

    def register_skill(self, skill_name: str, handler: Callable):
        """
        Register an executable that implements the declared skill.
        """
        if skill_name not in self.skill_specs:
            raise ValueError(f"Skill '{skill_name}' is not declared in the AgentCard.")
        self.skill_handlers[skill_name] = handler

    # ----------------------------------------------------------------------
    # Security
    # ----------------------------------------------------------------------

    def validate_security(self, headers: Dict[str, str]):
        """
        Validate incoming request headers against the AgentCard's security schemes.
        This is a minimal implementation: it only checks for required API keys.
        """
        for scheme in self.security:
            for scheme_name in scheme.keys():
                scheme_def = self.security_schemes.get(scheme_name)
                if not scheme_def:
                    continue

                if scheme_def.get("type") == "apiKey":
                    key_name = scheme_def.get("name")
                    if key_name not in headers:
                        raise PermissionError(f"Missing required API key header: {key_name}")

    # ----------------------------------------------------------------------
    # Skill Dispatch
    # ----------------------------------------------------------------------

    def invoke(self, skill_name: str, payload: Any, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Invoke a skill by name. Validates:
        - Security requirements
        - Skill existence
        - Skill handler registration
        """
        headers = headers or {}
        self.validate_security(headers)

        if skill_name not in self.skill_specs:
            raise ValueError(f"Skill '{skill_name}' is not declared in the AgentCard.")

        if skill_name not in self.skill_handlers:
            raise RuntimeError(f"Skill '{skill_name}' has no registered handler.")

        handler = self.skill_handlers[skill_name]
        return handler(payload)

    # ----------------------------------------------------------------------
    # Metadata Accessors
    # ----------------------------------------------------------------------

    def get_agent_card(self) -> Dict[str, Any]:
        """Return the full AgentCard."""
        return self.card

    def list_skills(self) -> List[str]:
        """Return the list of declared skill names."""
        return list(self.skill_specs.keys())

    def describe_skill(self, skill_name: str) -> Dict[str, Any]:
        """Return the metadata for a declared skill."""
        if skill_name not in self.skill_specs:
            raise ValueError(f"Skill '{skill_name}' is not declared.")
        return self.skill_specs[skill_name]

    # ----------------------------------------------------------------------
    # Utility
    # ----------------------------------------------------------------------

    def to_json(self) -> str:
        """Return a JSON representation of the agent card."""
        return json.dumps(self.card, indent=2)