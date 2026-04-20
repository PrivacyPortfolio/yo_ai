# tests/test_visiting_agent.py
#
# Standalone test for VisitingAgent as a BaseAgent subclass.
# No test framework or live server required — run directly:
#
#   python tests/test_visiting_agent.py
#
# Demonstrates:
#   1. VisitingAgent is a proper BaseAgent subclass
#   2. generate_message_ids() produces valid A2A correlation_id / task_id
#   3. as_actor_stub() produces the correct identity fragment
#   4. _build_context() seeds a valid YoAiContext from an envelope
#   5. ctx_for_capability() binds capability_id correctly
#   6. wrap_in_envelope() produces a valid JSON-RPC 2.0 / A2A envelope
#   7. BaseAgent identity fields are correctly set from the card
#   8. skill_specs indexed correctly from card skills
#   9. generate_message_ids() respects supplied request_id
#  10. Multiple sessions produce distinct correlation_ids

import asyncio
import sys

sys.path.insert(0, ".")

from core.base_agent import BaseAgent
from core.yoai_context import YoAiContext
from agents.visiting_agent.config import AgentConfig, WebSocketConfig
from agents.visiting_agent.visiting_agent import VisitingAgent


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

RESULTS = []


def _pass(name):
    RESULTS.append({"name": name, "status": "PASS"})
    print(f"  [PASS]  {name}")


def _fail(name, reason=""):
    RESULTS.append({"name": name, "status": "FAIL", "reason": reason})
    print(f"  [FAIL]  {name} — {reason}")


def _assert(condition, name, reason=""):
    if condition:
        _pass(name)
    else:
        _fail(name, reason or "assertion failed")


def _section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def _make_agent(num_steps=2) -> VisitingAgent:
    return VisitingAgent(
        agent_cfg=AgentConfig(
            agent_id="visiting-agent-pedantic",
            agent_name="Visiting Agent (FastA2A WebSocket)",
            vendor="pedantic.ai",
            num_steps=num_steps,
        ),
        ws_cfg=WebSocketConfig(url="ws://localhost:8000/ws"),
    )


# ---------------------------------------------------------------------------
# 1. VisitingAgent is a proper BaseAgent subclass
# ---------------------------------------------------------------------------

def test_is_base_agent_subclass():
    _section("1. VisitingAgent is a BaseAgent subclass")
    agent = _make_agent()

    _assert(isinstance(agent, BaseAgent), "isinstance(agent, BaseAgent)")
    _assert(isinstance(agent, VisitingAgent), "isinstance(agent, VisitingAgent)")
    _assert(hasattr(agent, "generate_message_ids"), "has generate_message_ids()")
    _assert(hasattr(agent, "as_actor_stub"),         "has as_actor_stub()")
    _assert(hasattr(agent, "_build_context"),        "has _build_context()")
    _assert(hasattr(agent, "validate_security"),     "has validate_security()")
    _assert(hasattr(agent, "invoke"),                "has invoke()")
    _assert(hasattr(agent, "to_json"),               "has to_json()")

    print(f"  [INFO] agent.name      = {agent.name!r}")
    print(f"  [INFO] agent.agent_id  = {agent.agent_id!r}")
    print(f"  [INFO] agent.provider  = {agent.provider!r}")


# ---------------------------------------------------------------------------
# 2. generate_message_ids() — A2A compliant ids
# ---------------------------------------------------------------------------

def test_generate_message_ids():
    _section("2. generate_message_ids() — A2A correlation_id / task_id")
    agent = _make_agent()

    correlation_id, task_id = agent.generate_message_ids()

    _assert(isinstance(correlation_id, str), "correlation_id is a string")
    _assert(isinstance(task_id, str),        "task_id is a string")
    _assert(len(correlation_id) > 0,         "correlation_id is non-empty")
    _assert(task_id == correlation_id,       "task_id defaults to correlation_id")

    print(f"  [EVENT] generate_message_ids | correlation_id={correlation_id} | task_id={task_id}")


# ---------------------------------------------------------------------------
# 3. as_actor_stub() — identity fragment for YoAiContext
# ---------------------------------------------------------------------------

