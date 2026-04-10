import asyncio
import json
import random
import websockets

from typing import Dict, Any
from config import ws_config, agent_config


class VisitingAgent:
    def __init__(self, agent_id: str, ws_url: str):
        self.agent_id = agent_id
        self.ws_url = ws_url

    async def _build_observation(self, step: int) -> Dict[str, Any]:
        # Simple deterministic position, random emotion
        return {
            "agent_id": self.agent_id,
            "position": {"x": step, "y": step + 1},
            "velocity": {"x": 0.5, "y": 0.1},
            "emotion": random.choice(["neutral", "afraid"]),
        }

    async def run_session(self, num_steps: int = 3) -> None:
        print(f"[Agent] Connecting to {self.ws_url} as {self.agent_id}...")
        async with websockets.connect(self.ws_url) as ws:
            print("[Agent] Connected.")

            for step in range(num_steps):
                obs = await self._build_observation(step)
                await ws.send(json.dumps(obs))
                print(f"[Agent] Sent observation: {obs}")

                response_raw = await ws.recv()
                try:
                    action = json.loads(response_raw)
                except json.JSONDecodeError:
                    print(f"[Agent] Received non-JSON response: {response_raw}")
                    continue

                print(f"[Agent] Received action: {action}")
                await self._handle_action(action)

                await asyncio.sleep(1.0)

        print("[Agent] Session complete.")

    async def _handle_action(self, action: Dict[str, Any]) -> None:
        command = action.get("command")
        message = action.get("message")
        print(f"[Agent] Handling action -> command={command}, message={message}")
        # Here you could branch behavior, update internal state, etc.


async def main():
    agent = VisitingAgent(
        agent_id=agent_config.agent_id,
        ws_url=ws_config.url,
    )
    await agent.run_session(num_steps=agent_config.num_steps)


if __name__ == "__main__":
    asyncio.run(main())