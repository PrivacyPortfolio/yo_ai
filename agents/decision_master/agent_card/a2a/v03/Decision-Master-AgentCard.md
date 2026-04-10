/**
 * This Decision-Master AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Decision-Master AgentCard¶
*/
{
    "name": "Decision-Master",
    "description": "The Decision-Master agent identifies and analyzes decision-making events in event logs and publishes them to the Decision-Diary topic.",
    "url": "https://privacyportfolio.com/agent-registry/decision-master/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/decision-master/decision-master-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/decision-master/Decision-Master-AgentCard.md",
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
            "name": "Decision-Diary.Manage",
            "description": "Add, remove, correlate, and prune events associated with decision sets.",
            "tags": ["decision-event", "decision-factor", "decision-outcome"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-diary.manage.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-diary.manage.output.schema.json" }
        },
        {
            "name": "Decision-Events.Identify",
            "description": "Identifies likely decision-making events.",
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-events.identify.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-events.identify.output.schema.json" }
        },
        {
            "name": "Decision-Outcome.Identify",
            "description": "Identifies the outcome of each decision-set.",
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.identify.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.identify.output.schema.json" }
        },
        {
            "name": "Decision-Outcome.Analyze",
            "description": "Analyzes explanation of decision-set outcome based on decision factors, evidence, and applicable mandates.",
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.analyze.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.analyze.output.schema.json" }
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}