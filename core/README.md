## /core/README.md

This folder contains the foundational runtime for the entire Yo-ai Platform. It defines:
•	the base Agent class
•	the PlatformAgent and YoAiAgent subclasses
•	the runtime pipeline for validation, transformation, knowledge loading, and output shaping
•	the AI provider orchestration layer
•	the logging subsystem
•	the schema loading and validation engine
•	the envelope and context utilities used across all agents

This folder is the authoritative implementation of the platform’s Core Principle:
Agents never decide whether they are basic or extended.
The platform decides that by choosing which card(s) to load.
This principle ensures:
•	privilege boundaries remain enforceable
•	agents cannot escalate their own capabilities
•	the platform controls authentication, authorization, and card exposure
•	the Solicitor General controls the tool base class and prevents jailbreaks
________________________________________
1. Core Agent Classes
base_agent.py
  Defines the base Agent class shared by all agents.
Implements:
•	card loading
•	capability dispatch
•	message envelope handling

platform_agent.py
  Defines the privileged PlatformAgent subclass.
Platform agents:
•	run inside the platform environment
•	have privileged tools
•	have access to /auth/ resources
•	always receive extended cards

yoai_agent.py
  Defines the YoAiAgent subclass.
Yo ai agents:
•	may receive extended cards only when authenticated

________________________________________
2. Envelope
envelope.py
  Defines the message envelope format used across the platform:
•	metadata
•	capability routing
•	card references
•	provenance

________________________________________
3. Input Processing
•	input_validator.py — validates incoming messages against schemas
•	schema_loader.py — loads JSON schemas
•	schema_validator.py — validates inputs/outputs

Knowledge & Fingerprints
•	load_knowledge.py — loads agent knowledge bundles
•	knowledge_write.py — writes knowledge artifacts
•	load_fingerprints.py — loads agent fingerprints

AI Transformation (/utils/ai/)
•	ai_transform.py — orchestrates LLM calls and applies transformations
•	output_shaper.py — shapes model output into schema compliant responses

Logging (observability/logging/)
•	log_sink.py — base sink
•	json_file_sink.py
•	s3_sink.py
•	kafka_sink.py
•	dynamodb_sink.py
•	windows_event_sink.py
•	sink_loader.py
These provide a pluggable logging architecture.
________________________________________
4. AI Provider Layer (/utils/ai/ai_providers)
  Implements the abstraction layer for all AI providers:
•	base_ai_client.py — shared interface
•	azure_openai_client.py
•	openai_client.py
•	claude_client.py
•	provider_loader.py
•	provider_orchestrator.py

This allows the platform to:
•	switch providers
•	load provider configs
•	orchestrate multi provider strategies
________________________________________
5. Core Principle Summary
•	Platform runtime decides which cards to load
•	Agent class simply loads whatever it is given
•	Platform agents always receive extended cards
•	Yo ai agents receive extended cards only when authenticated
•	Visiting agents never receive extended cards

This ensures:
•	privilege boundaries
•	safety
•	auditability
•	consistent behavior across all agents
________________________________________
6. Agent Categories (for reference)

Platform Agents (privileged, environment bound)
•	decision-master
•	door-keeper
•	incident-responder
•	solicitor-general
•	the-advisor
•	the-custodian
•	the-oracle
•	the-sentinel
•	workflow-builder

Yo ai Agents (unprivileged, runtime bound)
•	complaint-manager
•	compliance-validator
•	darkweb-checker
•	data-anonymizer
•	databroker-monitor
•	data-steward
•	ip-inspector
•	profile-builder
•	purchasing-agent
•	rewards-seeker
•	risk-assessor
•	socialmedia-checker
•	talent-agent
•	tech-inspector
•	vendor-manager

Visiting Agents
•	external
•	untrusted
•	public card only
________________________________________
