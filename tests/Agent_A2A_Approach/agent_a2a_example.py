# agent_a2a_example.py
# Approach_2 Scenario — A2A Transport Layer
# Yo-ai agents communicate with each other by calling the A2A transport layer directly

# In this example, the calling agent (hosted in another provider's environment)
# constructs the A2A JSON RPC envelope in process,
# and hands it directly to the transport layer.

envelope = {
    "jsonrpc": "2.0",
    "correlation_id": context.correlation_id,
    "task_id": context.task_id,
    "method": "a2a/request",
    "params": {
        "agent_name": "solicitor-general",
        "operation_id": "Policy.Check@v1",
        "input": {
            "payload": context.profile
        }
    }
}
result = await self.transport.handle_request(envelope)
# Correlation tracking and Task management is preserved



# For the response, the transport layer wraps the result in a JSON RPC envelope,
# and the calling agent receives a JSON RPC shaped dict:
{
  "jsonrpc": "2.0",
  "correlation_id": "req_456",
  "task_id": "req_456",
  "result": {
    "agent_name": "solicitor-general",
    "operation_id": "Policy.Check@v1",
    "output": {
      "result": {
        "allowed": true,
        "reason": "Profile verified"
      }
    }
  }
}
# The calling agent can now continue its workflow.
# In this example the (optional) correlation_id and task_id are set to the same value (any string)
# HTTP status codes do not apply but the transport layer can still return structured error responses.
