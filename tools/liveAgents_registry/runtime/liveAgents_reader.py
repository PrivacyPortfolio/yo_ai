# tools/liveAgents_registry/runtime/liveAgents_reader.py

from .liveAgents_registry import REGISTRY, _log

def get_agent(agent_id, agent_ctx=None):
    _log("AgentRegistry.Read", "get_agent()", {"agent_id": agent_id}, agent_ctx)
    return REGISTRY.get_agent(agent_id)

def get_agents(agent_ctx=None):
    _log("AgentRegistry.Read", "get_agents()", None, agent_ctx)
    return REGISTRY.get_agents()
