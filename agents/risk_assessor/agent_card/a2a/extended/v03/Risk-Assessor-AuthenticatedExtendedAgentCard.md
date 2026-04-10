/**
 * This Risk-Assessor AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Risk-Assessor Authenticated Extended Agent Card¶
*/
{
    "name": "Risk-Assessor",
    "description": "Builds, conducts, and maintains risk assessments.",
    "url": "https://privacyportfolio.com/agent-registry/risk-assessor/auth/agent.json",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
      },
    "iconUrl": "https://privacyportfolio.com/agent-registry/risk-assessor/risk-assessor-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/risk-assessor/auth/Risk-Assessor-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Risks.Assess"}
    ],
    "x-capabilities": [
        {
            "Risks.Assess": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Risks.Assess"}},
                    {"artifact": {"type": "task", "name": "Risks.Assess"}},
                    {"artifact": {"type": "tool", "name": "Risks.Assess"}},
                    {"artifact": {"type": "handler", "name": "Risks.Assess"}},
                    {"artifact": {"type": "messageType", "name": "Risks.Assess.Input"}},
                    {"artifact": {"type": "messageType", "name": "Risks.Assess.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
      {
        "name": "Risks.Assess",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Conducts structured, provenance-aware risk assessments using specified standards, evidence sources, and assessment models.",
        "tags": [
          "riskAssessment",
          "fraudDetection",
          "complianceSupport",
          "bulkOperations",
          "orgAnalysis"
        ],
        "examples": [
          "Assess risk of ACME Corp using NIST AI RMF",
          "Evaluate fraud indicators for vendor:123",
          "Perform bulk risk assessment for all cloud providers"
        ]
      },
      {
        "name": "Risks.Assess",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Conducts structured, provenance-aware risk assessments using specified standards, evidence sources, and assessment models.",
        "tags": [
          "riskAssessment",
          "fraudDetection",
          "complianceSupport",
          "bulkOperations",
          "orgAnalysis"
        ],
        "examples": [
          "Assess risk of ACME Corp using NIST AI RMF",
          "Evaluate fraud indicators for vendor:123",
          "Perform bulk risk assessment for all cloud providers"
        ]
      },
      {
        "name": "Risks.Assess",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Conducts structured, provenance-aware risk assessments using specified standards, evidence sources, and assessment models.",
        "capabilities": ["assess"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Risks.Assess.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/risks.assess.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/risks.assess.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Risks.Assess",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Risks.Assess.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/risks.assess.input.schema.json"
        },
        "description": "Input schema for the Risks.Assess capability."
      },
      {
        "name": "Risks.Assess.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/risks.assess.output.schema.json"
        },
        "description": "Output schema for the Risks.Assess capability."
      }
    ],
    "supportsAuthenticatedExtendedCard": true
}