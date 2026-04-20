# agents/visiting_agent/visiting_agent.py
#
# VisitingAgent — a minimal A2A-capable agent for test and demo purposes.
#
# Subclasses BaseAgent directly (not YoAiAgent) because a visiting agent:
#   - Has no AI client, tool registry, or governance artifacts
#   - Does not need profile-aware identity or slim/full init modes
#   - IS a proper A2A agent with identity, skills, and message-id generation
#
# By subclassing BaseAgent it gets for free:
#   - generate_message_ids()    — A2A-compliant correlation_id / task_id pair
#   - as_actor_stub()           — identity fragment for seeding YoAiContext
#   - validate_security()       — header-based security validation
#   - invoke()                  — skill dispatch
#   - to_json()                 — card serialization
#
# _build_context() is added here — same pattern as YoAiAgent — to show that
# any BaseAgent subclass can seed a YoAiContext for its exchanges.
#
# WebSocket transport lives in VisitingAgentSession (separate class) so the
# agent identity and the connection lifecycle remain cleanly decoupled.

import asyncio
import json
import random
from typing import Any, Dict, Optional

import websockets

from core.base_agent import BaseAgent
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from config import AgentConfig, WebSocketConfig


# ---------------------------------------------------------------------------
# Card builder — constructs a minimal A2A-compliant agent card dict from config
# ---------------------------------------------------------------------------

def _build_card(cfg: AgentConfig, ws_cfg: WebSocketConfig) -> Dict[str, Any]:
    # Builds the card that BaseAgent.__init__ freezes and indexes.
    # Visiting agents have a single skill: explore-environment.
    return {
        "id":          cfg.agent_id,
        "name":        cfg.agent_name,
        "description": "Minimal visiting agent for A2A test and demo exchanges.",
        "provider":    {"name": cfg.vendor},
        "protocolVersion": "1.0",
        "supportedInterfaces": [
            {
                "url":             ws_cfg.url,
                "protocolBinding": "WEBSOCKET",
                "protocolVersion": "1.0",
            }
        ],
        "capabilities": {
            "streaming":         False,
            "pushNotifications": False,
        },
        "security":        [],
        "securitySchemes": {},
        "defaultInputModes":  ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "name":        "explore-environment",
                "description": "Sends observations and interprets returned actions.",
            }
        ],
    }


# ---------------------------------------------------------------------------
# VisitingAgent
# ---------------------------------------------------------------------------

class VisitingAgent(BaseAgent):
    # -- Identity and A2A interfaces, no AI machinery ----------------------
    # Demonstrates that any BaseAgent subclass — regardless of origin or
    # vendor — gets the same A2A interfaces as platform agents.

    def __init__(
        self,
        agent_cfg: AgentConfig,
        ws_cfg: WebSocketConfig,
    ) -> None:
        card = _build_card(agent_cfg, ws_cfg)
        super().__init__(agent_card=card)

        # Flat config references — not part of the frozen card
        self.num_steps = agent_cfg.num_steps
        self.ws_url    = ws_cfg.url
        self.timeout   = ws_cfg.timeout_seconds

        # Correlation and task ids — seeded once per session via
        # generate_message_ids() (inherited from BaseAgent).
        # These mirror the pattern in YoAiAgent: flat attrs, set once,
        # updated by set_correlation() if needed.
        self.correlation_id: str | None = None
        self.task_id:        str | None = None

    def start_session(self, request_id: str | None = None) -> None:
        # Seed message ids for this session — same call as YoAiAgent.set_correlation()
        self.correlation_id, self.task_id = self.generate_message_ids(
            request_id=request_id,
        )

    def _build_context(
        self,
        envelope: dict,
        capability_id: str | None = None,
    ) -> YoAiContext:
        # Build a YoAiContext from an inbound envelope — same pattern as
        # YoAiAgent._build_context(). Demonstrates the interface is available
        # to any BaseAgent subclass via ctx_from_envelope().
        ctx = ctx_from_envelope(
            envelope,
            **self.as_actor_stub(),           # actor_kind, actor
            instance_id=self.agent_id,        # BaseAgent owns agent_id
            correlation_id=self.correlation_id,
            task_id=self.task_id,
            profile=None,                     # visiting agents have no profile
        )
        if capability_id:
            ctx = ctx_for_capability(ctx, capability_id)
        return ctx

    def build_observation(self, step: int) -> Dict[str, Any]:
        # Constructs a plain observation payload — not wrapped in an envelope yet.
        return {
            "agent_id": self.agent_id,
            "position": {"x": step, "y": step + 1},
            "velocity": {"x": 0.5, "y": 0.1},
            "emotion":  random.choice(["neutral", "afraid"]),
        }

    def wrap_in_envelope(
        self,
        payload: dict,
        capability_id: str = "explore-environment",
    ) -> dict:
        # Wraps an observation in a minimal A2A-compliant JSON-RPC envelope.
        # correlation_id becomes the JSON-RPC "id" — A2A spec alignment.
        return {
            "jsonrpc":    "2.0",
            "id":         self.correlation_id,
            "method":     f"a2a.{capability_id}",
            "params": {
                "capability": capability_id,
                "payload":    payload,
                "ctx": {
                    "startup_mode":  "a2a",
                    "correlation_id": self.correlation_id,
                    "task_id":        self.task_id,
                    "actor_kind":     "Agent",
                    "actor":          self.as_actor_stub()["actor"],
                },
            },
        }


