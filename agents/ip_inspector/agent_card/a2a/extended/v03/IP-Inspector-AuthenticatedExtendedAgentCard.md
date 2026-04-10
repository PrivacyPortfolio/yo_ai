/**
 * This IP-Inspector AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* IP-Inspector Authenticated Extended Agent Card¶
*/
{
    "name": "IP-Inspector",
    "description": "Discovers intellectual property and potential use cases, and searches for implementation instances.",
    "url": "https://privacyportfolio.com/agent-registry/ip-inspector/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/ip-inspector/ip-inspector-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/ip-inspector/auth/IP-Inspector-AuthenticatedExtendedAgentCard.md",
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
        {"name": "IP-Assets.Discover"},
        {"name": "IP-to-Products.Map"},
        {"name": "Implementation-Instances.Search"},
        {"name": "Use-Cases.Infer"},
        {"name": "IP-Portfolio.Cluster"},
        {"name": "IP-Report.Generate"},
        {"name": "IP-Risk.Evaluate"},
        {"name": "IP-Provenance.Trace"},
        {"name": "Related-IP.Discover"}
    ],
    "x-capabilities": [
        {
            "IP-Assets.Discover": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-Assets.Discover"}},
                    {"artifact": {"type": "task", "name": "IP-Assets.Discover"}},
                    {"artifact": {"type": "tool", "name": "IP-Assets.Discover"}},
                    {"artifact": {"type": "handler", "name": "IP-Assets.Discover"}},
                    {"artifact": {"type": "messageType", "name": "IP-Assets.Discover.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-Assets.Discover.Output"}}
                ]
            }
        },
        {
            "IP-to-Products.Map": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-to-Products.Map"}},
                    {"artifact": {"type": "task", "name": "IP-to-Products.Map"}},
                    {"artifact": {"type": "tool", "name": "IP-to-Products.Map"}},
                    {"artifact": {"type": "handler", "name": "IP-to-Products.Map"}},
                    {"artifact": {"type": "messageType", "name": "IP-to-Products.Map.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-to-Products.Map.Output"}}
                ]
            }
        },
        {
            "Implementation-Instances.Search": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Implementation-Instances.Search"}},
                    {"artifact": {"type": "task", "name": "Implementation-Instances.Search"}},
                    {"artifact": {"type": "tool", "name": "Implementation-Instances.Search"}},
                    {"artifact": {"type": "handler", "name": "Implementation-Instances.Search"}},
                    {"artifact": {"type": "messageType", "name": "Implementation-Instances.Search.Input"}},
                    {"artifact": {"type": "messageType", "name": "Implementation-Instances.Search.Output"}}
                ]
            }
        },
        {
            "Use-Cases.Infer": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Use-Cases.Infer"}},
                    {"artifact": {"type": "task", "name": "Use-Cases.Infer"}},
                    {"artifact": {"type": "tool", "name": "Use-Cases.Infer"}},
                    {"artifact": {"type": "handler", "name": "Use-Cases.Infer"}},
                    {"artifact": {"type": "messageType", "name": "Use-Cases.Infer.Input"}},
                    {"artifact": {"type": "messageType", "name": "Use-Cases.Infer.Output"}}
                ]
            }
        },
        {
            "IP-Portfolio.Cluster": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-Portfolio.Cluster"}},
                    {"artifact": {"type": "task", "name": "IP-Portfolio.Cluster"}},
                    {"artifact": {"type": "tool", "name": "IP-Portfolio.Cluster"}},
                    {"artifact": {"type": "handler", "name": "IP-Portfolio.Cluster"}},
                    {"artifact": {"type": "messageType", "name": "IP-Portfolio.Cluster.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-Portfolio.Cluster.Output"}}
                ]
            }
        },
        {
            "IP-Report.Generate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-Report.Generate"}},
                    {"artifact": {"type": "task", "name": "IP-Report.Generate"}},
                    {"artifact": {"type": "tool", "name": "IP-Report.Generate"}},
                    {"artifact": {"type": "handler", "name": "IP-Report.Generate"}},
                    {"artifact": {"type": "messageType", "name": "IP-Report.Generate.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-Report.Generate.Output"}}
                ]
            }
        },
        {
            "IP-Risk.Evaluate": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-Risk.Evaluate"}},
                    {"artifact": {"type": "task", "name": "IP-Risk.Evaluate"}},
                    {"artifact": {"type": "tool", "name": "IP-Risk.Evaluate"}},
                    {"artifact": {"type": "handler", "name": "IP-Risk.Evaluate"}},
                    {"artifact": {"type": "messageType", "name": "IP-Risk.Evaluate.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-Risk.Evaluate.Output"}}
                ]
            }
        },
        {
            "IP-Provenance.Trace": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "IP-Provenance.Trace"}},
                    {"artifact": {"type": "task", "name": "IP-Provenance.Trace"}},
                    {"artifact": {"type": "tool", "name": "IP-Provenance.Trace"}},
                    {"artifact": {"type": "handler", "name": "IP-Provenance.Trace"}},
                    {"artifact": {"type": "messageType", "name": "IP-Provenance.Trace.Input"}},
                    {"artifact": {"type": "messageType", "name": "IP-Provenance.Trace.Output"}}
                ]
            }
        },
        {
            "Related-IP.Discover": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Related-IP.Discover"}},
                    {"artifact": {"type": "task", "name": "Related-IP.Discover"}},
                    {"artifact": {"type": "tool", "name": "Related-IP.Discover"}},
                    {"artifact": {"type": "handler", "name": "Related-IP.Discover"}},
                    {"artifact": {"type": "messageType", "name": "Related-IP.Discover.Input"}},
                    {"artifact": {"type": "messageType", "name": "Related-IP.Discover.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
        {
            "name": "IP-Assets.Discover",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Identifies patents, trademarks, copyrights, trade dress, and proprietary technologies associated with an entity.",
            "tags": ["patents", "trademarks", "copyrights", "ipDiscovery", "portfolioAnalysis"],
            "examples": [
                "List all patents held by Company X",
                "What trademarks does this brand own"
            ]
        },
        {
            "name": "IP-Assets.Discover",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Identifies patents, trademarks, copyrights, trade dress, and proprietary technologies associated with an entity.",
            "tags": ["patents", "trademarks", "copyrights", "ipDiscovery", "portfolioAnalysis"],
            "examples": [
                "List all patents held by Company X",
                "What trademarks does this brand own"
            ]
        },
        {
            "name": "IP-Assets.Discover",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Identifies patents, trademarks, copyrights, trade dress, and proprietary technologies associated with an entity.",
            "capabilities": ["discover"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-Assets.Discover.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-Assets.Discover",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-Assets.Discover.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.input.schema.json" },
            "description": "Input schema for IP-Assets.Discover."
        },
        {
            "name": "IP-Assets.Discover.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.output.schema.json" },
            "description": "Output schema for IP-Assets.Discover."
        },
        {
            "name": "IP-to-Products.Map",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Determines which products, services, or features implement or rely on specific IP assets.",
            "tags": ["productMapping", "implementationDiscovery", "ipUsage", "portfolioLinkage"],
            "examples": [
                "Which products use Patent US-XXXXXXX",
                "What patents does this proprietary service rely on"
            ]
        },
        {
            "name": "IP-to-Products.Map",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Determines which products, services, or features implement or rely on specific IP assets.",
            "tags": ["productMapping", "implementationDiscovery", "ipUsage", "portfolioLinkage"],
            "examples": [
                "Which products use Patent US-XXXXXXX",
                "What patents does this proprietary service rely on"
            ]
        },
        {
            "name": "IP-to-Products.Map",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Determines which products, services, or features implement or rely on specific IP assets.",
            "capabilities": ["map"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-to-Products.Map.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-to-Products.Map",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-to-Products.Map.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.input.schema.json" },
            "description": "Input schema for IP-to-Products.Map."
        },
        {
            "name": "IP-to-Products.Map.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.output.schema.json" },
            "description": "Output schema for IP-to-Products.Map."
        },
        {
            "name": "Implementation-Instances.Search",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Searches for real-world implementations of an IP asset across products, SDKs, APIs, documentation, marketing materials, and technical artifacts.",
            "tags": ["implementationSearch", "competitiveIntelligence", "techDiscovery"],
            "examples": [
                "Where is this patented method implemented",
                "Find instances of this algorithm in the vendor’s ecosystem"
            ]
        },
        {
            "name": "Implementation-Instances.Search",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Searches for real-world implementations of an IP asset across products, SDKs, APIs, documentation, marketing materials, and technical artifacts.",
            "tags": ["implementationSearch", "competitiveIntelligence", "techDiscovery"],
            "examples": [
                "Where is this patented method implemented",
                "Find instances of this algorithm in the vendor’s ecosystem"
            ]
        },
        {
            "name": "Implementation-Instances.Search",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Searches for real-world implementations of an IP asset across products, SDKs, APIs, documentation, marketing materials, and technical artifacts.",
            "capabilities": ["search"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Implementation-Instances.Search.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Implementation-Instances.Search",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Implementation-Instances.Search.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.input.schema.json" },
            "description": "Input schema for Implementation-Instances.Search."
        },
        {
            "name": "Implementation-Instances.Search.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.output.schema.json" },
            "description": "Output schema for Implementation-Instances.Search."
        },
        {
            "name": "Use-Cases.Infer",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Analyzes IP assets to infer potential applications, commercial uses, and strategic value.",
            "tags": ["useCaseInference", "strategicAnalysis", "innovationMapping"],
            "examples": [
                "What could this patent be used for",
                "Infer use cases for this portfolio"
            ]
        },
        {
            "name": "Use-Cases.Infer",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Analyzes IP assets to infer potential applications, commercial uses, and strategic value.",
            "tags": ["useCaseInference", "strategicAnalysis", "innovationMapping"],
            "examples": [
                "What could this patent be used for",
                "Infer use cases for this portfolio"
            ]
        },
        {
            "name": "Use-Cases.Infer",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Analyzes IP assets to infer potential applications, commercial uses, and strategic value.",
            "capabilities": ["infer"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Use-Cases.Infer.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Use-Cases.Infer",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Use-Cases.Infer.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.input.schema.json" },
            "description": "Input schema for Use-Cases.Infer."
        },
        {
            "name": "Use-Cases.Infer.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.output.schema.json" },
            "description": "Output schema for Use-Cases.Infer."
        },
        {
            "name": "IP-Portfolio.Cluster",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Groups IP assets into themes, technologies, or product domains to reveal strategic clusters.",
            "tags": ["portfolioClustering", "taxonomy", "classification", "strategicThemes"],
            "examples": [
                "Cluster this company’s patents into technology areas",
                "Group trademarks by product line"
            ]
        },
        {
            "name": "IP-Portfolio.Cluster",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Groups IP assets into themes, technologies, or product domains to reveal strategic clusters.",
            "tags": ["portfolioClustering", "taxonomy", "classification", "strategicThemes"],
            "examples": [
                "Cluster this company’s patents into technology areas",
                "Group trademarks by product line"
            ]
        },
        {
            "name": "IP-Portfolio.Cluster",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Groups IP assets into themes, technologies, or product domains to reveal strategic clusters.",
            "capabilities": ["cluster"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-Portfolio.Cluster.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-Portfolio.Cluster",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-Portfolio.Cluster.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.input.schema.json" },
            "description": "Input schema for IP-Portfolio.Cluster."
        },
        {
            "name": "IP-Portfolio.Cluster.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.output.schema.json" },
            "description": "Output schema for IP-Portfolio.Cluster."
        },
        {
            "name": "IP-Report.Generate",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Produces a structured, regulator-friendly report summarizing discovered IP, implementations, inferred use cases, and strategic insights.",
            "tags": ["reporting", "audit", "documentation", "evidence"],
            "examples": [
                "Create an IP summary for Company X",
                "Generate a report of patents used in proprietary services"
            ]
        },
        {
            "name": "IP-Report.Generate",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Produces a structured, regulator-friendly report summarizing discovered IP, implementations, inferred use cases, and strategic insights.",
            "tags": ["reporting", "audit", "documentation", "evidence"],
            "examples": [
                "Create an IP summary for Company X",
                "Generate a report of patents used in proprietary services"
            ]
        },
        {
            "name": "IP-Report.Generate",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Produces a structured, regulator-friendly report summarizing discovered IP, implementations, inferred use cases, and strategic insights.",
            "capabilities": ["generate"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-Report.Generate.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-Report.Generate",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-Report.Generate.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.input.schema.json" },
            "description": "Input schema for IP-Report.Generate."
        },
        {
            "name": "IP-Report.Generate.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.output.schema.json" },
            "description": "Output schema for IP-Report.Generate."
        },
        {
            "name": "IP-Risk.Evaluate",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Assesses potential infringement exposure, licensing obligations, exclusivity constraints, and competitive risks.",
            "tags": ["riskAssessment", "infringementRisk", "licensing", "competitiveRisk"],
            "examples": [
                "What risks arise from using this patented method",
                "Evaluate licensing obligations for this portfolio"
            ]
        },
        {
            "name": "IP-Risk.Evaluate",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Assesses potential infringement exposure, licensing obligations, exclusivity constraints, and competitive risks.",
            "tags": ["riskAssessment", "infringementRisk", "licensing", "competitiveRisk"],
            "examples": [
                "What risks arise from using this patented method",
                "Evaluate licensing obligations for this portfolio"
            ]
        },
        {
            "name": "IP-Risk.Evaluate",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Assesses potential infringement exposure, licensing obligations, exclusivity constraints, and competitive risks.",
            "capabilities": ["evaluate"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-Risk.Evaluate.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-Risk.Evaluate",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-Risk.Evaluate.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.input.schema.json" },
            "description": "Input schema for IP-Risk.Evaluate."
        },
        {
            "name": "IP-Risk.Evaluate.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.output.schema.json" },
            "description": "Output schema for IP-Risk.Evaluate."
        },
        {
            "name": "IP-Provenance.Trace",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Tracks ownership history, assignments, transfers, and corporate lineage of IP assets.",
            "tags": ["provenance", "ownership", "assignments", "corporateLineage"],
            "examples": [
                "Who originally owned this patent",
                "Trace ownership changes for this portfolio"
            ]
        },
        {
            "name": "IP-Provenance.Trace",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Tracks ownership history, assignments, transfers, and corporate lineage of IP assets.",
            "tags": ["provenance", "ownership", "assignments", "corporateLineage"],
            "examples": [
                "Who originally owned this patent",
                "Trace ownership changes for this portfolio"
            ]
        },
        {
            "name": "IP-Provenance.Trace",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Tracks ownership history, assignments, transfers, and corporate lineage of IP assets.",
            "capabilities": ["trace"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/IP-Provenance.Trace.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-provenance.trace.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-provenance.trace.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "IP-Provenance.Trace",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "IP-Provenance.Trace.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "#/schemas/IP-Provenance.Trace#/definitions/Input" },
            "description": "Input schema for IP-Provenance.Trace."
        },
        {
            "name": "IP-Provenance.Trace.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/ip-provenance.trace.input.schema.json" },
            "description": "Output schema for IP-Provenance.Trace."
        },
        {
            "name": "Related-IP.Discover",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Identifies similar, adjacent, or competing IP assets across the market.",
            "tags": ["relatedPatents", "competitiveLandscape", "similaritySearch"],
            "examples": [
                "Find patents similar to US-XXXXXXX",
                "Identify competing IP in this domain"
            ]
        },
        {
            "name": "Related-IP.Discover",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Identifies similar, adjacent, or competing IP assets across the market.",
            "tags": ["relatedPatents", "competitiveLandscape", "similaritySearch"],
            "examples": [
                "Find patents similar to US-XXXXXXX",
                "Identify competing IP in this domain"
            ]
        },
        {
            "name": "Related-IP.Discover",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Identifies similar, adjacent, or competing IP assets across the market.",
            "capabilities": ["discover"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Related-IP.Discover.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Related-IP.Discover",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Related-IP.Discover.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.input.schema.json" },
            "description": "Input schema for Related-IP.Discover."
        },
        {
            "name": "Related-IP.Discover.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.output.schema.json" },
            "description": "Output schema for Related-IP.Discover."
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}