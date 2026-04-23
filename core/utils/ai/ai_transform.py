# core/utils/ai/ai_transform.py
#
# AI Transformation Layer.
# Builds the reasoning prompt, calls the agent's AI backend, and returns
# a structured Python dict for shape_output() to normalize.
#
# Architecture note:
#   This module delegates to agent.ai_client.chat_completion() — the agent's
#   own AI backend, configured at construction from the x-ai block.
#   Model selection (per-skill env-first resolution) is the responsibility
#   of agent.ai_client, not this module.
#   knowledge_query() enriches the prompt before that dispatch happens.
#
# See: knowledge_query.py, load_knowledge.py, knowledge_write.py

import json
import re

from core.utils.knowledge.knowledge_query import knowledge_query
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("ai_transform")


def call_ai(prompt: dict, agent) -> dict:
    """
    Knowledge-aware AI transformation for any Yo-ai agent capability.

    Every invocation:
      1a. Builds system prompt from agent persona (agent.build_system_prompt())
      1b. Queries agent-specific + shared knowledge repositories
      1c. Injects relevant knowledge fragments into the user prompt
      2.  Calls the agent's AI backend (agent.ai_client.chat_completion())
      3.  Parses and returns the result

    Parameters:
        prompt (dict): {
            "persona":      str,           # agent name / role
            "capability":   str,           # canonical capability ID
            "input":        dict,          # validated payload
            "context":      dict,          # awsRequestId, rawPath, etc.
            "instructions": str (optional) # capability-specific instructions
        }
        agent: instantiated agent runtime.
               Must provide:
                 agent.build_system_prompt() -> str
                 agent.ai_client.chat_completion(system, user) -> str
                 agent.name -> str  (used for knowledge_query)

    Returns:
        dict: AI-generated result (unshaped). Always a dict, never raises.
    """

    capability_id = prompt.get("capability", "unknown")
    agent_name    = getattr(agent, "name", agent.__class__.__name__)

    try:
        # ----------------------------------------------------------
        # 1a. Build system prompt from agent persona
        # ----------------------------------------------------------
        system_prompt = agent.build_system_prompt()

        # ----------------------------------------------------------
        # 1b. Query knowledge repositories
        #     Retrieve fragments relevant to this capability + payload.
        #     Agent-specific knowledge ranked above shared knowledge.
        #     Failures are silent — never block a capability invocation.
        # ----------------------------------------------------------
        knowledge_fragments = knowledge_query(
            agent_name=agent_name,
            capability_id=capability_id,
            payload=prompt.get("input", {}),
            agent=agent,   # passes agent.knowledge (MergedKnowledgeBase)
        )

        # ----------------------------------------------------------
        # 1c. Build user prompt — inject knowledge context
        # ----------------------------------------------------------
        user_prompt = _build_user_prompt(prompt, knowledge_fragments)

        LOG.info(
            "[AI] Executing capability: %s  agent: %s  knowledge fragments: %d",
            capability_id, agent_name, len(knowledge_fragments)
        )

        # ----------------------------------------------------------
        # 2. Call the agent's AI backend
        #    agent.ai_client handles provider selection, model
        #    resolution (env-first / x-ai per-skill), and API dispatch.
        # ----------------------------------------------------------
        ai_response = agent.ai_client.chat_completion(
            system=system_prompt,
            user=json.dumps(user_prompt, indent=2, default=str),
            capability_id=capability_id,   # enables per-skill model selection
        )

        # ----------------------------------------------------------
        # 3. Parse response
        # ----------------------------------------------------------
        result = _parse_response(ai_response)

        # Attach provenance for audit/observability.
        # shape_output() strips _ai_meta from the response envelope;
        # LogBootstrapper should capture it before that happens.
        result["_ai_meta"] = {
            "capability":         capability_id,
            "agentName":          agent_name,
            "knowledgeFragments": len(knowledge_fragments),
            "knowledgeSources":   [f["source"] for f in knowledge_fragments],
            # provider/model added by AiClient if available
            **({"provider": getattr(agent.ai_client, "_last_provider", None)}
               if hasattr(agent, "ai_client") else {}),
        }

        LOG.info("[AI] Capability %s completed successfully.", capability_id)
        return result

    except Exception as exc:
        LOG.exception(
            "[AI] Unhandled error for capability %s agent %s",
            capability_id, agent_name
        )
        return {
            "error":      str(exc),
            "capability": capability_id,
            "agentName":  agent_name,
            "_ai_meta": {
                "capability": capability_id,
                "agentName":  agent_name,
                "error":      True,
            },
        }


# ------------------------------------------------------------------
# Internal: user prompt builder
# ------------------------------------------------------------------

def _build_user_prompt(prompt: dict, knowledge_fragments: list) -> dict:
    """
    Assemble the user-facing prompt dict passed to chat_completion().

    Injects knowledge fragments as a 'knowledgeContext' block when present.
    The LLM sees source, scope, relevance score, and content for each fragment
    so it can weight them appropriately when reasoning.
    """
    user_prompt = {
        "persona":      prompt.get("persona"),
        "capability":   prompt.get("capability"),
        "input":        prompt.get("input"),
        "context":      prompt.get("context"),
        "instructions": prompt.get("instructions"),
    }

    if knowledge_fragments:
        user_prompt["knowledgeContext"] = {
            "instruction": (
                "The following knowledge fragments are relevant to this request. "
                "Consult them before reasoning. "
                "Agent-specific knowledge (scope: agent) takes priority over "
                "shared knowledge (scope: shared) when they conflict."
            ),
            "fragments": [
                {
                    "source":    f["source"],
                    "scope":     f["scope"],
                    "relevance": f["relevance"],
                    "content":   f["content"],
                }
                for f in knowledge_fragments
            ],
        }
    else:
        user_prompt["knowledgeContext"] = {
            "instruction": "No knowledge fragments were retrieved for this capability.",
            "fragments":   [],
        }

    return user_prompt


# ------------------------------------------------------------------
# Internal: response parser
# ------------------------------------------------------------------

def _parse_response(ai_response: str) -> dict:
    """
    Parse LLM text response to dict.
    Strips markdown code fences before attempting JSON parse.
    Falls back to {"rawText": <response>} if not valid JSON.
    """
    if not ai_response:
        return {"rawText": ""}

    cleaned = re.sub(r"```(?:json)?\s*", "", ai_response).replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        LOG.info("[AI] Parsed JSON response successfully.")
        if isinstance(parsed, dict):
            return parsed
        return {"result": parsed}

    except Exception:
        LOG.warning("[AI] Response was not valid JSON — returning rawText.")
        return {"rawText": ai_response}
