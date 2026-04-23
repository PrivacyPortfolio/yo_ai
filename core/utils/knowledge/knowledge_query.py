# core/utils/knowledge/knowledge_query.py
#
# Per-request knowledge retrieval — thin API over KnowledgeBase.
#
# Delegates to agent.knowledge (a MergedKnowledgeBase) which holds the
# virtual corpus index built at agent init from tree-files.txt or filesystem.
# Content is materialized on demand inside KnowledgeBase.query().
#
# This module exists as the stable external API for call_ai() in ai_transform.py.
# The retrieval logic lives in KnowledgeBase — not here.
#
# Called by: core/runtime/ai_transform.py (call_ai)
# See also:  shared/loaders/knowledge_base.py, core/runtime/load_knowledge.py

from typing import Any, Dict, List
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("knowledge_query")


# Result limits — passed through to KnowledgeBase.query()
import os
MAX_FRAGMENTS = int(os.environ.get("YO_AI_KNOWLEDGE_MAX_FRAGMENTS", "5"))


def knowledge_query(
    agent_name: str,
    capability_id: str,
    payload: Dict[str, Any],
    agent: Any = None,
    max_fragments: int = MAX_FRAGMENTS,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant knowledge fragments for a capability invocation.

    Delegates to agent.knowledge.query() if the agent has a KnowledgeBase.
    Falls back to empty list if the agent has no knowledge (slim=True,
    or knowledge loading failed at init).

    Args:
        agent_name    : Agent name — used for logging only
        capability_id : Canonical capability ID (e.g. "Trust.Assign")
        payload       : Capability input payload — keys/values become query terms
        agent         : Agent instance. Must have agent.knowledge (MergedKnowledgeBase).
                        When None, returns [].
        max_fragments : Maximum number of fragments to return

    Returns:
        List of fragment dicts:
        {
            "source":    str,   # relative file path
            "scope":     str,   # "agent" or "shared"
            "relevance": float, # 0.0–1.0
            "content":   str,   # truncated text
        }
        Sorted by relevance descending, agent scope first on ties.
        Returns [] on any failure — never raises.
    """
    if agent is None:
        LOG.debug(
            "knowledge_query: no agent provided for %s / %s — returning empty.",
            agent_name, capability_id
        )
        return []

    knowledge = getattr(agent, "knowledge", None)
    if knowledge is None:
        LOG.debug(
            "knowledge_query: agent.knowledge not set for %s (slim=True?) — returning empty.",
            agent_name
        )
        return []

    try:
        # Build query text from capability ID + flat payload values
        query_text = _build_query_text(capability_id, payload)

        fragments = knowledge.query(
            text=query_text,
            capability_id=capability_id,
            max_fragments=max_fragments,
        )

        if fragments:
            LOG.info(
                "knowledge_query: %d fragment(s) for %s / %s",
                len(fragments), agent_name, capability_id
            )
        else:
            LOG.debug(
                "knowledge_query: no relevant fragments for %s / %s",
                agent_name, capability_id
            )

        return fragments

    except Exception as exc:
        LOG.warning(
            "knowledge_query: failed for %s / %s — %s",
            agent_name, capability_id, exc
        )
        return []


def _build_query_text(capability_id: str, payload: Dict[str, Any]) -> str:
    """
    Combine capability ID and payload into a flat query string.
    KnowledgeBase.query() tokenizes this internally.
    """
    parts = [capability_id]

    def _extract(obj: Any, depth: int = 0) -> None:
        if depth > 3:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                parts.append(str(k))
                _extract(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                _extract(item, depth + 1)
        elif isinstance(obj, str) and len(obj) < 80:
            parts.append(obj)

    _extract(payload)
    return " ".join(parts)
