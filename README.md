# Yo-ai: AI Assurance Platform for Consumers and Organizations

Yo-ai is an AI Assurance Platform that enables Consumers and Organizations to establish secure, transparent, and mutually governed A2A (Agent to Agent) communication channels.
The Consumer is represented by the Data-Steward, an AI Agent that makes decisions and acts on the Consumer's behalf. 
The Organization is represented by the Vendor-Manager, an AI Agent that acts as a proxy to represent the organization.

Both sides use profiles to represent individual persons and corporate entities. These profiles are loaded, referenced, and updated by a team of cooperating AI Agents that can communicate:
- directly with the real-world parties they represent, or
- through A2A interchanges operating inside isolated internal sandboxes.

Real people use Yo-ai to interact with each others' agents when they are unavailable or unknown to each other.
This drastically reduces latency in all processes, while also providing security, accountability, and privacy.

## What Yo-ai Enables
Yo-ai provides a structured way for individuals and organizations to:

-	Open A2A communication channels
-	Negotiate mutually agreed-upon data processing agreements
-	Train each others' AI Agents to “play well with others”
-	Test for impacts to the corresponding party before, during, or after changes in processing
-	Build trust through transparency, primarily by sharing event logs about their agents’ activities

## Who the Yo-ai Platform Serves
Everyone who wants something, and anyone who cannot be everywhere all at once.

## Problems the Yo-ai Platform Solves
-		Distrust. ”Who comes knocking at my door? What are doing? What do you want? How can I engage with you – or not?”
-		High-latency processes. “My agent can produce this now. When can you get back to me?”

## Benefits the Yo-ai Platform Provides
As an evidence-based learning system for autonomous decision-making, Yo-ai provides 'explainability' through log-shipping for a unified system of truth for all participants in a process.  

# **How This Repository Is Structured**
Yo‑ai is a multi-agent, federated platform of A2A agents that can be cloned and run within any environment. 
A Makefile documents which modules are importable as Python packages.
Every top‑level directory contains a README.md.

### **`/core`**
 Summary: 
 Foundational agent classes and shared abstractions.
 
 Usage:
 Importable Python packages for agent class definitions.
 All platform agents inherit from these classes.

 Contains: 
 - BaseAgent — base class for all agents
 - PlatformAgent — privileged platform‑side agent
 - YoAiAgent — consumer/organization‑side agent

### **`/a2a`**
 Summary:
 Shared A2A runtime and the glue layer between the A2A Protocol and the Solicitor‑General.

 Usage:
 This is the semantic edge of the Yo-ai Platform.
 The Solicitor-General owns unified_capability_router.py, a platform-wide semantic router.


 Contains:
 - a2a_transport.py — A2A JSON-RPC handler that bridges the http /a2a endpoint and Solicitor‑General.


### **`/http`**
 Summary:
 HTTP‑facing routes, API-Direct routes, OpenAPI specification.

 Usage:
 Exposes public HTTP routes for agents and A2A operations.
 
 Contains:
 - /yo_ai_handler.py — HTTP A2A JSON‑RPC endpoint that receives JSON‑RPC requests and forwards them to the Solicitor‑General
 - /openapi/api_handler.py — DIRECT A2A JSON‑RPC endpoint that receives JSON‑RPC requests and forwards them to the Solicitor‑General
 - /openapi/openapi.yaml — Yo‑API capability definitions

### **`/agents`**
 Summary:
 Standalone agent bundles for consumer‑side and organization‑side teams.

 Usage:
 Each folder represents a complete agent package, including identity, capabilities, training materials, and artifacts.

 Contains:
 - agent.json — identity + capabilities
 - Agent card documentation
 - Training manuals
 - Artifacts (schemas, agreements, policies, knowledge)
 - Chat transcripts used to develop each agent

### **`/shared`**
 Summary:
 Shared resources used across all Yo‑ai agents.

 Usage:
 Imported by agents and platform components to ensure consistent schemas, policies, and tools.

 Contains:
 /artifacts
  - Subscriber and Agent Registration cards
  - Workflow DAGs
  - Event schemas
  - Kafka topic schemas
  - Negotiation messages
  - Report and evidence manifests
 /policies
  - Authorization policies
  - IAM models
  - Trust‑zone rules
 /tools
  - Detectors
  - Loaders
  - Ingestion systems
  - Publishing tools

### **`/tests`**
 Summary:
 Executable tests for platform functionality, workflows, and campaigns.

 Usage:
 Run via pytest or the Makefile to validate platform behavior.

 Contains:
 - Agent registry tests
 - Log‑shipping tests
 - Negotiation flow tests
 - Platform startup/shutdown tests

### **`/campaigns`**
 Summary:
 Human‑facing and agent‑facing communication flows for goal‑oriented campaigns.

 Usage:
 Used by agents and platform components to run structured trust‑building or diagnostic campaigns.

 Contains:
 - Red/Yellow/Green trust‑zone landing pages
 - “Am I a Threat?”
 - “Logs Don’t Lie”
 - Registered Agent onboarding

### **`tree-files.txt`**
 Represents resources that often exist locally but should not be committed to public repositories.
 Helps contributors understand the full structure without exposing sensitive or proprietary materials.
