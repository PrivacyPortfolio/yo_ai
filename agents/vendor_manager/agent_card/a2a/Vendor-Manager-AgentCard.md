/**
 * This Vendor-Manager AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Vendor-Manager AgentCard¶
*/
{
    "name": "Vendor-Manager",
    "description": "Agent responsible for monitoring vendors to maintain Responsible AI certification status.",
    "id": "com.privacyportfolio.vendor-manager",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
      },
    "iconUrl": "https://privacyportfolio.com/agent-directory/vendor-manager/vendor-manager-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/directory/vendor-manager/Vendor-Manager-AgentCard.md",
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
        "name": "OrgProfile.Manage",
        "description": "Manage an organization profile as a resource (not as an agent).",
        "version": "1.0.0", 
        "tags": ["verifyOrg", "shareData", "createTask", "buildWorkflow", "logEvent"],
        "examples": [
            "Identify the incorporated entity",
            "Get terms and conditions",
            "Send request"
        ],
        "inputModes": ["application/json", "text/plain"],
        "outputModes": ["application/json", "text/plain"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.manage.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.manage.output.schema.json" }
    }
  ]
}