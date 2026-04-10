/**
 * This Data-Anonymizer AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* Data-Anonymizer AgentCard¶
*/
{
    "name": "Data-Anonymizer",
    "description": "Uses a variety of tools and techniques for anonymizing and testing datasets of personal attributes.",
    "id": "com.privacyportfolio.data-anonymizer",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-directory/data-anonymizer/data-anonymizer-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/data-anonymizer/Data-Anonymizer-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/data_anonymizer/a2a",
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
            "name": "Identifiability.Assess",
            "description": "Evaluates whether a dataset or attribute can reasonably identify the data subject under contextual and linkage risks.",
            "version": "1.0.0", 
            "tags": ["riskAssessment", "linkageRisk", "quasiIdentifiers", "contextualRisk", "audit"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Assess identifiability of ZIP+Birthdate+Gender",
                "Evaluate re-identification risk for this dataset"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/identifiability.assess.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/identifiability.assess.output.schema.json" }
        },
        {
            "name": "Deidentification-Techniques.Apply",
            "description": "Recommends appropriate transformations such as masking, generalization, suppression, perturbation, bucketing, hashing, or tokenization.",
            "version": "1.0.0", 
            "tags": ["transformation", "minimization", "privacyTechniques", "dataSanitization"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Generalize birthdate to age bucket",
                "Mask phone number for analytics"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.output.schema.json" }
        },
        {
            "name": "K-Anonymity.Compute",
            "description": "Computes k-anonymity, l-diversity, t-closeness, and related privacy metrics.",
            "version": "1.0.0", 
            "tags": ["privacyMetrics", "kAnonymity", "lDiversity", "tCloseness", "riskScoring"],
            "input_modes": ["application/json"],
            "output_modes": ["application/json"],
            "examples": [
                "Compute k-anonymity for this table",
                "Evaluate diversity of sensitive attributes"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.output.schema.json" }
        },
        {
            "name": "Safe-Release.Recommend",
            "description": "Determines whether a dataset is safe for release under CPRA, NIST, HIPAA, and A2A norms, and provides required mitigations.",
            "version": "1.0.0", 
            "tags": ["policy", "releaseGuidance", "compliance", "riskMitigation"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Can this dataset be shared with Vendor X",
                "What mitigations are required before release"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.output.schema.json" }
        },
        {
            "name": "Deidentification-Report.Generate",
            "description": "Produces a structured, regulator-friendly report summarizing techniques applied, residual risk, and compliance posture.",
            "version": "1.0.0", 
            "tags": ["audit", "reporting", "evidence", "documentation"],
            "input_modes": ["application/json"],
            "output_modes": ["application/json", "text/plain"],
            "examples": [
                "Create a de-identification summary for this dataset",
                "Provide evidence for CCPA compliance"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.output.schema.json" }
        },
        {
            "name": "Auxiliary-Data-Risk.Evaluate",
            "description": "Assesses how external datasets could re-identify the subject through linkage or inference.",
            "version": "1.0.0", 
            "tags": ["auxiliaryData", "linkageRisk", "openSourceIntelligence", "riskAssessment"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Could this be re-identified using voter rolls",
                "Assess risk from data brokers"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.output.schema.json" }
        },
        {
            "name": "Data-For-Purpose.Minimize",
            "description": "Determines the minimum necessary personal data required for a stated purpose and flags unnecessary fields.",
            "version": "1.0.0", 
            "tags": ["purposeLimitation", "dataMinimization", "leastPrivilege"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "What fields are required for account creation",
                "Remove unnecessary identifiers for analytics"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.output.schema.json" }
        },
        {
            "name": "Reidentification-Attack.Simulate",
            "description": "Runs a simulated adversarial linkage attempt to estimate re-identification probability.",
            "version": "1.0.0", 
            "tags": ["simulation", "adversarial", "riskAssessment", "attackModeling"],
            "input_modes": ["application/json"],
            "output_modes": ["application/json"],
            "examples": [
                "Simulate linkage attack using ZIP+Age+Gender",
                "Estimate re-identification probability"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.output.schema.json" }
        },
        {
            "name": "Deidentification-Standard.Map",
            "description": "Maps the organization's proposed de-identification approach to NIST, CCPA, HIPAA Safe Harbor, and A2A requirements.",
            "version": "1.0.0", 
            "tags": ["standards", "mapping", "compliance", "policy"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Does this meet CCPA de-identification criteria",
                "Map this technique to NIST 800-188"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.output.schema.json" }
        },
        {
            "name": "Deidentification-Guidance.Publish",
            "description": "Generates human-readable instructions explaining how to properly de-identify the user's data for a given purpose.",
            "version": "1.0.0", 
            "tags": ["education", "guidance", "bestPractices", "documentation"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["text/plain"],
            "examples": [
                "Explain how to de-identify my address for analytics",
                "Provide safe handling instructions for my profile data"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.output.schema.json" }
        }
    ]
}