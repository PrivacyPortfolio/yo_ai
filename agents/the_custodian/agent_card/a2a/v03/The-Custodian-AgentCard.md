/**
 * The-Custodian AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements (internal ONLY)
 */

/**
* The-Custodian AgentCard¶
*/
{
    "name": "The-Custodian",
    "description": "A privileged PlatformAgent responsible for platform maintenance, storage pruning, trace pruning, DLQ management, and emitting configuration_change and housekeeping events. No profiles, no REST endpoints.",
    "url":   "https://privacyportfolio.com/agent-registry/the-custodian/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/the-custodian/the-custodian-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/the-custodian/The-Custodian-AgentCard.md",
    "capabilities": {
        "streaming": true,
        "pushNotifications": true,
        "stateTransitionHistory": false
    },
    "securitySchemes": {
        "yo-ai": {
        "type": "apiKey",
        "name": "yo-api",
        "in": "header"
        }
    },
    "security": [{ "yo-ai": ["apiKey", "yo-api", "header"] }],
    "defaultInputModes": ["application/json", "text/plain"],
    "defaultOutputModes": ["application/json", "text/plain"],
    "skills": [
        {
            "name": "prune_storage",
            "description": "Prune storage older than retention_days and emit housekeeping event.",
            "tags": ["system", "privileged", "maintenance"],
            "examples": ["Prune storage older than retention_days and emit housekeeping event."],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/prune_storage.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/prune_storage.output.schema.json" }
        },
        {
            "name": "prune_traces",
            "description": "Prune traces older than retention_days and emit housekeeping event.",
            "tags": ["trace"],
            "examples": ["Prune traces older than retention_days"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/prune_traces.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/prune_traces.output.schema.json" }
        },
        {
            "name": "dlq_inspect",
            "description": "Inspect the dead-letter-queue without consuming messages.",
            "tags": ["dlq"],
            "examples": ["Inspect the dead-letter-queue"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dlq_inspect.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dlq_inspect.output.schema.json" }
        },
        {
            "name": "dlq_reprocess",
            "description": "Attempt to reprocess dead-letter-queue messages.",
            "tags": ["dlq"],
            "examples": ["Reprocess dead-letter-queue messages"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dlq_reprocess.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dlq_reprocess.output.schema.json" }
        },
        {
            "name": "generate_config_change_event",
            "description": "Emit a configuration_change event owned by The-Custodian.",
            "tags": ["config_change"],
            "examples": ["config_change"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/generate_config_change_event.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/generate_config_change_event.output.schema.json" }
        }
  ],
  "supportsAuthenticatedExtendedCard": false
}