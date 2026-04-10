/**
 * This Solicitor-General AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Solicitor-General AgentCard¶
*/
{
    "name": "Solicitor-General",
    "description": "Agent that log all platform events and correlates requests with responses for routing.",
    "url":   "https://privacyportfolio.com/agent-registry/solicitor-general/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/solicitor-general/solicitor-general-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/solicitor-general/Solicitor-General-AgentCard.md",
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
            "name": "Just-Ask",
            "description": "Provides an introduction to the Yo-ai platform and guidance on how to interact with the Solicitor-General.",
            "tags": ["help", "introspection", "guidance"],
            "examples": ["Help", "What can you do", "Introduce yourself"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/just-ask.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/just-ask.output.schema.json" }
        },
        {
            "name": "Event.Log",
            "description": "Inserts a record into the EventLog.",
            "tags": ["audit"],
            "examples": ["Log event"],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/event.log.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/event.log.output.schema.json" }
        }
  ],
  "supportsAuthenticatedExtendedCard": true
}