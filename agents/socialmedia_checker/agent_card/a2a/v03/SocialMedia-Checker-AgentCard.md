/**
 * This SocialMedia-Checker AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* SocialMedia-Checker AgentCard¶
*/
{
    "name": "SocialMedia-Checker",
    "description": "Evaluates social media activity to verify promotional requirements and detect potential misappropriation of personal data.",
    "url": "https://privacyportfolio.com/agent-registry/socialmedia-checker/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/socialmedia-checker/socialmedia-checker-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/socialmedia-checker/SocialMedia-Checker-AgentCard.md",
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
        "name": "Promotional-Engagement.Verify",
        "description": "Checks whether required social media actions (follow, like, repost, hashtag usage) were completed for promotional eligibility.",
        "tags": ["promotion", "verification", "rewards", "logEvent"],
        "examples": [
            "Verify user followed brand",
            "Check hashtag usage",
            "Confirm engagement for reward eligibility"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/promotional-engagement.verify.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/promotional-engagement.verify.output.schema.json" }
    },
    {
        "name": "Misappropriation.Detect",
        "description": "Searches social media for unauthorized use of personal information, impersonation, or leaked data indicators.",
        "tags": ["misappropriation", "fraud", "identity", "logEvent"],
        "examples": [
            "Search for impersonation accounts",
            "Detect leaked email or phone number",
            "Identify suspicious mentions of PI"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/misappropriation.detect.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/misappropriation.detect.output.schema.json" }
    },
    {
        "name": "Evidence.Collect",
        "description": "Captures structured evidence of misappropriation or promotional compliance for downstream agents.",
        "tags": ["evidence", "compliance", "logEvent"],
        "examples": [
            "Capture screenshot metadata",
            "Record engagement proof",
            "Store impersonation indicators"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/evidence.collect.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/evidence.collect.output.schema.json" }
    }
  ],
  "supportsAuthenticatedExtendedCard": true
}