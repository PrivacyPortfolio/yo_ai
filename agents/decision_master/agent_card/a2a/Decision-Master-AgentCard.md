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
    "id": "com.privacyportfolio.decision-master",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-directory/decision-master/decision-master-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/decision-master/Decision-Master-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/vendor_manager/a2a",
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
    "security": [
      { "yo-ai": [] }
    ],
    "defaultInputModes": ["application/json", "text/plain"],
    "defaultOutputModes": ["application/json", "text/plain"],
    "skills": [
        {
            "name": "Decision-Diary.Manage",
            "description": "Add, remove, correlate, and prune events associated with decision sets.",
            "version": "1.0.0", 
            "tags": ["decision-event", "decision-factor", "decision-outcome"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-diary.manage.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-diary.manage.output.schema.json" }
        },
        {
            "name": "Decision-Events.Identify",
            "description": "Identifies likely decision-making events.",
            "version": "1.0.0", 
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-events.identify.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-events.identify.output.schema.json" }
        },
        {
            "name": "Decision-Outcome.Identify",
            "description": "Identifies the outcome of each decision-set.",
            "version": "1.0.0", 
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.identify.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.identify.output.schema.json" }
        },
        {
            "name": "Decision-Outcome.Analyze",
            "description": "Analyzes explanation of decision-set outcome based on decision factors, evidence, and applicable mandates.",
            "version": "1.0.0", 
            "tags": ["approval", "denial", "no-decision"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.analyze.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/decision-outcome.analyze.output.schema.json" }
        }
    ]
}