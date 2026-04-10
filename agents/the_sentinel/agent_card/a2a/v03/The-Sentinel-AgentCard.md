/**
 * The-Sentinel AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* The-Sentinel AgentCard¶
*/
{
    "name": "The-Sentinel",
    "description": "Listens for dangerous incidents and trends, and issues alerts.",
    "url":   "https://privacyportfolio.com/agent-registry/the-sentinel/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/the-sentinel/the-sentinel-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/The-Sentinel-AgentCard.md",
    "capabilities": {
        "streaming": true,
        "pushNotifications": true,
        "stateTransitionHistory": true
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
            "name": "Platform.Monitor",
            "description": "Monitor platform for adverse events.",
            "tags": ["adverseEvent", "Listening"],
            "examples": [
                "Listening",
                "Get adverseEvent"
            ],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/platform.monitor.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/platform.monitor.output.schema.json" }
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}