def test_as_actor_stub():
    _section("3. as_actor_stub() — identity fragment")
    agent = _make_agent()
    stub  = agent.as_actor_stub()

    _assert("actor_kind" in stub,                          "stub has actor_kind")
    _assert("actor"      in stub,                          "stub has actor")
    _assert(stub["actor_kind"] == "Agent",                 "actor_kind is 'Agent'")
    _assert(stub["actor"]["agent_id"] == agent.agent_id,   "actor.agent_id matches")
    _assert(stub["actor"]["name"]     == agent.name,       "actor.name matches")
    _assert("instance_id" not in stub,                     "no instance_id in stub (BaseAgent)")
    _assert("provider"    in stub["actor"],                "actor has provider")

    print(f"  [EVENT] as_actor_stub | actor_kind={stub['actor_kind']!r} | "
          f"agent_id={stub['actor']['agent_id']!r} | name={stub['actor']['name']!r}")


# ---------------------------------------------------------------------------
# 4. _build_context() — seeds a valid YoAiContext from an envelope
# ---------------------------------------------------------------------------

def test_build_context():
    _section("4. _build_context() — builds YoAiContext from envelope")
    agent = _make_agent()
    agent.start_session()

    obs      = agent.build_observation(step=0)
    envelope = agent.wrap_in_envelope(obs, capability_id="explore-environment")
    ctx      = agent._build_context(envelope, capability_id="explore-environment")

    _assert(isinstance(ctx, dict),                          "ctx is a dict (TypedDict)")
    _assert(ctx.get("correlation_id") == agent.correlation_id, "ctx.correlation_id matches agent")
    _assert(ctx.get("task_id")        == agent.task_id,        "ctx.task_id matches agent")
    _assert(ctx.get("actor_kind")     == "Agent",              "ctx.actor_kind is 'Agent'")
    _assert(ctx.get("instance_id")    == agent.agent_id,       "ctx.instance_id is agent_id")
    _assert(ctx.get("capability_id")  == "explore-environment","ctx.capability_id bound")
    _assert(ctx.get("startup_mode")   == "a2a",                "ctx.startup_mode is 'a2a'")
    _assert(ctx.get("profile")        is None,                 "ctx.profile is None (visiting)")

    print(f"  [EVENT] _build_context | capability_id={ctx.get('capability_id')!r} | "
          f"correlation_id={ctx.get('correlation_id')} | actor_kind={ctx.get('actor_kind')!r}")
    print(f"  [INFO]  ctx keys: {sorted(ctx.keys())}")


# ---------------------------------------------------------------------------
# 5. ctx_for_capability() — binds capability_id, resets response face
# ---------------------------------------------------------------------------

def test_ctx_for_capability():
    _section("5. ctx_for_capability() — capability binding and clean response face")
    from core.yoai_context import ctx_for_capability

    agent = _make_agent()
    agent.start_session()

    obs      = agent.build_observation(step=0)
    envelope = agent.wrap_in_envelope(obs)
    base_ctx = agent._build_context(envelope)

    cap_ctx  = ctx_for_capability(base_ctx, "explore-environment")

    _assert(cap_ctx.get("capability_id")     == "explore-environment", "capability_id bound")
    _assert(cap_ctx.get("profile_patch")     is None,                  "profile_patch reset (clean)")
    _assert(cap_ctx.get("governance_labels") == [],                     "governance_labels reset (clean)")
    _assert(cap_ctx.get("correlation_id")    == agent.correlation_id,   "correlation_id preserved")

    print(f"  [EVENT] ctx_for_capability | capability_id={cap_ctx.get('capability_id')!r} | "
          f"profile_patch={cap_ctx.get('profile_patch')!r} | "
          f"governance_labels={cap_ctx.get('governance_labels')!r}")


# ---------------------------------------------------------------------------
# 6. wrap_in_envelope() — valid JSON-RPC 2.0 / A2A shape
# ---------------------------------------------------------------------------

