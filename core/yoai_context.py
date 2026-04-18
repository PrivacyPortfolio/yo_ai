# core/yoai_context.py
#
# YoAiContext — schema artifact.
#
# A TypedDict that defines the shape of the unified interchange context for the
# YoAi platform. It is NEVER stored as an instance attribute on any agent.
#
# Usage contract:
#   - Import the type for annotations:   ctx: YoAiContext
#   - Build from an envelope:            ctx = ctx_from_envelope(envelope, agent)
#   - Advance to a capability:           ctx = ctx_for_capability(ctx, "Trust.Assign")
#   - Extract agent-init fields:         correlation_id=ctx["correlation_id"]
#   - Serialize for logging/transport:   dict(ctx)  — it already is one
#
# Lifetime: local variable or call parameter only. Never self.ctx.

from __future__ import annotations

from typing import Any, Literal, TypedDict

# ---------------------------------------------------------------------------
# Literal types
# ---------------------------------------------------------------------------

ActorKind = Literal[
    "Agent",
    "Subscriber",
    "Service",
    "Tool",
    "WorkflowOwner",
    "Capability",
]

StartupMode = Literal["a2a", "direct", "api", "starlette"]


# ---------------------------------------------------------------------------
# YoAiContext
# ---------------------------------------------------------------------------

class YoAiContext(TypedDict, total=False):
    """
    The single unified interchange context for the YoAi platform.

    Constructed once per request-response interchange and passed as a call
    parameter into every capability handler. Never stored on agent instances.

    Two temporal faces
    ──────────────────
    REQUEST face   Populated at construction from the incoming envelope.
                   Answers: who is asking, on whose behalf, for what, how.

    RESPONSE face  Written by the capability as it produces its result.
                   Answers: what changed, what should travel forward.

    ┌─ Correlation ──────────────────────────────────────────────────────┐
    │ correlation_id   JSON-RPC id. Primary request-response handle.     │
    │                  Set by A2ATransport at the protocol boundary.     │
    │ task_id          A2A task identifier.                              │
    │                  Defaults to correlation_id if absent.            │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Actor (REQUEST) ──────────────────────────────────────────────────┐
    │ actor_kind       What kind of entity invoked this operation.       │
    │ actor            Identity dict of the invoking entity.            │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Invocation mechanics (REQUEST) ───────────────────────────────────┐
    │ startup_mode     How the request entered the platform.             │
    │ instance_id      Runtime identity of the handling agent instance.  │
    │                  None for PlatformAgents.                         │
    │ caller           Registered caller identity for trust-gated access.│
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Subject (REQUEST) ────────────────────────────────────────────────┐
    │ profile          ProfileWrapper — lightweight profile snippet.     │
    │                  Shape: {type, name?, payload}                    │
    │ subject_ref      Lightweight pointer to the request subject.      │
    └────────────────────────────────────────────────────────────────────┘

    ┌─ Capability identity (REQUEST) ────────────────────────────────────┐
    │ capability_id    The capability being invoked, e.g. "Trust.Assign"│
    │                  None at pipeline level; bound via                │
    │                  ctx_for_capability().                            │
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
    │ profile_patch    Fields discovered during execution not present in │
    │                  the original profile. Forwarded to Data-Steward. │
    │                  Shape: {type, payload}                           │
    │ governance_labels  Sticky notes attached by the capability.       │
    │                  NOT present in request envelopes — prevents      │
    │                  information spills between capabilities.         │
    │                  Shape: list[str]                                 │
    └────────────────────────────────────────────────────────────────────┘
    """

    # ── Correlation ────────────────────────────────────────────────────
    correlation_id:    str | None
    task_id:           str | None

    # ── Actor ──────────────────────────────────────────────────────────
    actor_kind:        ActorKind | None
    actor:             dict[str, Any] | None

    # ── Invocation mechanics ───────────────────────────────────────────
    startup_mode:      StartupMode | None
    instance_id:       str | None
    caller:            dict[str, Any] | None

    # ── Subject ────────────────────────────────────────────────────────
    profile:           dict[str, Any] | None   # ProfileWrapper
    subject_ref:       dict[str, Any] | None

    # ── Capability identity ────────────────────────────────────────────
    capability_id:     str | None

    # ── Execution knobs ────────────────────────────────────────────────
    slim:              bool
    tools:             list[str] | None
    dry_run:           bool
    trace:             bool

    # ── Workflow state ─────────────────────────────────────────────────
    step:              int | None
    prior_outputs:     dict[str, Any]
    state:             dict[str, Any]

    # ── RESPONSE face ──────────────────────────────────────────────────
    profile_patch:     dict[str, Any] | None   # ProfilePatch
    governance_labels: list[str]


