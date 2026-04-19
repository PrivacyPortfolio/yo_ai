# core/yoai_agent.py

import types
from typing import Any, Dict, List

from core.base_agent import BaseAgent
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability

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

    Extends BaseAgent with AI machinery, governance artifacts, and the
    capability dispatch contract.

    Construction contract:
      - No ctx parameter. Callers that have a ctx extract the individual
        members they need and pass them explicitly.
      - self.name / self.agent_id are the identity source of truth (BaseAgent).
        self.actor_name is not duplicated here.
      - self.extended is frozen (MappingProxyType) immediately after receipt,
        matching the BaseAgent treatment of self.card.
      - self.correlation_id / self.task_id are the single flat source of truth
        for tracing. set_correlation() is the only writer after construction.
      - No ctx is ever stored on self. _build_context() produces a fresh
        YoAiContext per request and passes it into the handler as a local.
    """

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        profile: dict | None = None,
        slim: bool = False,
        correlation_id: str | None = None,
        task_id: str | None = None,
    ):
        # ── Layer 1: BaseAgent identity ────────────────────────────────────
        # Establishes self.name, self.agent_id, self.description,
        # self.provider, self.card (frozen), self.skill_specs,
        # self.skill_handlers, and all protocol/capability/security attrs.
        super().__init__(agent_card=card or {})

        # ── Extended card — frozen immediately ─────────────────────────────
        # Mirrors the BaseAgent treatment of self.card.
        # All runtime access via self.extended; never re-read raw dict above.
        self.extended: types.MappingProxyType | None = (
            types.MappingProxyType(extended_card) if extended_card else None
        )

        # ── AI client ──────────────────────────────────────────────────────
        # Constructed from the x-ai block in the extended card.
        # Uses self.name (BaseAgent) — not a local alias.
        self.ai_client = AiClient(
            agent_name=self.name,
            xai_block=(self.extended or {}).get("x-ai"),
        )

        # ── Profile — normalized, set once ────────────────────────────────
        # self.profile is the single source of truth for capability handlers.
        # Empty-name profiles are treated as no profile.
        if profile is not None:
            profile_name = (profile.get("name") or "").strip()
            self.profile: dict | None = profile if profile_name else None
        else:
            self.profile = None

        # ── Instance identity ──────────────────────────────────────────────
        # base_instance_id: self.name + "." + profile.name (if profile set)
        # instance_id:      base_instance_id — SG appends counter suffix if needed
        profile_name = (self.profile or {}).get("name", "").strip()
        self.base_instance_id: str = (
            f"{self.name}.{profile_name}" if profile_name else self.name
        )
        self.instance_id: str = self.base_instance_id

        # ── Correlation and task identity ──────────────────────────────────
        # Flat attrs are the single source of truth for tracing.
        # Callers that have a ctx extract these before constructing the agent.
        # set_correlation() is the only writer after this point.
        self.correlation_id: str | None = correlation_id
        self.task_id: str | None = task_id or correlation_id

        # ── Declarative contract: skills and schemas ───────────────────────
        # Loaded once at construction from frozen cards.
        # Extended skills/schemas are appended to base card declarations.
        self.skills: List[Dict[str, Any]] = self._load_skills()
        self.schemas: List[Dict[str, Any]] = self._load_schemas()

        # ── Initialization depth — controlled by slim ──────────────────────
        #
        # slim=False (default): full governance init
        #   tools, fingerprints, knowledge loaded
        #   Use for: Mode A, governed capabilities, vault/tool access
        #
        # slim=True: minimal init — identity + logger only
        #   Use for: Mode B Direct API, workflow steps, test harnesses
        if not slim:
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

        # ── Logger — always last ───────────────────────────────────────────
        # Initialized after all identity attrs are final so instance_id
        # is stable before the first log line is ever written.
        self.logger = get_logger(self.instance_id)

    # ── showCard — trust-gated extended card access ────────────────────────

    def showCard(self, ctx: YoAiContext | None = None) -> dict:
        """
        Return the appropriate agent card based on caller context.

        No card          → fires NO_CARD alert, returns {}.
        Identified caller (ctx["caller"]["agent_id"] present) → extended card.
        Anonymous caller → basic card only.

        ctx is a YoAiContext dict — access via ctx.get(), never attribute access.
        This method has no side effects on agent state.
        """
        if not self.card:
            self._fire_no_card_event(ctx)
            return {}

        caller = (ctx.get("caller") if ctx else None) or {}
        caller_identified = bool(caller.get("agent_id"))

        if caller_identified:
            if self.extended:
                return dict(self.extended)
            self.logger.write(
                event_type="extended_card_missing",
                payload={"caller_agent_id": caller.get("agent_id")},
                context=ctx,
                level="WARNING",
                include=["instance_id", "correlation_id"],
            )

        return dict(self.card)

    # ── Capability dispatch ────────────────────────────────────────────────

    def handle_capability(
        self,
        capability_name: str,
        envelope: dict,
        request_id: str | None = None,
    ):
        """
        Safe capability entrypoint for direct invocation.

        Builds a fresh YoAiContext from the envelope, logs invocation,
        dispatches to the named capability method, and normalizes exceptions.
        ctx is a local — it is never stored on self.
        """
        from core.runtime.error_handler import ErrorHandler

        handler = getattr(self, capability_name, None)

        if handler is None or not callable(handler):
            self.logger.write(
                event_type="capability_not_found",
                payload={
                    "capability": capability_name,
                    "agent": self.instance_id,
                },
                context=None,
                level="ERROR",
                include=["instance_id"],
            )
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

        ctx: YoAiContext | None = None
        try:
            ctx = self._build_context(envelope)

            self.logger.write(
                event_type="capability_invocation",
                payload={
                    "capability": capability_name,
                    "payload_keys": list(
                        envelope.get("payload", envelope).keys()
                    ),
                },
                context=ctx,
                level="DEBUG",
                include=["instance_id", "correlation_id", "task_id"],
            )

            payload = envelope.get("payload", envelope)
            return handler(payload, ctx)

        except Exception as exc:
            self.logger.write(
                event_type="capability_exception",
                payload={
                    "capability": capability_name,
                    "error_type": type(exc).__name__,
                    "error_str": str(exc),
                },
                context=ctx,     # None if _build_context itself raised
                level="ERROR",
                include=["instance_id", "correlation_id", "task_id"],
            )
            return ErrorHandler.normalize_exception(
                exc,
                request_id=request_id,
                agent_name=self.instance_id,
                capability=capability_name,
                context={"source": "YoAiAgent.handle_capability"},
            )

    # ── Context factory ────────────────────────────────────────────────────

    def _build_context(self, envelope: dict) -> YoAiContext:
        """
        Build a fresh YoAiContext for one capability invocation.

        Merges:
          - Agent identity fields via as_actor_stub() (BaseAgent)
          - Agent tracing fields: correlation_id, task_id, profile
          - Request fields from the envelope (actor, startup_mode, knobs, etc.)

        The returned ctx is a plain dict — it is passed into the handler
        and discarded after the call completes. Never assigned to self.
        """
        return ctx_from_envelope(
            envelope,
            **self.as_actor_stub(),          # instance_id, actor_kind, actor
            correlation_id=self.correlation_id,
            task_id=self.task_id,
            profile=self.profile,
        )

    # ── Correlation management ─────────────────────────────────────────────

    def set_correlation(
        self,
        request_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        # ── delegate to BaseAgent.generate_message_ids ─────────────────────
        # Overrides any ids seeded at construction.
        # task_id is preserved if already set and no new one is supplied.
        self.correlation_id, self.task_id = self.generate_message_ids(
            request_id=request_id,
            task_id=task_id or self.task_id,
        )

    def clear_correlation(self) -> None:
        """Clear tracing ids after a message or task completes."""
        self.correlation_id = None
        self.task_id = None

    # ── Internal loaders ──────────────────────────────────────────────────

    def _load_skills(self) -> List[Dict[str, Any]]:
        """
        Merge skills from basic and extended cards.
        Called once during __init__ against the frozen cards.
        Result is stored in self.skills — cards are not re-read after this.
        """
        skills = list(self.skill_specs.values())     # BaseAgent canonical index
        if self.extended:
            skills += list(self.extended.get("skills", []))
        return skills

    def _load_schemas(self) -> List[Dict[str, Any]]:
        """
        Merge schemas from basic and extended cards.
        Called once during __init__ against the frozen cards.
        Result is stored in self.schemas — cards are not re-read after this.
        """
        schemas = list((self.card or {}).get("schemas", []))
        if self.extended:
            schemas += list(self.extended.get("schemas", []))
        return schemas
