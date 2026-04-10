# agents/the_advisor/the_advisor.py

from core.platform_agent import PlatformAgent
from core.envelope import AgentContext
from core.runtime.knowledge_write import add_agent_knowledge
import json
import uuid


class AdvisorAgent(PlatformAgent):
    """
    The-Advisor:
      - High-budget reasoning agent
      - Provides guidance, synthesis, and platform expertise
      - Has full access to shared + agent knowledge
      - Uses a Cognitive-Reasoning-Loop for deeper inference
      - Tracks whether advice was followed (learning loop)
    """
    def __init__(self, card, extended_card=None):
        super().__init__(
            card=card,
            extended_card=extended_card,
        )

    # ---------------------------------------------------------
    # Cognitive Reasoning Loop
    # ---------------------------------------------------------
    async def cognitive_reason(self, query: str, context: AgentContext):
        """
        Multi-step reasoning loop:
          1. Interpret the question
          2. Retrieve relevant knowledge
          3. Reason deeply using LLM
          4. Produce structured advice
        """

        # Step 1: Interpret
        interpretation = await self.llm_reason(
            f"Interpret the user's intent:\n\nQuery: {query}"
        )

        # Step 2: Retrieve knowledge (agent + shared)
        knowledge = await self.resolve_knowledge(query, context)

        # Step 3: Deep reasoning
        reasoning = await self.llm_reason(
            f"You are The-Advisor. Provide expert guidance.\n\n"
            f"Query: {query}\n"
            f"Interpreted Intent: {interpretation}\n"
            f"Relevant Knowledge: {knowledge}\n"
            f"Provide structured, actionable advice."
        )

        # Step 4: Produce structured output
        advice_id = str(uuid.uuid4())
        return {
            "adviceId": advice_id,
            "interpretation": interpretation,
            "knowledgeUsed": bool(knowledge),
            "advice": reasoning
        }

    # ---------------------------------------------------------
    # Friend-calling behavior
    # ---------------------------------------------------------
    async def resolve_knowledge(self, query: str, context: AgentContext):
        """
        Advisor *does* use knowledge:
          - agent knowledge
          - shared knowledge
          - fallback to LLM reasoning
        """
        return await super().resolve_knowledge(query, context)

    async def _call_friend(self, query: str, context: AgentContext):
        """
        The-Advisor never calls The-Oracle or other agents.
        It is the end of the reasoning chain.
        """
        return await self.cognitive_reason(query, context)

    # ---------------------------------------------------------
    # Learning Loop
    # ---------------------------------------------------------
    async def learn_from_outcome(self, advice_id: str, actual_behavior: str, metadata: dict):
        """
        Store whether the advice was followed or ignored.
        """
        record = {
            "adviceId": advice_id,
            "actualBehavior": actual_behavior,
            "metadata": metadata
        }

        filename = f"learning/{advice_id}.json"
        add_agent_knowledge(self, filename, json.dumps(record, indent=2), overwrite=True)

        return {"status": "advisor-learned", "adviceId": advice_id}
