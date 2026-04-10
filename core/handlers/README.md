# A2A Handler Architecture
## How Agents Talk to Agents

**Platform:** Yo-ai · Native Python · No Third-Party Framework Dependencies  
**A2A Specification:** [https://a2a-protocol.org/latest/specification/](https://a2a-protocol.org/latest/specification/)  
**Status:** Current Release (MODE1) · Roadmap (MODE2-5)

---

## Overview

The Yo-ai platform is designed around a core principle:
**every agent interaction flows through governed, contextual pipelines that ensure identity, authorization, and auditability**. 

Unlike traditional API platforms where endpoints are isolated and stateless, 
Yo-ai provides **five distinct entry points** that all converge on the same governance infrastructure
— the **Solicitor General (SG)** and the **Unified Capability Registry (UCR)**. 
This architecture ensures that whether an external agent sends a semantic A2A message, 
an authenticated REST client calls a typed API, 
or a platform agent invokes a peer directly, 
the same context-building, routing, and audit flows apply.

Each entry point is declared in an agent's extended card as a **supported interface**, 
allowing callers to choose the integration style that best fits their tooling 
while maintaining platform-wide governance.

```json
"supportedInterfaces": [
  {
    "url": "https://privacyportfolio.com/agent-registry/[agent-name]/a2a",
    "protocolBinding": "JSONRPC_HTTP",
    "protocolVersion": "1.0"
  },
  {
    "url": "https://privacyportfolio.com/agent-registry/[agent-name]/mesh",
    "protocolBinding": "A2A_DIRECT",
    "protocolVersion": "1.0"
  },
  {
    "url": "https://privacyportfolio.com/agent-registry/[agent-name]/api",
    "protocolBinding": "OPENAI_API",
    "protocolVersion": "1.0"
  },
  {
    "url": "https://privacyportfolio.com/agent-registry/[agent-name]/app",
    "protocolBinding": "MCP",
    "protocolVersion": "1.0"
  },
  {
    "url": "https://privacyportfolio.com/agent-registry/[agent-name]/op",
    "protocolBinding": "REST",
    "protocolVersion": "1.0"
  }
]
```

**Key Insight:** Each agent can declare which interfaces it supports, 
and each capability can be configured to support specific entry points through its designated handler. 
This flexibility allows the platform to meet diverse integration needs without sacrificing governance.

---

## The Five Entry Points

| Entry Point | Label          | Protocol Binding | Used By                       | Governed |
|-------------|----------------|------------------|-------------------------------|----------|
| `"a2a"`     | HTTP A2A       | JSONRPC_HTTP     | External public agents, curl  |  ✅ Yes -| 
| `"mesh"`    | Direct A2A     | RPC              | Internal agents, SDK/ADK      |  ✅ Yes  |
| `"api"`     | OpenAI API     | OPENAI_API       | OpenAI-compatible API clients |  ✅ Yes  |
| `"app"`     | MCP/Starlette  | MCP              | MCP/streaming clients         |  ✅ Yes  |
| `"op"`      | REST Operation | REST             | REST-compatible API clients   |  ❌ No   |

**Notes:**
- **Entry Point** corresponds to an OpenAPI path or RPC mechanism
- **Label** is how documentation, diagrams, and developer guides refer to each interface
- **Protocol Binding** is what appears in agent cards and context metadata
- **Used By** indicates which tools are typically used for access
- **Governed** indicates whether the Solicitor General performs semantic routing and governance

---

## Why Context Matters: Governed vs. Ungoverned Invocation

When you invoke an agent capability through
**(A2A)**, **(Mesh)**, **(API)**, or **(MCP/App)**, 
the platform ensures:

✅ **Identity Context** – Who is making the request?  
✅ **Profile Context** – What data, permissions, and subscriber entitlements apply?  
✅ **Capability Context** – What capability is being invoked, under what conditions?  
✅ **Audit Trail** – Every invocation is logged with full context for compliance  
✅ **Semantic Routing** – The Solicitor General interprets intent and routes to the correct capability  
✅ **Authorization Checks** – The platform validates the caller has permission to invoke this capability  

**Example Flow (API):**
```
POST /agent-registry/data-steward/api
Body: { "capability": "dataRequestGovern", "payload": {...} }

  ↓ API Gateway
  ↓ APIHandler extracts caller identity from authorizer
  ↓ Wraps request in JSON-RPC envelope with agent_ctx metadata
  ↓ Routes to Solicitor General
  ↓ SG builds full agent_ctx (profile, permissions, subscriber context)
  ↓ SG routes to DataSteward.dataRequestGovern()
  ↓ Capability executes with full context
  ↓ Returns governed response
```

**Result:** The capability knows **whose data** to govern,
**what permissions** apply, 
and **who requested** the action. 
Audit logs capture the full chain of custody.

---

**(REST)** bypasses all governance and invokes the capability Lambda directly. 

**Ungoverned Invocation:**
- ❌ No identity context – The capability doesn't know who called it
- ❌ No profile context – The capability doesn't know whose data to operate on
- ❌ No authorization checks – Anyone can call the endpoint
- ❌ No audit trail – Invocations are logged but without governance metadata
- ❌ No semantic routing – Direct path to capability, no SG interpretation

**(REST)** can be used for testing and reducing overhead:
- ✅ **Schema validation testing** – "Does my request shape match the OpenAPI spec?"
- ✅ **Wiring verification** – "Is the Lambda deployed and responding?"
- ✅ **Quick debugging** – "Does the bare logic execute without errors?"

**Example Flow (REST):**
```
POST /agent-registry/the-sentinel/op/platformMonitor
Body: { "userId": "user123", "dataType": "profile" }

  ↓ API Gateway
  ↓ Direct invoke: the-sentinel-platformMonitor Lambda
  ↓ Capability executes with NO agent_ctx, NO profile
  ↓ Capability executes every 60 seconds without logging
  ↓ Returns stub error if agent_ctx or profile is required: "What data? Whose data?"
```

**Result:** The capability receives raw parameters 
but has **no context** about the caller, their permissions, 
or which subscriber's data to operate on. 
It will typically return a stub error explaining the limitation.

**When to Use (REST):**
- 🧪 During development to test OpenAPI schema compliance
- 🧪 To verify Lambda deployment and basic execution
- 🧪 To learn what context a capability requires by observing failure modes

**When NOT to Use (REST):**
- ❌ Production workloads 
- ❌ Any operation requiring identity, authorization, or profile context
- ❌ Workflows that need audit trails for compliance

---

## The Five Entry Point Handlers

| Entry Point | Label          | Handler Module                |
|-------------|----------------|-------------------------------|
|  `"a2a"`    | HTTP A2A       | `http/yo_ai_handler.py`       |
|  `"mesh"`   | Direct A2A     | `mesh/platform_message_bus.py`|
|  `"api"`    | OpenAI API     | `http/openapi/api_handler.py` |
|  `"app"`    | MCP/Starlette  | `http/app_mount.py`           |
|  `"op"`     | REST Operation | `(per-capability handler)`    |

---

## Next Steps

- **Getting Started:** See [Quickstart Guide](./docs/quickstart.md)
- **Agent Cards:** Explore [Agent Registry](https://privacyportfolio.com/agent-registry) 
- **A2A Specification:** Read the [official A2A spec](https://a2a-protocol.org/latest/specification/) 
- **Capability Development:** Build new capabilities for your agents in [Developer Guide](https://yo-ai.ai/docs/developer-guide.md)
