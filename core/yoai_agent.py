# core/yoai_agent.py
# v3 — Persona-injecting, policy-gated, agreement-aware agent base
#
# Execution hierarchy enforced at every capability call:
#   Training Manual (Persona) → Policies (Constraints) → Agreements (Guardrails)
#
# Cache strategy:
#   _persona_cache  — loaded eagerly at construction, never reloaded (immutable)
#   _policy_cache   — lazy-loaded on first execute_pipeline(), optionally refreshed
#   _agreement_cache— lazy-loaded on first execute_pipeline(), optionally refreshed

from abc import ABC, abstractmethod
from pathlib import Path
import types
from typing import Any, Dict, List, Optional, Tuple

from core.base_agent import BaseAgent
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability

from core.utils.ai.ai_client import AiClient
from core.utils.validators.load_fingerprints import load_fingerprints
from core.utils.knowledge.load_knowledge import load_knowledge
from core.observability.logging.log_bootstrapper import get_logger

from tools.bootstrap_tools import build_tool_registry
from tools.tool_invocation_manager import ToolInvocationManager


class YoAiAgent(BaseAgent, ABC):
    """
    Identity-bearing, profile-aware, multi-instance agent base.

    v2 additions over v1
    --------------------
    * Persona injection: the agent's Training Manual is read from disk
      at construction and cached as ``_persona_cache``.  Every subsequent
      call to ``execute_pipeline()`` prepends the persona to the LLM prompt
      at zero I/O cost.

    * Hierarchical pipeline: ``execute_pipeline()`` enforces
      Persona → Policies → Agreements before reaching the LLM.

    * Lazy-loaded governance artifacts: Policies and Agreements are read
      from the agent's directory tree on first use; ``refresh_context()``
      forces a reload when external changes are known.

    Construction contract (unchanged from v1)
    ------------------------------------------
    * No ``ctx`` parameter.  Callers that have a ctx extract the individual
      members they need and pass them explicitly.
    * ``self.name`` / ``self.agent_id`` are the identity source of truth
      (BaseAgent).
    * ``self.extended`` is frozen (MappingProxyType) immediately after
      receipt, matching the BaseAgent treatment of ``self.card``.
    * ``self.correlation_id`` / ``self.task_id`` are the single flat source
      of truth for tracing.  ``set_correlation()`` is the only writer after
      construction.
    * No ctx is ever stored on self.  ``_build_context()`` produces a fresh
      YoAiContext per request and passes it into the handler as a local.

    File-system layout expected
    ---------------------------
    Persona (eager):
        <base_path>/explainability/training_manuals/<agent_name>_topology_or_manual.md

    Policies (lazy):
        <base_path>/agents/<agent_name>/policies/   (directory of *.md / *.json)

    Agreements (lazy):
        <base_path>/agents/<agent_name>/agreements/ (directory of *.md / *.json)

    ``base_path`` defaults to ``Path("C:\\")`` and can be overridden via the
    ``base_path`` constructor keyword.
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
        base_path: str | Path | None = None,
    ):
        # ── Layer 1: BaseAgent identity ────────────────────────────────────
        # Establishes self.name, self.agent_id, self.description,
        # self.provider, self.card (frozen), self.skill_specs,
        # self.skill_handlers, and all protocol/capability/security attrs.
        super().__init__(agent_card=card or {})

        # ── Extended card — frozen immediately ─────────────────────────────
        self.extended: types.MappingProxyType | None = (
            types.MappingProxyType(extended_card) if extended_card else None
        )

        # ── AI client ──────────────────────────────────────────────────────
        # Single entry-point for all LLM calls; also used by execute_pipeline.
        self.ai_client = AiClient(
            agent_name=self.name,
            xai_block=(self.extended or {}).get("x-ai"),
        )

        # ── Profile — normalized, set once ────────────────────────────────
        if profile is not None:
            profile_name = (profile.get("name") or "").strip()
            self.profile: dict | None = profile if profile_name else None
        else:
            self.profile = None

        # ── Instance identity ──────────────────────────────────────────────
        profile_name = (self.profile or {}).get("name", "").strip()
        self.base_instance_id: str = (
            f"{self.name}.{profile_name}" if profile_name else self.name
        )
        self.instance_id: str = self.base_instance_id

        # ── Correlation and task identity ──────────────────────────────────
        self.correlation_id: str | None = correlation_id
        self.task_id: str | None = task_id or correlation_id

        # ── Declarative contract: skills and schemas ───────────────────────
        self.skills: List[Dict[str, Any]] = self._load_skills()
        self.schemas: List[Dict[str, Any]] = self._load_schemas()

        # ── Persona / policy / agreement cache slots ───────────────────────
        # Declared unconditionally so every code path (slim or full) can
        # reference these attrs without AttributeError.  slim agents leave
        # them None; full agents populate _persona_cache immediately below.
        self._persona_cache: str | None = None
        self._policy_cache: dict | None = None
        self._agreement_cache: dict | None = None

        # ── File-system root for governance artifacts ──────────────────────
        self.base_path: Path = Path(base_path) if base_path else Path("C:\\")

        # ── Initialization depth — controlled by slim ──────────────────────
        #
        # slim=False (default): full governance init
        #   tools, fingerprints, knowledge, and persona loaded
        #   Use for: Mode A, governed capabilities, vault/tool access
        #
        # slim=True: minimal init — identity + logger only
        #   Persona/policy/agreement caches remain None.
        #   Use for: Mode B Direct API, workflow steps, test harnesses
        if not slim:
            registry = build_tool_registry(self.extended)
            self.tools = registry
            self.tool_manager = ToolInvocationManager(registry)
            self.fingerprints = load_fingerprints(self.card, self.extended)
            self.knowledge = load_knowledge(self)

            # ── Persona injection (eager, cached) ─────────────────────────
            # Loaded once here; ``persona_context`` property returns the
            # cached string with zero I/O on every subsequent access.
            persona_path = (
                self.base_path
                / "explainability"
                / "training_manuals"
                / f"{self.name}_topology_or_manual.md"
            )
            if persona_path.exists():
                self._persona_cache = persona_path.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError(
                    f"Training manual not found: {persona_path}\n"
                    f"Expected: <base_path>/explainability/training_manuals/"
                    f"{self.name}_topology_or_manual.md"
                )
        else:
            self.tools = None
            self.tool_manager = None
            self.fingerprints = {}
            self.knowledge = {}

        # ── Logger — always last ───────────────────────────────────────────
        # Initialized after all identity attrs are final so instance_id
        # is stable before the first log line is ever written.
        self.logger = get_logger(self.instance_id)

        # ── Instantiation record ───────────────────────────────────────────
        self.logger.write(
            event_type="agent.Initialized",
            payload={
                "instance_id":    self.instance_id,
                "agent_id":       self.agent_id,
                "name":           self.name,
                "profile":        (self.profile or {}).get("name"),
                "slim":           slim,
                "skills":         [s.get("name") for s in self.skills],
                "has_tools":      self.tools is not None,
                "has_knowledge":  bool(self.knowledge),
                "persona_loaded": self._persona_cache is not None,
                "correlation_id": self.correlation_id,
            },
            context=None,
        )

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
        """Override correlation/task ids.  Only writer after construction."""
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
        """
        skills = list(self.skill_specs.values())     # BaseAgent canonical index
        if self.extended:
            skills += list(self.extended.get("skills", []))
        return skills

    def _load_schemas(self) -> List[Dict[str, Any]]:
        """
        Merge schemas from basic and extended cards.
        Called once during __init__ against the frozen cards.
        """
        schemas = list((self.card or {}).get("schemas", []))
        if self.extended:
            schemas += list(self.extended.get("schemas", []))
        return schemas

    # ── v2: Persona / Policy / Agreement layer ────────────────────────────

    @property
    def persona_context(self) -> str | None:
        """
        Return the cached Training Manual text (zero I/O after construction).

        Returns None for slim agents.  Full agents always have this populated
        because ``__init__`` raises FileNotFoundError if the manual is absent.
        """
        return self._persona_cache

    def _load_policies(self, force_refresh: bool = False) -> dict:
        """
        Lazy-load policies directory on first call; return cache thereafter.

        Reads every file under:
            <base_path>/agents/<agent_name>/policies/

        Pass ``force_refresh=True`` when you know external policies changed.
        """
        if self._policy_cache is None or force_refresh:
            policy_dir = self.base_path / "agents" / self.name / "policies"
            self._policy_cache = self._read_directory_as_dict(policy_dir)
        return self._policy_cache

    def _load_agreements(self, force_refresh: bool = False) -> dict:
        """
        Lazy-load agreements directory on first call; return cache thereafter.

        Reads every file under:
            <base_path>/agents/<agent_name>/agreements/

        Pass ``force_refresh=True`` when you know external agreements changed.
        """
        if self._agreement_cache is None or force_refresh:
            agreement_dir = self.base_path / "agents" / self.name / "agreements"
            self._agreement_cache = self._read_directory_as_dict(agreement_dir)
        return self._agreement_cache

    @staticmethod
    def _read_directory_as_dict(directory: Path) -> dict:
        """
        Read every file in *directory* and return ``{filename: text}`` dict.

        Missing or empty directories return an empty dict rather than raising,
        so agents that have no policies/agreements degrade gracefully.
        """
        if not directory.exists() or not directory.is_dir():
            return {}
        return {
            f.name: f.read_text(encoding="utf-8")
            for f in sorted(directory.iterdir())
            if f.is_file()
        }

    # ── v2: Hierarchical pipeline ─────────────────────────────────────────

    def execute_pipeline(
        self,
        user_request: str,
        context: dict | None = None,
        refresh_policies: bool = False,
    ) -> dict:
        """
        Execute the Persona → Policies → Agreements → LLM pipeline.

        Steps
        -----
        1. Inject persona (cached, zero I/O).
        2. Load and evaluate policy constraints.
        3. Load active agreements.
        4. Construct composite prompt and call the LLM via ``self.ai_client``.

        Args:
            user_request:     The incoming request string.
            context:          Optional ambient state (session data, agent vars).
            refresh_policies: Force reload of policies/agreements from disk.

        Returns:
            LLM response dict on success, or
            ``{"status": "rejected", "reason": <str>}`` on policy violation.
        """
        # Step 1: Persona — always cached, zero cost after construction
        persona_instructions = self.persona_context

        # Step 2: Load and evaluate policies
        policy_rules = self._load_policies(force_refresh=refresh_policies)
        is_compliant, violation_msg = self._evaluate_policy_constraints(
            user_request, policy_rules
        )
        if not is_compliant:
            self.logger.write(
                event_type="pipeline.policy_violation",
                payload={"reason": violation_msg, "request_preview": user_request[:120]},
                context=None,
                level="WARNING",
                include=["instance_id", "correlation_id"],
            )
            return {"status": "rejected", "reason": violation_msg}

        # Step 3: Load active agreements (guardrails)
        active_agreements = self._load_agreements(force_refresh=refresh_policies)

        # Step 4: Construct composite prompt
        final_prompt = {
            "persona_instructions":  persona_instructions,
            "operational_boundaries": policy_rules,
            "active_agreements":     active_agreements,
            "current_user_request":  user_request,
            "context":               context or {},
        }

        # Step 5: Call LLM through ai_client (single, governed entry-point)
        return self.ai_client.complete(final_prompt)

    def _evaluate_policy_constraints(
        self,
        user_request: str,
        policy_rules: dict,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check *user_request* against every loaded policy.

        Default implementation iterates all policies and delegates each check
        to ``_violates_policy()``.  Override this method in a subclass to add
        short-circuit logic, severity levels, or audit hooks.

        Returns:
            (True, None)                  — request is compliant
            (False, "violation message")  — request is rejected
        """
        violations = []
        for policy_name, policy_content in policy_rules.items():
            if self._violates_policy(user_request, policy_content):
                violations.append(policy_name)

        if violations:
            return False, f"Request violates policies: {', '.join(violations)}"
        return True, None

    @abstractmethod
    def _violates_policy(self, request: str, policy_content: str) -> bool:
        """
        Agent-specific policy check.

        Implement in your concrete subclass.  Return True if *request*
        violates the rules expressed in *policy_content*, False otherwise.
        """

    # ── Cache management ──────────────────────────────────────────────────

    def refresh_context(self) -> None:
        """
        Force reload of all mutable governance artifacts (Policies + Agreements).

        The persona (Training Manual) is intentionally excluded — it is
        considered immutable for the agent's lifetime.  Restart the agent
        if the persona itself changes.
        """
        self._load_policies(force_refresh=True)
        self._load_agreements(force_refresh=True)

    def get_cache_stats(self) -> dict:
        """Return a snapshot of cache population state (useful for debugging)."""
        return {
            "persona_cached":    self._persona_cache is not None,
            "policies_cached":   self._policy_cache is not None,
            "agreements_cached": self._agreement_cache is not None,
            "policy_count":      len(self._policy_cache or {}),
            "agreement_count":   len(self._agreement_cache or {}),
        }