# ---------------------------------------------------------------------------
# VisitingAgentSession — WebSocket transport, decoupled from identity
# ---------------------------------------------------------------------------

class VisitingAgentSession:
    # -- Manages the WebSocket connection lifecycle for one visiting session --

    def __init__(self, agent: VisitingAgent) -> None:
        self.agent = agent

    async def run(self) -> None:
        agent = self.agent
        print(f"[VisitingAgent] Connecting to {agent.ws_url} as {agent.name} "
              f"({agent.agent_id})")
        print(f"[VisitingAgent] correlation_id={agent.correlation_id}  "
              f"task_id={agent.task_id}")

        async with websockets.connect(
            agent.ws_url,
            open_timeout=agent.timeout,
        ) as ws:
            print("[VisitingAgent] Connected.")

            for step in range(agent.num_steps):
                # Build observation and wrap in envelope
                obs     = agent.build_observation(step)
                envelope = agent.wrap_in_envelope(obs, capability_id="explore-environment")

                # Build ctx for this exchange — demonstrates _build_context()
                ctx = agent._build_context(envelope, capability_id="explore-environment")

                print(f"\n[VisitingAgent] Step {step} — sending envelope")
                print(f"  capability_id  : {ctx.get('capability_id')}")
                print(f"  correlation_id : {ctx.get('correlation_id')}")
                print(f"  task_id        : {ctx.get('task_id')}")
                print(f"  actor_kind     : {ctx.get('actor_kind')}")
                print(f"  actor.name     : {ctx.get('actor', {}).get('name')}")
                print(f"  payload        : {obs}")

                await ws.send(json.dumps(envelope))

                # Receive and parse response
                try:
                    raw      = await asyncio.wait_for(ws.recv(), timeout=agent.timeout)
                    response = json.loads(raw)
                except asyncio.TimeoutError:
                    print(f"[VisitingAgent] Step {step} — response timed out.")
                    continue
                except json.JSONDecodeError as exc:
                    print(f"[VisitingAgent] Step {step} — non-JSON response: {raw}")
                    continue

                print(f"[VisitingAgent] Step {step} — received response:")
                print(f"  {json.dumps(response, indent=2)}")

                await _handle_action(response)
                await asyncio.sleep(1.0)

        print("\n[VisitingAgent] Session complete.")


async def _handle_action(response: dict) -> None:
    result  = response.get("result", response)
    command = result.get("command")
    message = result.get("message")
    print(f"[VisitingAgent] Action — command={command!r}  message={message!r}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main(agent_cfg: AgentConfig = None, ws_cfg: WebSocketConfig = None) -> None:
    from config import agent_config, ws_config
    agent_cfg = agent_cfg or agent_config
    ws_cfg    = ws_cfg    or ws_config

    agent = VisitingAgent(agent_cfg=agent_cfg, ws_cfg=ws_cfg)
    agent.start_session()

    session = VisitingAgentSession(agent)
    await session.run()
