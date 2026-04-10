/**
 * This Data-Steward AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Data-Steward AgentCard¶
*/
{
    "name": "Data-Steward",
    "description": "Governs access to the personal data vault, evaluates intended use of personal data, and makes decisions and takes action on behalf of an individual person.",
    "url": "https://privacyportfolio.com/agent-registry/data-steward/agent.json",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/data-steward/data-steward-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/data-steward/Data-Steward-AgentCard.md",
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
          "name": "Phone.Call",
          "description": "Make outbound phone calls for verification, negotiation, or rights requests.",
          "tags": ["pushNotification", "request", "verify", "question", "survey", "logEvent"],
          "examples": [
            "YourRequestStatus",
            "Please do this",
            "Buy this",
            "Do you have?",
            "Answer these questions"
          ],
          "inputModes": ["application/json", "text/plain"],
          "outputModes": ["application/json", "text/plain"],
          "inputSchema": { "$ref": "#/schemas/Phone.Call.Input" },
          "outputSchema": { "$ref": "#/schemas/Phone.Call.Output" }
      },
      {
          "name": "Phone.Answer",
          "description": "Handle inbound phone calls, verify caller identity, and determine purpose of call.",
          "tags": ["verifyCaller", "shareData", "createTask", "buildWorkflow", "logEvent"],
          "examples": [
            "Identify the caller",
            "Introduce yourself",
            "Determine purpose of call"
          ],
          "inputModes": ["application/json", "text/plain"],
          "outputModes": ["application/json", "text/plain"],
          "inputSchema": { "$ref": "#/schemas/Phone.Answer.Input" },
          "outputSchema": { "$ref": "#/schemas/Phone.Answer.Output" }
      },
      {
          "name": "Data-Request.Govern",
          "description": "Evaluate intended use of personal data before granting access to the personal data vault.",
          "tags": ["verify", "authorize", "policyCheck", "riskAssessment", "logEvent"],
          "examples": [
            "Request to fill out a signup form",
            "Request to provide shipping address",
            "Request to verify identity"
          ],
          "inputModes": ["application/json", "text/plain"],
          "outputModes": ["application/json", "text/plain"],
          "inputSchema": { "$ref": "#/schemas/Data-Request.Govern.Input" },
          "outputSchema": { "$ref": "#/schemas/Data-Request.Govern.Output" }
      },
      {
          "name": "Email.Send",
          "description": "Send outbound email as the authorized agent of the data subject.",
          "tags": ["pushNotification", "request", "verify", "solicitation", "logEvent"],
          "examples": [
            "YourRequestStatus",
            "Please do this",
            "Buy this",
            "Do you have?",
            "Answer these questions"
          ],
          "inputModes": ["application/json", "text/plain"],
          "outputModes": ["application/json", "text/plain"],
          "inputSchema": { "$ref": "#/schemas/Email.Send.Input" },
          "outputSchema": { "$ref": "#/schemas/Email.Send.Output" }
      },
      {
          "name": "Email.Read",
          "description": "Read inbound email, detect spam/phishing, and extract workflow triggers.",
          "tags": ["spam", "phishing", "solicitation", "verify", "survey", "logEvent"],
          "examples": [
            "Your Request Status",
            "Please do this",
            "Buy this",
            "Do you have?",
            "I am..."
          ],
          "inputModes": ["application/json", "text/plain"],
          "outputModes": ["application/json", "text/plain"],
          "inputSchema": { "$ref": "#/schemas/Email.Read.Input" },
          "outputSchema": { "$ref": "#/schemas/Email.Read.Output" }
      }
    ],
    "supportsAuthenticatedExtendedCard": true
}