/**
 * This Complaint-Manager AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Complaint-Manager AgentCard¶
*/
{
    "name": "Complaint-Manager",
    "description": "Manages discovery, generation, submission, stakeholder notification, and publication of complaints to regulators, organizations, and named stakeholders.",
    "url": "https://privacyportfolio.com/agent-registry/complaint-manager/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/complaint-manager/complaint-manager-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/complaint-manager/Complaint-Manager-AgentCard.md",
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
            "name": "Liability.Discover",
            "description": "Identifies potential liability, obligations, or violations based on facts, evidence, and applicable mandates.",
            "tags": ["liability", "compliance", "complaints"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/liability.discover.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/liability.discover.output.schema.json" }
        },
        {
            "name": "EnforcementAgency.Get",
            "description": "Determines the appropriate enforcement agency based on the mandate, jurisdiction, and organization.",
            "tags": ["regulators", "routing"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.output.schema.json" }
        },
        {
            "name": "Stakeholders.Get",
            "description": "Retrieves stakeholders who must be notified or included in the complaint lifecycle.",
            "tags": ["stakeholders"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholders.get.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholders.get.output.schema.json" }
        },
        {
            "name": "Complaint.Generate",
            "description": "Generates a structured complaint document based on findings, facts, and applicable mandates.",
            "tags": ["complaints", "documents"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.generate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.generate.output.schema.json" }
        },
        {
            "name": "Complaint.Submit",
            "description": "Submits a complaint to the appropriate enforcement agency or organization.",
            "tags": ["submission", "regulators"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.submit.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.submit.output.schema.json" }
        },
        {
            "name": "Complaint.Publish",
            "description": "Publishes a complaint to designated stakeholders or public registries.",
            "tags": ["publication"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.publish.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.publish.output.schema.json" }
        },
        {
            "name": "Stakeholder.Notify",
            "description": "Sends a notification to a stakeholder regarding a complaint or enforcement action.",
            "tags": ["notifications"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.output.schema.json" }
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}