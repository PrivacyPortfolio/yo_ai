/**
 * This Data-Anonymizer AuthenticatedExtendedCard conveys:
 * - Tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */


/**
* Data-Anonymizer Authenticated Extended Agent Card¶
*/
{
    "name": "Data-Anonymizer",
    "description": "Uses a variety of tools and techniques for anonymizing and testing datasets of personal attributes.",
    "url": "https://privacyportfolio.com/agent-registry/data-anonymizer/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/data-anonymizer/data-anonymizer-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/data-anonymizer/auth/Data-Anonymizer-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Identifiability.Assess"},
        {"name": "Deidentification-Techniques.Apply"},
        {"name": "K-Anonymity.Compute"},
        {"name": "Safe-Release.Recommend"},
        {"name": "Deidentification-Report.Generate"},
        {"name": "Auxiliary-Data-Risk.Evaluate"},
        {"name": "Data-For-Purpose.Minimize"},
        {"name": "Reidentification-Attack.Simulate"},
        {"name": "Deidentification-Standard.Map"},
        {"name": "Deidentification-Guidance.Publish"}
    ],
    "x-capabilities": [
        {
            "Identifiability.Assess": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Identifiability.Assess"}},
                    {"artifact": {"type": "task", "name": "Identifiability.Assess"}},
                    {"artifact": {"type": "tool", "name": "Identifiability.Assess"}},
                    {"artifact": {"type": "handler", "name": "Identifiability.Assess"}},
                    {"artifact": {"type": "messageType", "name": "Identifiability.Assess.Input"}},
                    {"artifact": {"type": "messageType", "name": "Identifiability.Assess.Output"}}
                ]
            }
        },
        {
            "Deidentification-Techniques.Apply": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Deidentification-Techniques.Apply"}},
                    {"artifact": {"type": "task", "name": "Deidentification-Techniques.Apply"}},
                    {"artifact": {"type": "tool", "name": "Deidentification-Techniques.Apply"}},
                    {"artifact": {"type": "handler", "name": "Deidentification-Techniques.Apply"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Techniques.Apply.Input"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Techniques.Apply.Output"}}
                ]
            }
        },
        {
            "K-Anonymity.Compute": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "K-Anonymity.Compute"}},
                    {"artifact": {"type": "task", "name": "K-Anonymity.Compute"}},
                    {"artifact": {"type": "tool", "name": "K-Anonymity.Compute"}},
                    {"artifact": {"type": "handler", "name": "K-Anonymity.Compute"}},
                    {"artifact": {"type": "messageType", "name": "K-Anonymity.Compute.Input"}},
                    {"artifact": {"type": "messageType", "name": "K-Anonymity.Compute.Output"}}
                ]
            }
        },
        {
            "Safe-Release.Recommend": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Safe-Release.Recommend"}},
                    {"artifact": {"type": "task", "name": "Safe-Release.Recommend"}},
                    {"artifact": {"type": "tool", "name": "Safe-Release.Recommend"}},
                    {"artifact": {"type": "handler", "name": "Safe-Release.Recommend"}},
                    {"artifact": {"type": "messageType", "name": "Safe-Release.Recommend.Input"}},
                    {"artifact": {"type": "messageType", "name": "Safe-Release.Recommend.Output"}}
                ]
            }
        },
        {
            "Deidentification-Report.Generate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Deidentification-Report.Generate"}},
                    {"artifact": {"type": "task", "name": "Deidentification-Report.Generate"}},
                    {"artifact": {"type": "tool", "name": "Deidentification-Report.Generate"}},
                    {"artifact": {"type": "handler", "name": "Deidentification-Report.Generate"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Report.Generate.Input"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Report.Generate.Output"}},
                    {"artifact": {"type": "Report", "name": "Deidentification-Report"}}
                ]
            }
        },
        {
            "Auxiliary-Data-Risk.Evaluate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Auxiliary-Data-Risk.Evaluate"}},
                    {"artifact": {"type": "task", "name": "Auxiliary-Data-Risk.Evaluate"}},
                    {"artifact": {"type": "tool", "name": "Auxiliary-Data-Risk.Evaluate"}},
                    {"artifact": {"type": "handler", "name": "Auxiliary-Data-Risk.Evaluate"}},
                    {"artifact": {"type": "messageType", "name": "Auxiliary-Data-Risk.Evaluate.Input"}},
                    {"artifact": {"type": "messageType", "name": "Auxiliary-Data-Risk.Evaluate.Output"}}
                ]
            }
        },
        {
            "Data-For-Purpose.Minimize": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Data-For-Purpose.Minimize"}},
                    {"artifact": {"type": "task", "name": "Data-For-Purpose.Minimize"}},
                    {"artifact": {"type": "tool", "name": "Data-For-Purpose.Minimize"}},
                    {"artifact": {"type": "handler", "name": "Data-For-Purpose.Minimize"}},
                    {"artifact": {"type": "messageType", "name": "Data-For-Purpose.Minimize.Input"}},
                    {"artifact": {"type": "messageType", "name": "Data-For-Purpose.Minimize.Output"}}
                ]
            }
        },
        {
            "Reidentification-Attack.Simulate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Reidentification-Attack.Simulate"}},
                    {"artifact": {"type": "task", "name": "Reidentification-Attack.Simulate"}},
                    {"artifact": {"type": "tool", "name": "Reidentification-Attack.Simulate"}},
                    {"artifact": {"type": "handler", "name": "Reidentification-Attack.Simulate"}},
                    {"artifact": {"type": "messageType", "name": "Reidentification-Attack.Simulate.Input"}},
                    {"artifact": {"type": "messageType", "name": "Reidentification-Attack.Simulate.Output"}}
                ]
            }
        },
        {
            "Deidentification-Standard.Map": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Deidentification-Standard.Map"}},
                    {"artifact": {"type": "task", "name": "Deidentification-Standard.Map"}},
                    {"artifact": {"type": "tool", "name": "Deidentification-Standard.Map"}},
                    {"artifact": {"type": "handler", "name": "Deidentification-Standard.Map"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Standard.Map.Input"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Standard.Map.Output"}}
                ]
            }
        },
        {
            "Deidentification-Guidance.Publish": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Deidentification-Guidance.Publish"}},
                    {"artifact": {"type": "task", "name": "Deidentification-Guidance.Publish"}},
                    {"artifact": {"type": "tool", "name": "Deidentification-Guidance.Publish"}},
                    {"artifact": {"type": "handler", "name": "Deidentification-Guidance.Publish"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Guidance.Publish.Input"}},
                    {"artifact": {"type": "messageType", "name": "Deidentification-Guidance.Publish.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
      {
        "name": "Identifiability.Assess",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Evaluates whether a dataset or attribute can reasonably identify the data subject under contextual and linkage risks.",
        "tags": ["riskAssessment", "linkageRisk", "quasiIdentifiers", "contextualRisk", "audit"],
        "examples": [
          "Assess identifiability of ZIP+Birthdate+Gender",
          "Evaluate re-identification risk for this dataset"
        ]
      },
      {
        "name": "Identifiability.Assess",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Evaluates whether a dataset or attribute can reasonably identify the data subject under contextual and linkage risks.",
        "tags": ["riskAssessment", "linkageRisk", "quasiIdentifiers", "contextualRisk", "audit"],
        "examples": [
          "Assess identifiability of ZIP+Birthdate+Gender",
          "Evaluate re-identification risk for this dataset"
        ]
      },
      {
        "name": "Identifiability.Assess",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Evaluates whether a dataset or attribute can reasonably identify the data subject under contextual and linkage risks.",
        "capabilities": ["assess"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Identifiability.Assess.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/identifiability.assess.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/identifiability.assess.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Identifiability.Assess",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Identifiability.Assess.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/identifiability.assess.input.schema.json"
        },
        "description": "Input schema for the Identifiability.Assess capability."
      },
      {
        "name": "Identifiability.Assess.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/identifiability.assess.output.schema.json"
        },
        "description": "Output schema for the Identifiability.Assess capability."
      },
      {
        "name": "Deidentification-Techniques.Apply",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Recommends appropriate transformations such as masking, generalization, suppression, perturbation, bucketing, hashing, or tokenization.",
        "tags": ["transformation", "minimization", "privacyTechniques", "dataSanitization"],
        "examples": [
          "Generalize birthdate to age bucket",
          "Mask phone number for analytics"
        ]
      },
      {
        "name": "Deidentification-Techniques.Apply",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Recommends appropriate transformations such as masking, generalization, suppression, perturbation, bucketing, hashing, or tokenization.",
        "tags": ["transformation", "minimization", "privacyTechniques", "dataSanitization"],
        "examples": [
          "Generalize birthdate to age bucket",
          "Mask phone number for analytics"
        ]
      },
      {
        "name": "Deidentification-Techniques.Apply",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Recommends appropriate transformations such as masking, generalization, suppression, perturbation, bucketing, hashing, or tokenization.",
        "capabilities": ["deidentify"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Deidentification-Techniques.Apply.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Deidentification-Techniques.Apply",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Deidentification-Techniques.Apply.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.input.schema.json"
        },
        "description": "Input schema for the Deidentification-Techniques.Apply capability."
      },
      {
        "name": "Deidentification-Techniques.Apply.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-techniques.apply.output.schema.json"
        },
        "description": "Output schema for the Deidentification-Techniques.Apply capability."
      },
      {
        "name": "K-Anonymity.Compute",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Computes k-anonymity, l-diversity, t-closeness, and related privacy metrics.",
        "tags": ["privacyMetrics", "kAnonymity", "lDiversity", "tCloseness", "riskScoring"],
        "examples": [
          "Compute k-anonymity for this table",
          "Evaluate diversity of sensitive attributes"
        ]
      },
      {
        "name": "K-Anonymity.Compute",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Computes k-anonymity, l-diversity, t-closeness, and related privacy metrics.",
        "tags": ["privacyMetrics", "kAnonymity", "lDiversity", "tCloseness", "riskScoring"],
        "examples": [
          "Compute k-anonymity for this table",
          "Evaluate diversity of sensitive attributes"
        ]
      },
      {
        "name": "K-Anonymity.Compute",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Computes k-anonymity, l-diversity, t-closeness, and related privacy metrics.",
        "capabilities": ["compute"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/K-Anonymity.Compute.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "K-Anonymity.Compute",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "K-Anonymity.Compute.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.input.schema.json"
        },
        "description": "Input schema for the K-Anonymity.Compute capability."
      },
      {
        "name": "K-Anonymity.Compute.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/k-anonymity.compute.output.schema.json"
        },
        "description": "Output schema for the K-Anonymity.Compute capability."
      },
      {
        "name": "Safe-Release.Recommend",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Determines whether a dataset is safe for release under CPRA, NIST, HIPAA, and A2A norms, and provides required mitigations.",
        "tags": ["policy", "releaseGuidance", "compliance", "riskMitigation"],
        "examples": [
          "Can this dataset be shared with Vendor X",
          "What mitigations are required before release"
        ]
      },
      {
        "name": "Safe-Release.Recommend",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Determines whether a dataset is safe for release under CPRA, NIST, HIPAA, and A2A norms, and provides required mitigations.",
        "tags": ["policy", "releaseGuidance", "compliance", "riskMitigation"],
        "examples": [
          "Can this dataset be shared with Vendor X",
          "What mitigations are required before release"
        ]
      },
      {
        "name": "Safe-Release.Recommend",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Determines whether a dataset is safe for release under CPRA, NIST, HIPAA, and A2A norms, and provides required mitigations.",
        "capabilities": ["recommend"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Safe-Release.Recommend.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Safe-Release.Recommend",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Safe-Release.Recommend.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.input.schema.json"
        },
        "description": "Input schema for the Safe-Release.Recommend capability."
      },
      {
        "name": "Safe-Release.Recommend.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/safe-release.recommend.output.schema.json"
        },
        "description": "Output schema for the Safe-Release.Recommend capability."
      },
      {
        "name": "Deidentification-Report.Generate",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Produces a structured, regulator-friendly report summarizing techniques applied, residual risk, and compliance posture.",
        "tags": ["audit", "reporting", "evidence", "documentation"],
        "examples": [
          "Create a de-identification summary for this dataset",
          "Provide evidence for CCPA compliance"
        ]
      },
      {
        "name": "Deidentification-Report.Generate",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Produces a structured, regulator-friendly report summarizing techniques applied, residual risk, and compliance posture.",
        "tags": ["audit", "reporting", "evidence", "documentation"],
        "examples": [
          "Create a de-identification summary for this dataset",
          "Provide evidence for CCPA compliance"
        ]
      },
      {
        "name": "Deidentification-Report.Generate",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Produces a structured, regulator-friendly report summarizing techniques applied, residual risk, and compliance posture.",
        "capabilities": ["generate"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Deidentification-Report.Generate.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Deidentification-Report.Generate",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Deidentification-Report.Generate.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.input.schema.json"
        },
        "description": "Input schema for the Deidentification-Report.Generate capability."
      },
      {
        "name": "Deidentification-Report.Generate.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-report.generate.output.schema.json"
        },
        "description": "Output schema for the Deidentification-Report.Generate capability."
      },
      {
        "name": "Deidentification-Report",
        "version": "1.0.0",
        "artifactType": "Report",
        "description": "Human-readable and machine-readable report summarizing de-identification posture."
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Assesses how external datasets could re-identify the subject through linkage or inference.",
        "tags": ["auxiliaryData", "linkageRisk", "openSourceIntelligence", "riskAssessment"],
        "examples": [
          "Could this be re-identified using voter rolls",
          "Assess risk from data brokers"
        ]
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Assesses how external datasets could re-identify the subject through linkage or inference.",
        "tags": ["auxiliaryData", "linkageRisk", "openSourceIntelligence", "riskAssessment"],
        "examples": [
          "Could this be re-identified using voter rolls",
          "Assess risk from data brokers"
        ]
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Assesses how external datasets could re-identify the subject through linkage or inference.",
        "capabilities": ["evaluate"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Auxiliary-Data-Risk.Evaluate.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.input.schema.json"
        },
        "description": "Input schema for the Auxiliary-Data-Risk.Evaluate capability."
      },
      {
        "name": "Auxiliary-Data-Risk.Evaluate.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/auxiliary-data-risk.evaluate.output.schema.json"
        },
        "description": "Output schema for the Auxiliary-Data-Risk.Evaluate capability."
      },
      {
        "name": "Data-For-Purpose.Minimize",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Determines the minimum necessary personal data required for a stated purpose and flags unnecessary fields.",
        "tags": ["purposeLimitation", "dataMinimization", "leastPrivilege"],
        "examples": [
          "What fields are required for account creation",
          "Remove unnecessary identifiers for analytics"
        ]
      },
      {
        "name": "Data-For-Purpose.Minimize",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Determines the minimum necessary personal data required for a stated purpose and flags unnecessary fields.",
        "tags": ["purposeLimitation", "dataMinimization", "leastPrivilege"],
        "examples": [
          "What fields are required for account creation",
          "Remove unnecessary identifiers for analytics"
        ]
      },
      {
        "name": "Data-For-Purpose.Minimize",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Determines the minimum necessary personal data required for a stated purpose and flags unnecessary fields.",
        "capabilities": ["minimize"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Data-For-Purpose.Minimize.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Data-For-Purpose.Minimize",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Data-For-Purpose.Minimize.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.input.schema.json"
        },
        "description": "Input schema for the Data-For-Purpose.Minimize capability."
      },
      {
        "name": "Data-For-Purpose.Minimize.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/data-for-purpose.minimize.output.schema.json"
        },
        "description": "Output schema for the Data-For-Purpose.Minimize capability."
      },
      {
        "name": "Reidentification-Attack.Simulate",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Simulates attacker behavior to estimate re-identification risk using auxiliary datasets and linkage strategies.",
        "tags": ["attackSimulation", "reidentification", "auxiliaryData", "riskAssessment"],
        "examples": [
          "Simulate re-identification using voter rolls",
          "Estimate attack success probability with data broker feeds"
        ]
      },
      {
        "name": "Reidentification-Attack.Simulate",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Simulates attacker behavior to estimate re-identification risk using auxiliary datasets and linkage strategies.",
        "tags": ["attackSimulation", "reidentification", "auxiliaryData", "riskAssessment"],
        "examples": [
          "Simulate re-identification using voter rolls",
          "Estimate attack success probability with data broker feeds"
        ]
      },
      {
        "name": "Reidentification-Attack.Simulate",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Simulates attacker behavior to estimate re-identification risk using auxiliary datasets and linkage strategies.",
        "capabilities": ["simulate"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Reidentification-Attack.Simulate.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Reidentification-Attack.Simulate",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Reidentification-Attack.Simulate.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.input.schema.json"
        },
        "description": "Input schema for the Reidentification-Attack.Simulate capability."
      },
      {
        "name": "Reidentification-Attack.Simulate.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/reidentification-attack.simulate.output.schema.json"
        },
        "description": "Output schema for the Reidentification-Attack.Simulate capability."
      },

      {
        "name": "Deidentification-Standard.Map",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Maps de-identification posture to regulatory and policy standards such as CPRA, GDPR, HIPAA, and NIST.",
        "tags": ["standards", "compliance", "mapping", "governance"],
        "examples": [
          "Map this dataset to HIPAA Safe Harbor",
          "Check alignment with CPRA de-identification criteria"
        ]
      },
      {
        "name": "Deidentification-Standard.Map",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Maps de-identification posture to regulatory and policy standards such as CPRA, GDPR, HIPAA, and NIST.",
        "tags": ["standards", "compliance", "mapping", "governance"],
        "examples": [
          "Map this dataset to HIPAA Safe Harbor",
          "Check alignment with CPRA de-identification criteria"
        ]
      },
      {
        "name": "Deidentification-Standard.Map",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Maps de-identification posture to regulatory and policy standards such as CPRA, GDPR, HIPAA, and NIST.",
        "capabilities": ["map"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Deidentification-Standard.Map.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Deidentification-Standard.Map",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Deidentification-Standard.Map.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.input.schema.json"
        },
        "description": "Input schema for the Deidentification-Standard.Map capability."
      },
      {
        "name": "Deidentification-Standard.Map.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-standard.map.output.schema.json"
        },
        "description": "Output schema for the Deidentification-Standard.Map capability."
      },
      {
        "name": "Deidentification-Guidance.Publish",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Publishes human-readable and machine-readable guidance for safely de-identifying and releasing datasets.",
        "tags": ["guidance", "documentation", "governance", "compliance"],
        "examples": [
          "Generate de-identification guidance for analytics engineers",
          "Publish guidance for regulators on this dataset"
        ]
      },
      {
        "name": "Deidentification-Guidance.Publish",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Publishes human-readable and machine-readable guidance for safely de-identifying and releasing datasets.",
        "tags": ["guidance", "documentation", "governance", "compliance"],
        "examples": [
          "Generate de-identification guidance for analytics engineers",
          "Publish guidance for regulators on this dataset"
        ]
      },
      {
        "name": "Deidentification-Guidance.Publish",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Publishes human-readable and machine-readable guidance for safely de-identifying and releasing datasets.",
        "capabilities": ["publish"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Deidentification-Guidance.Publish.html",
          "config": { "backend": "" }
        },
        "inputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.input.schema.json"
        },
        "outputSchema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.output.schema.json"
        },
        "auth": "apiKey"
      },
      {
        "name": "Deidentification-Guidance.Publish",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Deidentification-Guidance.Publish.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.input.schema.json"
        },
        "description": "Input schema for the Deidentification-Guidance.Publish capability."
      },
      {
        "name": "Deidentification-Guidance.Publish.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/deidentification-guidance.publish.output.schema.json"
        },
        "description": "Output schema for the Deidentification-Guidance.Publish capability."
      }
    ],
    "supportsAuthenticatedExtendedCard": true
}