# core/yoai_agent.py

import uuid
from core.base_agent import BaseAgent
from core.yoai_context import YoAiContext

from core.utils.ai.ai_client import AiClient
from core.utils.validators.load_fingerprints import load_fingerprints
from core.utils.knowledge.load_knowledge import load_knowledge
from core.observability.logging.log_bootstrapper import get_logger

from tools.bootstrap_tools import build_tool_registry
from tools.tool_invocation_manager import ToolInvocationManager


class YoAiAgent(BaseAgent):
    """
    YoAiAgent:
    Identity-bearing, profile-aware, multi-instance agent.

    """

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        ctx: YoAiContext | None = None,
        profile: dict | None = None,
        slim: bool | None = None,
        context=None,
    ):
        super().__init__(card=card, extended_card=extended_card, context=context)

        # ------------------------------------------------------------------
        # Resolve construction parameters
        # Priority: explicit kwarg > CapabilityContext > default
        # ------------------------------------------------------------------
        _profile = profile if profile is not None else (
            capability_ctx.profile if capability_ctx else None
        )
        _slim = slim if slim is not None else (
            capability_ctx.slim if capability_ctx else False
        )

        # Preserve the capability_ctx for downstream use by capability handlers
        self.capability_ctx = capability_ctx

        # ------------------------------------------------------------------
        # Warn if required cards are missing — do not crash
        # ------------------------------------------------------------------
        if not self.card:
            print(f"[YoAiAgent WARNING] Basic card missing for "
                  f"{self.__class__.__name__}. Expected at agent_card/agent.json")

        if not self.extended:
            print(f"[YoAiAgent WARNING] Extended card missing for "
                  f"{self.__class__.__name__}. Expected at agent_card/extended/agent.json")

        # ------------------------------------------------------------------
        # Agent identity — card-driven
        # ------------------------------------------------------------------
        self.actor_name = (self.card or {}).get("name", "unknown-agent")

        # ------------------------------------------------------------------
        # AI client — constructed from x-ai block in extended card.
        # Handles all missing/partial x-ai configurations gracefully.
        # Used by call_ai() in ai_transform.py for model resolution and
        # LLM dispatch. Per-capability resolution active for Door-Keeper;
        # per-agent or platform fallback for all other agents.
        # ------------------------------------------------------------------
        self.ai_client = AiClient(
            agent_name=self.actor_name,
            xai_block=(self.extended or {}).get("x-ai"),
        )

        # ------------------------------------------------------------------
        # Profile — normalized, resolved, set once
        # self.profile is the single source of truth for capability handlers.
        # Never pull profile from the envelope inside run() — use self.profile.
        # ------------------------------------------------------------------
        if _profile is not None:
            profile_name = _profile.get("name") or ""
            self.profile = _profile if profile_name.strip() else None
        else:
            self.profile = None

        # ------------------------------------------------------------------
        # Instance identity
        # base_instance_id: actor_name + "." + profile.name (if profile present)
        # instance_id: base_instance_id — SG appends counter suffix if needed
        # ------------------------------------------------------------------
        profile_name = (self.profile or {}).get("name", "").strip()
        if profile_name:
            self.base_instance_id = f"{self.actor_name}.{profile_name}"
        else:
            self.base_instance_id = self.actor_name

        self.instance_id = self.base_instance_id

        # ------------------------------------------------------------------
        # Correlation and task identity
        # Seeded from CapabilityContext at construction.
        # SG calls set_correlation() after construction to finalize.
        # self.correlation_id and self.task_id are the single source of
        # truth for handlers — never use agent_ctx for these.
        # ------------------------------------------------------------------
        self.correlation_id = (
            capability_ctx.correlation_id if capability_ctx else None
        )
        self.task_id = (
            capability_ctx.task_id if capability_ctx else None
        ) or self.correlation_id

        # ------------------------------------------------------------------
        # Declarative contract loading — always performed
        # ------------------------------------------------------------------
        self.skills = self._load_skills()
        self.schemas = self._load_schemas()

        # ------------------------------------------------------------------
        # Initialization depth — controlled by slim flag
        #
        # slim=False (default): full governance init
        #   tools, fingerprints, knowledge loaded
        #   Use for: Mode A, governed capabilities, vault/tool access
        #
        # slim=True: minimal init — identity + logger only
        #   Use for: Mode B Direct API, workflow steps that don't need
        #            governance artifacts, test harnesses
        # ------------------------------------------------------------------
        if not _slim:
            registry = build_tool_registry(self.extended)
            self.tools = registry
            self.tool_manager = ToolInvocationManager(registry)
            self.fingerprints = load_fingerprints(self.card, self.extended)
            self.knowledge = load_knowledge(self)
        else:
            self.tools = None
            self.tool_manager = None
            self.fingerprints = {}
            self.knowledge = {}

        # ------------------------------------------------------------------
        # Platform-wide structured logger — always initialized
        # ------------------------------------------------------------------
        self.logger = get_logger(self.instance_id)
        self.logger.write({
            "actor": self.instance_id,
            "event_type": "agent_initialized",
            "message": f"{self.instance_id} initialized",
            "payload": {
                "actor_name": self.actor_name,
                "base_instance_id": self.base_instance_id,
                "profile_name": profile_name or None,
                "slim": _slim,
                "card_loaded": bool(self.card),
                "extended_card_loaded": bool(self.extended),
                "correlation_id": self.correlation_id,
                "task_id": self.task_id,
            },
        })

    # ------------------------------------------------------------------
    # showCard() — trust-gated extended card access
    # ------------------------------------------------------------------
    def showCard(self, context=None) -> dict:
        """
        Return the appropriate agent card based on caller context.

        No card → fires NO_CARD alert (three bells), returns {}.
        Identified caller (context.caller.agent_id present) → extended card.
        Anonymous caller → basic card only.
        """
        if not self.card:
            self._fire_no_card_event(context)
            return {}

        caller = (context.caller if context else None) or {}
        caller_identified = bool(caller.get("agent_id"))

        if caller_identified:
            if self.extended:
                return self.extended
            self.log(
                event_type="extended_card_missing",
                message=(
                    f"{self.actor_name} extended card requested by identified "
                    f"caller but not available — returning basic card"
                ),
                payload={
                    "caller_agent_id": caller.get("agent_id"),
                    "correlation_id": self.correlation_id,
                },
                level="WARNING",
            )
            return self.card

        return self.card

    # ------------------------------------------------------------------
    # Loader: Skills
    # ------------------------------------------------------------------
    def _load_skills(self):
        skills = list((self.card or {}).get("skills", []))
        if self.extended:
            skills += self.extended.get("skills", [])
        return skills

    # ------------------------------------------------------------------
    # Loader: Schemas
    # ------------------------------------------------------------------
    def _load_schemas(self):
        schemas = list((self.card or {}).get("schemas", []))
        if self.extended:
            schemas += self.extended.get("schemas", [])
        return schemas

    # ------------------------------------------------------------------
    # Correlation and task context management
    # ------------------------------------------------------------------
    def set_correlation(self, correlation_id: str = None):
        """
        Sets the active correlation ID and task_id for this agent instance.
        Called by the SG immediately after construction.
        Overrides any values seeded from CapabilityContext at construction.
        task_id defaults to correlation_id if not already set.
        """
        self.correlation_id = correlation_id or str(uuid.uuid4())
        if not self.task_id:
            self.task_id = self.correlation_id

    def clear_correlation(self):
        """Clears correlation and task context after a message/task completes."""
        self.correlation_id = None
        self.task_id = None

    # ------------------------------------------------------------------
    # Structured logging with automatic context injection
    # ------------------------------------------------------------------
    def log(
        self,
        event_type: str,
        message: str,
        payload: dict = None,
        level: str = "INFO",
    ):
        """
        Write a structured log event with automatic context injection.

        Automatically injects:
          actor          — self.instance_id
          correlation_id — self.correlation_id
          task_id        — self.task_id

        Use this instead of self.logger.write() directly so all
        capability log records carry consistent identity fields.
        """
        self.logger.write({
            "actor": self.instance_id,
            "event_type": event_type,
            "message": message,
            "payload": payload or {},
            "correlation_id": self.correlation_id,
            "task_id": self.task_id,
            "level": level,
        })

    # ------------------------------------------------------------------
    # Safe capability entrypoint for direct invocation
    # ------------------------------------------------------------------
    def handle_capability(
        self,
        capability_name: str,
        payload: dict,
        agent_context=None,
        capability_ctx: CapabilityContext | None = None,
        request_id=None,
    ):
        """
        Safe capability entrypoint.

        In Mode A: SG provides both contexts via the UCR.
        In Mode B: capability_ctx only, agent_context is None.
        In tests:  both may be None — handlers tolerate this gracefully.

        Passes both contexts to handler:
          handler(payload, agent_context, capability_ctx)

        Ensures ANY exception becomes an AnyException wrapped in a
        JSON-RPC envelope — no raw exceptions ever escape an agent.
        """
        from core.error_handler import ErrorHandler

        handler = getattr(self, capability_name, None)

        if handler is None or not callable(handler):
            return ErrorHandler.from_known_error(
                code=-32601,
                message="Capability not found",
                request_id=request_id,
                extra={
                    "agent": self.instance_id,
                    "capability": capability_name,
                    "source": "YoAiAgent.handle_capability",
                },
            )

        try:
            return handler(payload, agent_context, capability_ctx)

        except Exception as exc:
            return ErrorHandler.normalize_exception(
                exc,
                request_id=request_id,
                agent_name=self.instance_id,
                capability=capability_name,
                context={"source": "YoAiAgent.handle_capability"},
            )
