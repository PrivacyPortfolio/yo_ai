# platform_event_bus_listener.py
# Passive, resource-efficient multi-tier message listener for task-driven agents

from typing import Callable, List, Set, Dict, Any
import logging
import time


class PlatformEventBusListener:
    def __init__(
        self,
        agent_id: str,
        subscribed_topics: List[str],
        thread_membership: Set[str],
        keyword_matchers: List[Callable[[str], bool]],
        relevance_heuristic: Callable[[Dict[str, Any]], float],
        ai_invoker: Callable[[Dict[str, Any]], Any],
        logger: logging.Logger = None
    ):
        self.agent_id = agent_id
        self.subscribed_topics = subscribed_topics
        self.thread_membership = thread_membership
        self.keyword_matchers = keyword_matchers
        self.relevance_heuristic = relevance_heuristic
        self.ai_invoker = ai_invoker
        self.logger = logger or logging.getLogger(agent_id)

    # -----------------------------
    # Tier 1 — Topic Filter (0–1ms)
    # -----------------------------
    def tier1_topic_filter(self, message: Dict[str, Any]) -> bool:
        topic_match = message.get("topic") in self.subscribed_topics
        thread_match = message.get("threadId") in self.thread_membership

        return topic_match or thread_match

    # -----------------------------
    # Tier 2 — Keyword / Pattern Match (1–3ms)
    # -----------------------------
    def tier2_keyword_match(self, message: Dict[str, Any]) -> bool:
        text = message.get("text", "").lower()

        mentioned = self.agent_id.lower() in text
        keyword_hit = any(fn(text) for fn in self.keyword_matchers)

        return mentioned or keyword_hit

    # -----------------------------
    # Tier 3 — Relevance Scoring (10–50ms)
    # -----------------------------
    def tier3_relevance_score(self, message: Dict[str, Any]) -> float:
        text = message.get("text", "")

        entities = self.extract_entities(text)
        intent = self.infer_intent(text)

        score = self.relevance_heuristic({
            "text": text,
            "entities": entities,
            "intent": intent,
            "threadId": message.get("threadId")
        })

        return score

    # -----------------------------
    # Tier 4 — AI Invocation (500ms–2s)
    # -----------------------------
    async def tier4_invoke_ai(self, message: Dict[str, Any]):
        self.logger.info(f"[{self.agent_id}] Invoking AI for message {message.get('id')}")
        return await self.ai_invoker({
            "agentId": self.agent_id,
            "message": message,
            "context": {"threadId": message.get("threadId")}
        })

    # -----------------------------
    # Public: handle incoming message
    # -----------------------------
    async def handle_message(self, message: Dict[str, Any]):
        # TIER 1
        if not self.tier1_topic_filter(message):
            self.logger.debug(f"[{self.agent_id}] Tier1 ignore")
            return None

        # TIER 2
        if not self.tier2_keyword_match(message):
            self.logger.debug(f"[{self.agent_id}] Tier2 log-only")
            return