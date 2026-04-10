# core/yoai_context.py
from __future__ import annotations
from typing import Literal, Any

ActorKind = Literal["Agent", "Subscriber", "Service", "Tool", "WorkflowOwner", "Capability"]


class YoAiContext:
    """
    YoAiContext
    ═══════════
    The single unified interchange context for the YoAi platform.
    Defined on YoAiAgent. Constructed once per request-response interchange
    and populated progressively as the interchange proceeds.

    YoAiContext is the temporal thread that stitches together every logged
    platform event so activity can be queried or replayed. Every actor in
    the system — agent, subscriber, service, tool, workflow, or a capability
    invoking another capability — leaves its mark here.

    Two temporal faces
    ──────────────────
    REQUEST face   Populated at construction from the incoming envelope.
                   Answers: who is asking, on whose behalf, for what, how.

    RESPONSE face  Populated by the capability as it produces its result.
                   Answers: what changed, what should travel forward.

    Fields
    ──────

    ┌─ Correlation ──────────────────────────────────────────────────────┐
    │ correlation_id   JSON-RPC id. Primary request-response handle.     │
    │                  Set by A2ATransport at the protocol boundary.     │
    │ task_id          A2A task identifier.                              │
    │                  Defaults to correlation_id if absent.            │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Actor (REQUEST) ──────────────────────────────────────────────────┐
    │ actor_kind       What kind of entity invoked this operation.       │
    │                  One of: Agent | Subscriber | Service | Tool |     │
    │                          WorkflowOwner | Capability               │
    │ actor            Identity dict of the invoking entity.            │
    │                  Shape varies by actor_kind:                      │
    │                    Agent       → agent card stub                  │
    │                    Subscriber  → subscriber record stub           │
    │                    Capability  → {"capability_id": "Trust.Assign"}│
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Invocation mechanics (REQUEST) ───────────────────────────────────┐
    │ startup_mode     How the request entered the platform.             │
    │                  One of: "a2a" | "direct" | "api" | "starlette"  │
    │ instance_id      Runtime identity of the agent instance handling  │
    │                  this request. None for PlatformAgents.           │
    │ caller           Registered caller identity for trust-gated       │
    │                  access (e.g. showCard). None for anonymous.      │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Subject (REQUEST) ────────────────────────────────────────────────┐
    │ profile          ProfileWrapper — lightweight profile snippet.     │
    │                  Schema: yo-ai.ai/schemas/profile.schema.json     │
    │                  Shape: {type, name?, payload}                    │
    │                  Identifies whose context the agent operates in.  │
    │                  No PI — payload contains only authorized attrs.  │
    │ subject_ref      Lightweight pointer to the subject of the        │
    │                  request. Informational only; does not drive       │
    │                  routing decisions.                               │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Capability identity (REQUEST) ────────────────────────────────────┐
    │ capability_id    The capability being invoked, e.g. "Trust.Assign"│
    │                  None at pipeline level, bound at dispatch via     │
    │                  for_capability().                                │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Execution knobs (REQUEST) ────────────────────────────────────────┐
    │ slim             Skip expensive init (fingerprints, knowledge,    │
    │                  tools).                                          │
    │ tools            Selective tool loading.                          │
    │                  None=all, []=none, ["vault"]=named subset.       │
    │ dry_run          Validate without executing side effects.         │
    │ trace            Activate OTel Layer 4 explainability tracing.    │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Workflow state (REQUEST, updated per step) ───────────────────────┐
    │ step             Current workflow step index.                      │
    │ prior_outputs    Outputs from previous steps.                     │
    │ state            Arbitrary workflow state bag.                    │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ RESPONSE face — written by the capability, travels forward ───────┐
    │ profile_patch    ProfilePatch — fields discovered or collected     │
    │                  during execution that weren't in the original     │
    │                  profile. Forwarded to Data-Steward to enrich     │
    │                  the DataVault.                                   │
    │                  Schema: yo-ai.ai/schemas/profile.patch.schema.json│
    │                  Shape: {type, payload}                           │
    │                                                                   │
    │ governance_labels  Sticky notes attached to the response by the   │
    │                  capability. Travel forward to the next actor.    │
    │                  NOT present in the request envelope — this       │
    │                  prevents information spills and ensures labels    │
    │                  aren't acted upon by the capability that         │
    │                  receives the request.                            │
    │                  Schema: yo-ai.ai/schemas/governancelabels.schema │
    │                  Shape: list[str]                                 │
    │                  Examples:                                        │
    │                    "AccessTokenExpires:07:55:08TZ"               │
    │                    "data-purpose:billingForAmazonPrimeAccount"    │
    └────────────────────────────────────────────────────────────────────┘
    """

    STARTUP_MODES = frozenset({"a2a", "direct", "api", "starlette"})
    ACTOR_KINDS   = frozenset({"Agent", "Subscriber", "Service", "Tool", "WorkflowOwner", "Capability"})

    def __init__(
        self,
        *,
        # ── Correlation ────────────────────────────────────────────────
        correlation_id: str | None = None,
        task_id: str | None = None,
        # ── Actor ──────────────────────────────────────────────────────
        actor_kind: ActorKind | None = None,
        actor: dict | None = None,
        # ── Invocation mechanics ───────────────────────────────────────
        startup_mode: str | None = None,
        instance_id: str | None = None,
        caller: dict | None = None,
        # ── Subject ────────────────────────────────────────────────────
        profile: dict | None = None,          # ProfileWrapper
        subject_ref: dict | None = None,
        # ── Capability identity ────────────────────────────────────────
        capability_id: str | None = None,
        # ── Execution knobs ────────────────────────────────────────────
        slim: bool = False,
        tools: list[str] | None = None,
        dry_run: bool = False,
        trace: bool = False,
        # ── Workflow state ─────────────────────────────────────────────
        step: int | None = None,
        prior_outputs: dict | None = None,
        state: dict | None = None,
        # ── RESPONSE face ──────────────────────────────────────────────
        profile_patch: dict | None = None,    # ProfilePatch
        governance_labels: list[str] | None = None,
    ):
        # Correlation
        self.correlation_id    = correlation_id
        self.task_id           = task_id if task_id is not None else correlation_id
        # Actor
        self.actor_kind        = actor_kind
        self.actor             = actor
        # Invocation mechanics
        self.startup_mode      = startup_mode
        self.instance_id       = instance_id
        self.caller            = caller
        # Subject
        self.profile           = profile
        self.subject_ref       = subject_ref
        # Capability identity
        self.capability_id     = capability_id
        # Execution knobs
        self.slim              = slim
        self.tools             = tools
        self.dry_run           = dry_run
        self.trace             = trace
        # Workflow state
        self.step              = step
        self.prior_outputs     = prior_outputs or {}
        self.state             = state or {}
        # RESPONSE face — written by the capability
        self.profile_patch     = profile_patch
        self.governance_labels = governance_labels or []

    # ── Schema name helpers ────────────────────────────────────────────────
    @property
    def input_schema_name(self) -> str:
        """'Trust.Assign' → 'trust.assign.input.schema.json'"""
        return f"{self.capability_id.lower()}.input.schema.json" if self.capability_id else ""

    @property
    def output_schema_name(self) -> str:
        """'Trust.Assign' → 'trust.assign.output.schema.json'"""
        return f"{self.capability_id.lower()}.output.schema.json" if self.capability_id else ""

    # ── Lifecycle ──────────────────────────────────────────────────────────
    def for_capability(self, capability_id: str, **overrides) -> "YoAiContext":
        """
        Return a new YoAiContext bound to a specific capability.

        Called at dispatch time — the pipeline-level context (capability_id=None)
        becomes a capability-level context. Everything is inherited except
        capability_id and any supplied overrides.

        The response face (profile_patch, governance_labels) is NOT inherited —
        each capability starts with a clean response face.

            ctx = pipeline_ctx.for_capability("Trust.Assign", slim=True)
        """
        data = self.to_dict()
        data["capability_id"]     = capability_id
        data["profile_patch"]     = None   # clean response face
        data["governance_labels"] = []     # clean response face
        data.update(overrides)
        return self.__class__.from_dict(data)

    # ── Serialization ──────────────────────────────────────────────────────
    @classmethod
    def from_dict(cls, data: dict) -> "YoAiContext":
        """
        Construct from a plain dict.
        Unknown keys are silently ignored — forward compatible.
        """
        return cls(
            correlation_id    = data.get("correlation_id"),
            task_id           = data.get("task_id"),
            actor_kind        = data.get("actor_kind"),
            actor             = data.get("actor"),
            startup_mode      = data.get("startup_mode"),
            instance_id       = data.get("instance_id"),
            caller            = data.get("caller"),
            profile           = data.get("profile"),
            subject_ref       = data.get("subject_ref"),
            capability_id     = data.get("capability_id"),
            slim              = data.get("slim", False),
            tools             = data.get("tools"),
            dry_run           = data.get("dry_run", False),
            trace             = data.get("trace", False),
            step              = data.get("step"),
            prior_outputs     = data.get("prior_outputs"),
            state             = data.get("state"),
            profile_patch     = data.get("profile_patch"),
            governance_labels = data.get("governance_labels"),
        )

    def to_dict(self) -> dict:
        """
        Serialize to a plain dict.
        Used for logging, diagnostics, envelope passthrough, and workflow persistence.
        """
        return {
            "correlation_id":    self.correlation_id,
            "task_id":           self.task_id,
            "actor_kind":        self.actor_kind,
            "actor":             self.actor,
            "startup_mode":      self.startup_mode,
            "instance_id":       self.instance_id,
            "caller":            self.caller,
            "profile":           self.profile,
            "subject_ref":       self.subject_ref,
            "capability_id":     self.capability_id,
            "slim":              self.slim,
            "tools":             self.tools,
            "dry_run":           self.dry_run,
            "trace":             self.trace,
            "step":              self.step,
            "prior_outputs":     self.prior_outputs,
            "state":             self.state,
            "profile_patch":     self.profile_patch,
            "governance_labels": self.governance_labels,
        }