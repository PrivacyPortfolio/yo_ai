# tools/liveAgents_registry/runtime/liveAgents_writer.py

from .liveAgents_registry import REGISTRY, _log

def register(payload, agent_ctx=None, capability_ctx=None):
    _log("AgentRegistry.Write", "register()", payload, agent_ctx, capability_ctx)
    return REGISTRY.register(payload)

def heartbeat(agent_id, instance_id, ts, agent_ctx=None):
    _log("AgentRegistry.Write", "heartbeat()", {"agent_id": agent_id}, agent_ctx)
    return REGISTRY.heartbeat(agent_id, instance_id, ts)

def mark_stopped(agent_id, instance_id, ts, agent_ctx=None):
    _log("AgentRegistry.Write", "mark_stopped()", {"agent_id": agent_id}, agent_ctx)
    return REGISTRY.mark_stopped(agent_id, instance_id, ts)
