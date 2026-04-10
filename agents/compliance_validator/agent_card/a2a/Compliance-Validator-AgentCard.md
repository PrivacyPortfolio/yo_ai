/**
 * This Compliance-Validator AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 * - ExtendedCard contains tasks and messages for Registered Agents
 */

/**
* Compliance-Validator AgentCard¶
*/
{
    "name": "Compliance-Validator",
    "description": "Evaluates facts, evidence, and assessments regarding laws, regulations, mandates, policies, and contracts. Produces factual compliance rationales suitable for audit, challenge, or testimony.",
    "id": "com.privacyportfolio.compliance-validator",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-directory/compliance-validator/compliance-validator-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/compliance-validator/Compliance-Validator-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/compliance_validator/a2a",
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
            "name": "Compliance-Standard.Get",
            "description": "Retrieves a compliance standard, mandate, regulation, law, policy, or contract clause from the agent's knowledge repository.",
            "version": "1.0.0", 
            "examples": [
                "Get GDPR Article 5",
                "Retrieve CCPA 1798.100",
                "Fetch ISO27001 A.5.1"
            ],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.output.schema.json" }
        },
        {
            "name": "Compliance.Validate",
            "description": "Evaluates facts and evidence against one or more compliance standards. Produces a factual compliance rationale suitable for audit or testimony.",
            "version": "1.0.0", 
            "tags": [
                "complianceValidation",
                "legalMapping",
                "evidenceAnalysis",
                "audit",
                "testimony"
            ],
            "examples": [
                "Validate whether ACME's data handling aligns with GDPR Article 5",
                "Check if vendor:123 meets CCPA 1798.100 requirements",
                "Evaluate compliance of risk assessment findings against ISO27001"
            ],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.output.schema.json" }
        }
    ]
}