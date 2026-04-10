/**
 * This Compliance-Validator AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, tools, and artifacts for Registered Agents
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Compliance-Validator Authenticated Extended Agent Card¶
*/
{
    "name": "Compliance-Validator",
    "description": "Evaluates facts, evidence, and assessments regarding laws, regulations, mandates, policies, and contracts. Produces factual compliance rationales suitable for audit, challenge, or testimony.",
    "url":   "https://privacyportfolio.com/agent-registry/compliance-validator/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/compliance-validator/compliance-validator-agent-icon",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/compliance-validator/auth/Compliance-Validator-AuthenticatedExtendedAgentCard.md",
    "capabilities": {
        "streaming": true,
        "pushNotifications": true,
        "stateTransitionHistory": true,
        "exposesTasks": true,
        "exposesMessages": true,
        "exposesArtifacts": true,
        "exposesTools": true
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
        {"name": "Compliance-Standard.Get"},
        {"name": "Compliance.Validate"}
    ],
    "x-capabilities": [
        {
            "Compliance-Standard.Get": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Compliance-Standard.Get"}},
                    {"artifact": {"type": "task", "name": "Compliance-Standard.Get"}},
                    {"artifact": {"type": "tool", "name": "Compliance-Standard.Get"}},
                    {"artifact": {"type": "handler", "name": "Compliance-Standard.Get"}},
                    {"artifact": {"type": "messageType", "name": "Compliance-Standard.Get.Input"}},
                    {"artifact": {"type": "messageType", "name": "Compliance-Standard.Get.Output"}}
                ]
            }
        },
        {
            "Compliance.Validate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Compliance.Validate"}},
                    {"artifact": {"type": "task", "name": "Compliance.Validate"}},
                    {"artifact": {"type": "tool", "name": "Compliance.Validate"}},
                    {"artifact": {"type": "handler", "name": "Compliance.Validate"}},
                    {"artifact": {"type": "messageType", "name": "Compliance.Validate.Input"}},
                    {"artifact": {"type": "messageType", "name": "Compliance.Validate.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
        {
            "name": "Compliance-Standard.Get",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Retrieves a compliance standard, mandate, regulation, law, policy, or contract clause from the agent's knowledge repository.",
            "tags": ["compliance", "standards", "regulations", "knowledge"],
            "examples": [
              "Get GDPR Article 5",
              "Retrieve CCPA 1798.100",
              "Fetch ISO27001 A.5.1"
            ]
        },
        {
            "name": "Compliance-Standard.Get",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Retrieves a compliance standard, mandate, regulation, law, policy, or contract clause from the agent's knowledge repository.",
            "tags": ["compliance", "standards", "regulations", "knowledge"],
            "examples": [
              "Get GDPR Article 5",
              "Retrieve CCPA 1798.100",
              "Fetch ISO27001 A.5.1"
            ]
        },
        {
            "name": "Compliance-Standard.Get",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Retrieves a compliance standard, mandate, regulation, law, policy, or contract clause from the agent's knowledge repository.",
            "capabilities": ["get"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Compliance-Standard.Get",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Compliance-Standard.Get",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Compliance-Standard.Get.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.input.schema.json" },
            "description": "Input schema for Compliance-Standard.Get capability."
        },
        {
            "name": "Compliance-Standard.Get.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/compliance-standard.get.output.schema.json" },
            "description": "Output schema for Compliance-Standard.Get capability."
        },
        {
            "name": "Compliance.Validate",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Evaluates facts and evidence against one or more compliance standards. Produces a factual compliance rationale suitable for audit or testimony.",
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
            ]
        },
        {
            "name": "Compliance.Validate",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Evaluates facts and evidence against one or more compliance standards. Produces a factual compliance rationale suitable for audit or testimony.",
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
            ]
        },
        {
            "name": "Compliance.Validate",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Evaluates facts and evidence against one or more compliance standards. Produces a factual compliance rationale suitable for audit or testimony.",
            "capabilities": ["validate"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Compliance.Validate.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Compliance.Validate",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Compliance.Validate.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.input.schema.json" },
            "description": "Input schema for Compliance.Validate capability."
        },
        {
            "name": "Compliance.Validate.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/compliance.validate.output.schema.json" },
            "description": "Output schema for Compliance.Validate capability."
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}