# ---------------------------------------------------------------------------
# Schema names — pure functions, no instance needed
# ---------------------------------------------------------------------------

def input_schema_name(ctx: YoAiContext) -> str:
    """'Trust.Assign' → 'trust.assign.input.schema.json'"""
    cap = ctx.get("capability_id")
    return f"{cap.lower()}.input.schema.json" if cap else ""


def output_schema_name(ctx: YoAiContext) -> str:
    """'Trust.Assign' → 'trust.assign.output.schema.json'"""
    cap = ctx.get("capability_id")
    return f"{cap.lower()}.output.schema.json" if cap else ""


# ---------------------------------------------------------------------------
# Factory: build from a raw envelope
# ---------------------------------------------------------------------------

def ctx_from_envelope(
    envelope: dict[str, Any],
    *,
    instance_id: str | None = None,
    correlation_id: str | None = None,
    task_id: str | None = None,
    profile: dict[str, Any] | None = None,
) -> YoAiContext:
    """
    Build a YoAiContext from an incoming request envelope.

    The envelope is the authoritative source for request-scoped fields.
    Agent identity fields (instance_id, correlation_id, task_id, profile)
    are supplied explicitly by the caller — typically YoAiAgent._build_context()
    — so the agent's own resolved values take precedence over anything
    the envelope might carry for those fields.

    Returns a plain dict conforming to YoAiContext. No class instantiated,
    nothing stored on any agent.
    """
    raw_ctx: dict[str, Any] = envelope.get("ctx", {}) or {}
    meta:    dict[str, Any] = envelope.get("meta", {}) or {}

    resolved_correlation = (
        correlation_id
        or raw_ctx.get("correlation_id")
        or meta.get("correlation_id")
    )
    resolved_task = (
        task_id
        or raw_ctx.get("task_id")
        or meta.get("task_id")
        or resolved_correlation
    )

    ctx: YoAiContext = {
        # ── Correlation ────────────────────────────────────────────────
        "correlation_id":    resolved_correlation,
        "task_id":           resolved_task,

        # ── Actor ──────────────────────────────────────────────────────
        "actor_kind":        raw_ctx.get("actor_kind"),
        "actor":             raw_ctx.get("actor"),

        # ── Invocation mechanics ───────────────────────────────────────
        "startup_mode":      raw_ctx.get("startup_mode") or meta.get("startup_mode"),
        "instance_id":       instance_id,
        "caller":            raw_ctx.get("caller"),

        # ── Subject ────────────────────────────────────────────────────
        "profile":           profile if profile is not None else raw_ctx.get("profile"),
        "subject_ref":       raw_ctx.get("subject_ref"),

        # ── Capability identity ────────────────────────────────────────
        "capability_id":     raw_ctx.get("capability_id"),

        # ── Execution knobs ────────────────────────────────────────────
        "slim":              bool(raw_ctx.get("slim", False)),
        "tools":             raw_ctx.get("tools"),
        "dry_run":           bool(raw_ctx.get("dry_run", False)),
        "trace":             bool(raw_ctx.get("trace", False)),

        # ── Workflow state ─────────────────────────────────────────────
        "step":              raw_ctx.get("step"),
        "prior_outputs":     raw_ctx.get("prior_outputs") or {},
        "state":             raw_ctx.get("state") or {},

        # ── RESPONSE face (clean for every new request) ────────────────
        "profile_patch":     None,
        "governance_labels": [],
    }

    return ctx


# ---------------------------------------------------------------------------
# Factory: advance to a specific capability
# ---------------------------------------------------------------------------

def ctx_for_capability(
    ctx: YoAiContext,
    capability_id: str,
    **overrides: Any,
) -> YoAiContext:
    """
    Return a new YoAiContext bound to a specific capability.

    Called at dispatch time — the pipeline-level context (capability_id=None)
    becomes a capability-level context. All request-face fields are inherited.
    The response face (profile_patch, governance_labels) is always reset so
    each capability starts clean and cannot read labels placed by a prior one.

    Any keyword overrides are applied after the copy:
        ctx = ctx_for_capability(pipeline_ctx, "Trust.Assign", slim=True)
    """
    advanced: YoAiContext = {**ctx}  # shallow copy — all values are scalars or immutable refs
    advanced["capability_id"]     = capability_id
    advanced["profile_patch"]     = None   # clean response face
    advanced["governance_labels"] = []     # clean response face
    advanced.update(overrides)             # type: ignore[typeddict-item]
    return advanced
