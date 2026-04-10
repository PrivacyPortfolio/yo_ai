# agent_api_example.py
# Approach_3 Scenario — Direct Agent API
# Bypasses the A2A transport layer entirely; calls the agent’s capability handler directly
# as a tool, worker, or function from within another provider's AI agent platform 


from agents.data_steward import DataSteward
from core.envelope import InputEnvelope

ds = DataSteward()

input_env = InputEnvelope(
    payload={"to": "+15551234567", "purpose": "Verification"},
    caller="anthropic.clerk",
    profile_name="user_42",
    operation_id="Phone.Call@v1"
)

result = await ds.capabilities["Phone.Call@v1"].execute(input_env)