# agent_http_example.py
# Approach_1: HTTP via public A2A entrypoint

# In this example, external callers interact with Yo-ai agents exclusively through the public HTTP surface:
POST /a2a/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "task_id": "req_456",
  "method": "a2a/request",
  "params": {
    "agent_name": "data-steward",
    "operation_id": "Phone.Call@v1",
    "input": {
      "payload": {
        "to": "+15551234567",
        "purpose": "Verification"
      }
    }
  }
}
# If operation_id is omitted, the platform will infer it dynamically 
# using governing labels, correlation lineage, and task metadata.



# For the final response to the caller, the HTTP Router serializes the JSON RPC envelope and returns it.
# Success example:
{
  "jsonrpc": "2.0",
  "id": "req_123",
  "result": {
    "agent_name": "data-steward",
    "operation_id": "Phone.Call@v1",
    "output": {
      "result": {
        "callId": "call_789",
        "status": "completed"
      }
    },
    "timestamp": "2026-03-07T14:30:00Z"
  }
}
# Validation error example (still HTTP 200):
{
  "jsonrpc": "2.0",
  "id": "req_123",
  "result": {
    "output": {
      "error": {
        "code": "AI_OUTPUT_VALIDATION_FAILED",
        "message": "Missing required field: result.callId"
      }
    }
  }
}
# Yo-ai only expects a caller to know which agent they want to talk to (agent_name),
# based on discovery of capabilities through the agent's card.
# Although the agent card, api, and schemas are publicly discoverable, 
# the caller does not need to understand the internal structure of the agent's code or capabilities.