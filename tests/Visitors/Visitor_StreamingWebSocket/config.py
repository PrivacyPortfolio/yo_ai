from dataclasses import dataclass

@dataclass
class WebSocketConfig:
    url: str = "ws://localhost:8000/ws"
    timeout_seconds: int = 10
    reconnect: bool = False

@dataclass
class AgentConfig:
    agent_id: str = "VisitingAgent-Pedantic"
    num_steps: int = 3

ws_config = WebSocketConfig()
agent_config = AgentConfig()