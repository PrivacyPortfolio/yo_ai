/**
 * The-Advisor AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* The-Advisor AgentCard¶
*/
{
    "name": "The-Advisor",
    "description": "Provides advice on any issue to Yo-ai Registered Agents.",
    "id": "com.privacyportfolio.the-advisor",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-directory/the-advisor/the-advisor-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/the-advisor/The-Advisor-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/the_advisor/a2a",
        "protocolBinding": "JSONRPC-HTTP",
        "protocolVersion": "1.0"
      }
    ],
    "capabilities": {
      "streaming": true,
      "pushNotifications": true,
      "extendedAgentCard": true
    },
    "securitySchemes": {
        "yo-ai": {
            "type": "apiKey",
            "name": "yo-api",
            "in": "header"
        }
    },
    "security": [{ "yo-ai": [] }],
    "defaultInputModes": ["application/json", "text/plain"],
    "defaultOutputModes": ["application/json", "text/plain"],
    "skills": [
        {
            "name": "Cognitive.Reason",
            "description": "",
            "tags": [""],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/cognitive.reason.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/cognitive.reason.output.schema.json" }
        },
        {
            "name": "Knowledge.Resolve",
            "description": "",
            "tags": [""],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/knowledge.resolve.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/knowledge.resolve.output.schema.json" }
        },
        {
            "name": "Friend.Call",
            "description": "",
            "tags": [""],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/friend.call.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/friend.call.output.schema.json" }
        },
        {
            "name": "Outcome.LearnFrom",
            "description": "",
            "tags": [""],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/outcome.learnfrom.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/outcome.learnfrom.output.schema.json" }
        }
    ]
}