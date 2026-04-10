/**
 * This Workflow-Builder AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - AuthenticatedExtendedCard contains tasks and messages for Registered Agents
 */

/**
* Workflow-Builder AgentCard¶
*/
{
    "name": "Workflow-Builder",
    "description": "Agent that builds workflow itineraries connecting agents with endpoints.",
    "url": "https://privacyportfolio.com/agent-registry/workflow-builder/agent.json",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
      },
    "iconUrl": "https://privacyportfolio.com/agent-registry/workflow-builder/workflow-builder-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/workflow-builder/Workflow-Builder-AgentCard.md",
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
    "defaultOutputModes": ["application/json", "image/png"],
    "skills": [
        {
            "name": "Workflow.Build",
            "description": "Builds orchestrated workflows connecting agents with endpoints.",
            "tags": ["-wf", "internal", "external"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/workflow.build.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/workflow.build.output.schema.json" }
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}