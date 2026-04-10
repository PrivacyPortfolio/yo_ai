/**
 * This Talent-Agent AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Talent-Agent AgentCard¶
*/
{
    "name": "Talent-Agent",
    "description": "Agent responsible for responding to job postings, pitching consulting services, and managing professional opportunities.",
    "id": "com.privacyportfolio.talent-agent",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-directory/talent-agent/talent-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/talent-agent/Talent-Agent-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/talent_agent/a2a",
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
        "name": "Job-Postings.Scan",
        "description": "Identify job opportunities that match the subject’s skills and preferences.",
        "version": "1.0.0", 
        "tags": ["jobs", "opportunity", "matching", "logEvent"],
        "examples": [
            "Scan LinkedIn postings",
            "Identify remote roles",
            "Match consulting opportunities"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/job-postings.scan.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/job-postings.scan.output.schema.json" }
    },
    {
        "name": "Consulting-Services.Pitch",
        "description": "Generate and send consulting pitches to prospective clients.",
        "version": "1.0.0", 
        "tags": ["consulting", "pitch", "outreach", "logEvent"],
        "examples": [
            "Send consulting proposal",
            "Pitch services to vendor",
            "Respond to RFP"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.output.schema.json" }
    },
    {
        "name": "Application.Submit",
        "description": "Submit job applications using minimized profile from Data-Steward.",
        "version": "1.0.0", 
        "tags": ["application", "submit", "logEvent"],
        "examples": [
            "Apply to job",
            "Submit resume",
            "Send cover letter"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/application.submit.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/application.submit.output.schema.json" }
    },
    {
        "name": "Talent-Profile.Request",
        "description": "Request minimized resume, skills, and professional profile from Data-Steward.",
        "version": "1.0.0", 
        "tags": ["requestData", "resume", "skills", "logEvent"],
        "examples": [
            "Request resume bundle",
            "Request skills profile"
        ],
        "inputModes": ["application/json"],
        "outputModes": ["application/json"],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/talent-profile.request.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/talent-profile.request.output.schema.json" }
    }
  ]
}