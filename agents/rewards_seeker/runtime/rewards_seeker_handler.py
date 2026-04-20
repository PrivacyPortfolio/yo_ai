# agents/rewards_seeker/runtime/rewards_seeker_handler.py

"""
AI‑first AWS Lambda handler for the Rewards-Seeker agent.

Responsibilities:
- Keep transport concerns out of agent logic
- Support warm reuse (agent instantiated once per container)
- Route capability requests to a generic AI‑first capability executor
- Let the agent runtime + AI layer synthesize transformations
- Shape output to the agent’s declared Output schema
"""

import json
from datetime import datetime, timezone

from rewards_seeker import RewardsSeekerAgent
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from core.yoai_context import input_schema_name, output_schema_name
from core.utils.validators.schema_validator import schema_validator
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.observability.logging.log_bootstrapper import get_logger

_logger = get_logger("rewards-seeker-handler")


# ── Module-level singleton ─────────────────────────────────────────────────

_AGENT = RewardsSeekerAgent(slim=True)

# ── Capability routing ─────────────────────────────────────────────────────

_CAPABILITY_ROUTER = {
"Rewards.Discover": "Rewards.Discover",
"PromoEligibilityVerify": "Promo-Eligibility.Verify",
"RewardRedeem": "Reward.Redeem",
"RewardsProfileRequest": "Rewards-Profile.Request",
"RedemptionPlanGenerate": "Redemption-Plan.Generate"
}


# ------------------------------------------------------------
# Lambda entrypoint
# ------------------------------------------------------------
def lambda_handler(event, context):
    raw_path = event.get("rawPath", "")
    aws_request_id = getattr(context, "aws_request_id", None) if context else None

    try:
        # ── Route resolution ───────────────────────────────────────────────
        path_segment  = raw_path.rstrip("/").split("/")[-1]
        capability_id = _CAPABILITY_ROUTER.get(path_segment)
        if not capability_id:
            return _error(400, f"Unknown capability: {path_segment}")

        body     = json.loads(event.get("body") or "{}")
        payload  = body.get("payload", body)
        ctx_data = body.get("ctx", {})

        # ── Seed YoAiContext at the transport boundary ──────────────────────
        correlation_id, task_id = _AGENT.generate_message_ids(
            request_id=aws_request_id,
            task_id=ctx_data.get("task_id"),
        )

        envelope = {
            "payload": payload,
            "ctx": {
                "startup_mode":  ctx_data.get("startup_mode", "api"),
                "caller":        ctx_data.get("caller"),
                "profile":       ctx_data.get("profile"),
                "subject_ref":   ctx_data.get("subject_ref"),
                "slim":          ctx_data.get("slim", True),
                "dry_run":       ctx_data.get("dry_run", False),
                "trace":         ctx_data.get("trace", False),
                "step":          ctx_data.get("step"),
                "prior_outputs": ctx_data.get("prior_outputs"),
                "state":         ctx_data.get("state"),
            },
        }

        pipeline_ctx: YoAiContext = ctx_from_envelope(
            envelope,
            **_AGENT.as_actor_stub(),
            instance_id=_AGENT.instance_id,
            correlation_id=correlation_id,
            task_id=task_id,
            profile=ctx_data.get("profile"),
        )

        ctx: YoAiContext = ctx_for_capability(pipeline_ctx, capability_id)

        # ── Input validation ───────────────────────────────────────────────
        i_schema_name     = input_schema_name(ctx)
        validation_errors = schema_validator.validate_input(i_schema_name, payload)
        if validation_errors:
            _logger.write({
                "event_type": "Handler.ValidationFailed",
                "level":      "WARNING",
                "payload": {
                    "capability":    capability_id,
                    "schemaName":    i_schema_name,
                    "errors":        validation_errors,
                    "correlationId": ctx.get("correlation_id"),
                },
            })
            return _error(400, f"Input validation failed: {validation_errors}")

        # ── AI-first execution ─────────────────────────────────────────────
        if ctx.get("dry_run"):
            result = {"status": "dry_run", "capability": capability_id, "payload": payload}
        else:
            result = call_ai(
                {
                    "persona":    _AGENT.name,
                    "agentId":    _AGENT.agent_id,
                    "capability": capability_id,
                    "input":      payload,
                    "context": {
                        "awsRequestId":  aws_request_id,
                        "rawPath":       raw_path,
                        "correlationId": ctx.get("correlation_id"),
                        "taskId":        ctx.get("task_id"),
                    },
                },
                _AGENT,
            )

        # ── Output shaping ─────────────────────────────────────────────────
        o_schema_name = output_schema_name(ctx)
        shaped_output = shape_output(result, o_schema_name) if o_schema_name else result

        # ── Completion log ─────────────────────────────────────────────────
        _logger.write({
            "event_type": "Handler.Complete",
            "level":      "INFO",
            "payload": {
                "agentName":     _AGENT.name,
                "capability":    capability_id,
                "correlationId": ctx.get("correlation_id"),
                "taskId":        ctx.get("task_id"),
                "dryRun":        ctx.get("dry_run"),
                "awsRequestId":  aws_request_id,
            },
        })

        # ── Return envelope ─────────────────────────────────────────────────
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "method":  f"a2a.{capability_id}",
                "result":  shaped_output,
                "metadata": {
                    "agentName":     _AGENT.name,
                    "capability":    capability_id,
                    "correlationId": ctx.get("correlation_id"),
                    "taskId":        ctx.get("task_id"),
                    "timestamp":     datetime.now(timezone.utc).isoformat(),
                },
            }),
        }

    except Exception as e:
        _logger.write({
            "event_type": "Handler.Error",
            "level":      "ERROR",
            "payload": {
                "error":        str(e),
                "awsRequestId": aws_request_id,
                "rawPath":      raw_path,
            },
        })
        return _error(500, str(e))

# ── Error helper ───────────────────────────────────────────────────────────

def _error(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