def test_wrap_in_envelope():
    _section("6. wrap_in_envelope() — JSON-RPC 2.0 + A2A shape")
    agent = _make_agent()
    agent.start_session()

    obs      = agent.build_observation(step=1)
    envelope = agent.wrap_in_envelope(obs, capability_id="explore-environment")

    _assert(envelope.get("jsonrpc") == "2.0",                      "jsonrpc is '2.0'")
    _assert(envelope.get("id")      == agent.correlation_id,        "id is correlation_id")
    _assert("a2a." in envelope.get("method", ""),                  "method has 'a2a.' prefix")
    _assert("params" in envelope,                                   "envelope has params")
    _assert("payload" in envelope["params"],                        "params has payload")
    _assert("ctx"     in envelope["params"],                        "params has ctx block")
    _assert(envelope["params"]["ctx"]["correlation_id"] == agent.correlation_id,
            "ctx.correlation_id in envelope matches agent")

    print(f"  [EVENT] wrap_in_envelope | id={envelope['id']} | "
          f"method={envelope['method']!r} | capability={envelope['params']['capability']!r}")


# ---------------------------------------------------------------------------
# 7. BaseAgent identity fields set from card
# ---------------------------------------------------------------------------

def test_identity_from_card():
    _section("7. BaseAgent identity fields set from card")
    agent = _make_agent()

    _assert(agent.name        == "Visiting Agent (FastA2A WebSocket)", "name from card")
    _assert(agent.agent_id    == "visiting-agent-pedantic",            "agent_id from card")
    _assert(agent.description is not None,                             "description from card")
    _assert(agent.provider    == {"name": "pedantic.ai"},              "provider from card")
    _assert(agent.protocol_version == "1.0",                          "protocol_version from card")

    print(f"  [INFO] name={agent.name!r}")
    print(f"  [INFO] agent_id={agent.agent_id!r}")
    print(f"  [INFO] provider={agent.provider!r}")


# ---------------------------------------------------------------------------
# 8. skill_specs indexed from card
# ---------------------------------------------------------------------------

def test_skill_specs():
    _section("8. skill_specs — indexed from card skills[]")
    agent = _make_agent()

    _assert("explore-environment" in agent.skill_specs,
            "explore-environment in skill_specs")
    _assert(agent.skill_specs["explore-environment"]["name"] == "explore-environment",
            "skill_specs entry has correct name")

    print(f"  [INFO] skill_specs keys: {list(agent.skill_specs.keys())}")


# ---------------------------------------------------------------------------
# 9. generate_message_ids() respects supplied request_id
# ---------------------------------------------------------------------------

def test_generate_message_ids_with_request_id():
    _section("9. generate_message_ids() — respects supplied request_id")
    agent       = _make_agent()
    request_id  = "jsonrpc-req-abc-123"

    correlation_id, task_id = agent.generate_message_ids(request_id=request_id)

    _assert(correlation_id == request_id,    "correlation_id equals supplied request_id")
    _assert(task_id        == request_id,    "task_id falls back to correlation_id")

    print(f"  [EVENT] generate_message_ids (with request_id) | "
          f"correlation_id={correlation_id} | task_id={task_id}")


# ---------------------------------------------------------------------------
# 10. Multiple sessions produce distinct correlation_ids
# ---------------------------------------------------------------------------

def test_multiple_sessions_distinct_ids():
    _section("10. Multiple sessions — distinct correlation_ids")
    agent1 = _make_agent()
    agent2 = _make_agent()

    agent1.start_session()
    agent2.start_session()

    _assert(agent1.correlation_id != agent2.correlation_id,
            "distinct correlation_ids across sessions",
            f"both got {agent1.correlation_id!r}")
    _assert(agent1.task_id != agent2.task_id,
            "distinct task_ids across sessions")

    print(f"  [EVENT] session 1 | correlation_id={agent1.correlation_id}")
    print(f"  [EVENT] session 2 | correlation_id={agent2.correlation_id}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all():
    print("\nVisitingAgent — BaseAgent interface test suite")
    print("=" * 60)

    test_is_base_agent_subclass()
    test_generate_message_ids()
    test_as_actor_stub()
    test_build_context()
    test_ctx_for_capability()
    test_wrap_in_envelope()
    test_identity_from_card()
    test_skill_specs()
    test_generate_message_ids_with_request_id()
    test_multiple_sessions_distinct_ids()

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    if failed:
        print("\nFAILED:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r.get('reason', '')}")
    print("=" * 60)
    return failed


if __name__ == "__main__":
    failed = run_all()
    sys.exit(1 if failed else 0)
