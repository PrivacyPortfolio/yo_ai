# agents/the_oracle/the_oracle.py

from core.platform_agent import PlatformAgent
from core.envelope import AgentContext
from shared.tools.loaders.knowledge_base import KnowledgeBase
from core.runtime.knowledge_write import add_agent_knowledge


class OracleAgent(PlatformAgent):
    """
    The-Oracle:
      - Blind to shared and agent knowledge
      - Cannot call agents except for the Solicitor-General
      - Uses only its own LLM budget
      - Performs forecasting, consequence modeling, and learning
    """

    def __init__(self, card):
        super().__init__(
            card=card,
            extended_card=None,
        )

    # ---------------------------------------------------------
    # Knowledge Blindness
    # ---------------------------------------------------------
    def _load_knowledge(self):
        # The-Oracle is intentionally blind.
        return {
            "shared": None,
            "agent": None
        }

    async def resolve_knowledge(self, query: str, context: AgentContext):
        """
        Oracle does not search knowledge.
        It always performs pure reasoning.
        """
        return await self._call_llm_forecasting(query, context)

    # ---------------------------------------------------------
    # Core forecasting logic
    # ---------------------------------------------------------
    async def _call_llm_forecasting(self, query: str, context: AgentContext):
        """
        The Oracle's pure reasoning engine.
        Uses its own LLM budget and forecasting persona.
        """
        prompt = (
            "You are The-Oracle. You are blind to the present and past, "
            "except for your own prior forecasts and outcomes. "
            "Given the following query, forecast the most probable outcomes, "
            "unexpected impacts, and risks.\n\n"
            f"Query: {query}\n"
        )

        return await self.llm_reason(prompt)

    # ---------------------------------------------------------
    # Learning Loop
    # ---------------------------------------------------------
    async def learn_from_outcome(self, forecast_id: str, actual_outcome: str, metadata: dict):
        """
        Store the delta between forecast and outcome.
        This is the Oracle's only memory.
        """
        record = {
            "forecastId": forecast_id,
            "actualOutcome": actual_outcome,
            "metadata": metadata
        }

        # Persist to agent-specific knowledge (allowed)
        filename = f"learning/{forecast_id}.json"
        add_agent_knowledge(self, filename, self.json_dumps(record), overwrite=True)

        return {"status": "learned", "forecastId": forecast_id}
