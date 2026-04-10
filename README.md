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
This codebase implements a federated, manifest driven agent ecosystem designed for clarity, modularity, and lightweight deployment. The structure is intentionally opinionated to make it easy for developers to clone, understand, extend, and deploy individual components without carrying unnecessary baggage.
This document explains the purpose of each top level subsystem, how they fit together, and how to navigate the platform as a contributor.
________________________________________
The platform is organized around four core principles:
1.	Developer friendly — easy to clone, run, and reason about
2.	Modular — agents, tools, and platform runtime evolve independently
3.	Lightweight deployables — only the code that must run in Lambda is bundled
4.	Explainable — design intent, training materials, and reasoning traces

The repository is structured into clear subsystems:

yo_ai/
│
├── agents/          # Agent implementations (runtime + capabilities)
├── api/             # Public API contracts (OpenAPI)
├── campaigns/       # Executable onboarding + scenario examples
├── core/            # Platform runtime (routing, tasks, observability, messages)
├── explainability/  # Training manuals, reasoning traces, design intent
├── scripts/         # Build, deploy, validate
├── shared/          # Governance artifacts (non-deployable)
├── tests/           # Unit + integration tests
└── tools/           # Independently deployable tool bundlesEach subsystem is described below.
________________________________________
🤖 Agents (agents/)
Agents are the core actors of the Yo ai ecosystem.
Each agent is self contained and includes:
•	agent_card/ — declarative manifests (basic, extended, authenticated)
•	capabilities/ — Python implementations of capability handlers
•	runtime/ — the agent’s main execution logic
•	knowledge/ — articles, expertise, prompts
•	policies/ — authorization and behavioral constraints
•	agreements/ — DPAs, SLAs, or contractual metadata
•	artifacts/ — agent owned templates or resources
Agents do not contain platform level routing, tasks, or observability logic.
________________________________________
🧩 Core Platform Runtime (core/)
This subsystem contains the platform’s shared execution engine.
It is not deployable and is shared across all agents and tools.
core/handlers/ — Protocol Entrypoints
Lambda handlers for HTTP, A2A, RPC, WebSocket, and other protocol surfaces.
They normalize incoming requests into platform envelopes.
core/routing/ — Semantic Routing Layer
The decision making engine that determines:
•	which agent to invoke
•	which capability to execute
•	which tool to call
•	which rules or overrides apply
Includes resolvers, routing rules, and the unified capability map.
core/tasks/ — Task + Workflow Engine
Implements:
•	task state machines
•	workflow orchestration
•	recovery + rehydration
•	long running process management
core/observability/ — Traces, Logs, Kafka Schemas
Contains:
•	Kafka topic schemas
•	OpenTelemetry configs
•	dashboards
•	structured logging formatters
•	event definitions
core/messages/ — Message Templates + Builders
Defines:
•	platform notifications
•	alerts
•	error envelopes
•	event log entries
•	tool request/response messages
Includes template files and Python builders.
core/runtime/ — Envelope + Validation
Implements:
•	envelope schema
•	message types
•	validation logic
•	correlation/task ID handling
________________________________________
🛠 Tools (tools/)
Tools are independently deployable runtime units.
Each tool has:
•	tool.json — manifest describing entrypoint, version, capabilities
•	config/ — runtime configuration
•	templates/ — tool specific templates
•	docs/ — developer documentation
Tools are referenced through the tool registry, not by file paths.
________________________________________
📚 Shared Governance Artifacts (shared/)
This folder contains non deployable platform governance materials:
•	schemas
•	policies
•	registries
•	agreements
•	templates
________________________________________
🌐 API Contracts (api/)
Contains the platform’s public OpenAPI specification and any future API contracts (AsyncAPI, GraphQL, router maps).
This folder defines the external surface of the platform.
________________________________________
🚀 Campaigns (campaigns/)
Executable examples that help developers:
•	onboard quickly
•	run real scenarios
•	test workflows end to end
•	explore agent interactions
Campaigns are intentionally deployable but not part of the platform runtime.
________________________________________
🧠 Explainability (explainability/)
A subsystem containing:
•	training manuals
•	reasoning traces
•	design intent
•	drift detection baselines
•	scenario walkthroughs
•	development history
This is the platform’s knowledge spine.
________________________________________
🔧 Scripts (scripts/)
Contains deterministic, Windows safe build and deployment scripts:
•	Lambda layer builders
•	schema validators
•	bundle generators
•	CI/CD helpers
Scripts are not part of the runtime.
________________________________________
🧪 Tests (tests/)
Unit and integration tests for agents, tools, and platform subsystems.
________________________________________
📦 Deployment Philosophy
The platform is designed for lightweight, modular deployment:
•	Agents deploy only their runtime and capabilities folders
•	Tools are independently deployed 
•	core/, shared/, api/, campaigns/, and explainability/ are never deployed
•	Build scripts enforce strict boundaries
This keeps bundles small, predictable, and cost efficient.

### **`tree-files.txt`**
 Represents resources that often exist locally but should not be committed to public repositories.
 Helps contributors understand the full structure without exposing sensitive or proprietary materials.
