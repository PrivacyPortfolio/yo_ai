# agents/complaint_manager/runtime/complaint_manager_handler.py

"""
AI‑first AWS Lambda handler for the Complaint-Manager agent.

Responsibilities:
- Keep transport concerns out of agent logic
- Support warm reuse (agent instantiated once per container)
- Route capability requests to a generic AI‑first capability executor
- Let the agent runtime + AI layer synthesize transformations
- Shape output to the agent’s declared Output schema
"""

import json

from .complaint_manager import ComplaintManagerAgent
from core.utils.schema_loader import load_capability_schema
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.utils.validators.input_validator import validate_input

from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("complaint_manager_handler")

# Warm reuse: instantiate the agent once per Lambda container
AGENT = ComplaintManagerAgent()


# ------------------------------------------------------------
# Capability routing table
# ------------------------------------------------------------
# Maps capability names (from OpenAPI paths) to capability identifiers.
# These identifiers correspond to schema folders, not Python methods.
CAPABILITY_ROUTER = {
    # Example mappings — replace with your agent’s capabilities
    "LiabilityDiscover": "Liability.Discover",
    "EnforcementAgencyGet": "EnforcementAgency.Get",
    "StakeholdersGet": "Stakeholders.Get",
    "ComplaintGenerate": "Complaint.Generate",
    "ComplaintSubmit": "Complaint.Submit",
    "ComplaintPublish": "Complaint.Publish",
    "StakeholderNotify": "Stakeholder.Notify",
}


# ------------------------------------------------------------
# Lambda entrypoint
# ------------------------------------------------------------
def lambda_handler(event, context):
    """
    Expected event format (API Gateway HTTP API):
    {
        "rawPath": "/agents/<agent-name>/<CapabilityName>",
        "body": "{... JSON ...}"
    }
    """

    try:
        raw_path = event.get("rawPath", "")
        capability_name = raw_path.split("/")[-1]

        if capability_name not in CAPABILITY_ROUTER:
            raise ValueError(f"Unknown capability: {capability_name}")

        capability_id = CAPABILITY_ROUTER[capability_name]

        # Parse JSON body
        body = event.get("body") or "{}"
        payload = json.loads(body)

        # ------------------------------------------------------------
        # 1. Load capability schema (Input + Output messageTypes)
        # ------------------------------------------------------------
        capability_schema = load_capability_schema(
            agent_id=AGENT.agent_id,
            capability_id=capability_id
        )

        # ------------------------------------------------------------
        # 2. Validate input (non-blocking if configured)
        # ------------------------------------------------------------
        validated_input = validate_input(
            payload,
            capability_schema.input_schema
        )

        # ------------------------------------------------------------
        # 3. Build AI prompt (persona + capability + input + context)
        # ------------------------------------------------------------
        ai_prompt = {
            "persona": AGENT.persona,
            "agentId": AGENT.agent_id,
            "capability": capability_id,
            "input": validated_input,
            "context": {
                "awsRequestId": context.aws_request_id if context else None,
                "rawPath": raw_path,
            },
            "instructions": capability_schema.instructions,
        }

        # ------------------------------------------------------------
        # 4. AI Transformation Layer
        # ------------------------------------------------------------
        ai_result = call_ai(ai_prompt, AGENT)

        # ------------------------------------------------------------
        # 5. Shape output to match Output schema
        # ------------------------------------------------------------
        shaped_output = shape_output(
            ai_result,
            capability_schema.output_schema
        )

        # ------------------------------------------------------------
        # 6. Log event for A2A governance
        # ------------------------------------------------------------
        log_event({
            "agentId": AGENT.agent_id,
            "capability": capability_id,
            "input": validated_input,
            "output": shaped_output,
            "context": ai_prompt["context"],
        })

        # ------------------------------------------------------------
        # 7. Return envelope
        # ------------------------------------------------------------
        response = {
            "agentId": AGENT.agent_id,
            "capability": capability_id,
            "output": shaped_output,
            "timestamp": AGENT.now_iso(),
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response),
        }

    except Exception as e:
        logger.exception("Handler error")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }