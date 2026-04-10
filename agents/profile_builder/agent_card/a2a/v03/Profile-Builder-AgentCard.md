/**
 * This Profile-Builder AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Profile-Builder AgentCard¶
*/
{
    "name": "Profile-Builder",
    "description": "Builds and maintains organization profiles.",
    "url": "https://privacyportfolio.com/agent-registry/profile-builder/agent.json",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
      },
    "iconUrl": "https://privacyportfolio.com/agent-registry/profile-builder/profile-builder-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/profile-builder/Profile-Builder-AgentCard.md",
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
        "name": "Org-Profile.Build",
        "description": "Build organization profiles based on discovery from IP-Inspector and Tech-Inspector agents.",
        "tags": ["public", "private", "affiliate"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.output.schema.json" }
      }
    ],
    "supportsAuthenticatedExtendedCard": true
}