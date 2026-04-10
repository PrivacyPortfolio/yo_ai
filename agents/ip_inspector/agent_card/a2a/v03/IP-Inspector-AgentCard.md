/**
 * This IP-Inspector AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 */

/**
* IP-Inspector AgentCard¶
*/
{
    "name": "IP-Inspector",
    "description": "Discovers intellectual property and potential use cases, and searches for implementation instances.",
    "url": "https://privacyportfolio.com/agent-registry/ip-inspector/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/ip-inspector/ip-inspector-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/ip-inspector/IP-Inspector-AgentCard.md",
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
            "name": "IP-Assets.Discover",
            "description": "Identifies patents, trademarks, copyrights, trade dress, and proprietary technologies associated with an entity.",
            "tags": ["patents", "trademarks", "copyrights", "ipDiscovery", "portfolioAnalysis"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "List all patents held by Company X",
                "What trademarks does this brand own"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-assets.discover.output.schema.json" }
        },
        {
            "name": "IP-to-Products.Map",
            "description": "Determines which products, services, or features implement or rely on specific IP assets.",
            "tags": ["productMapping", "implementationDiscovery", "ipUsage", "portfolioLinkage"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Which products use Patent US-XXXXXXX",
                "What patents does this proprietary service rely on"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-to-products.map.output.schema.json" }
        },
        {
            "name": "Implementation-Instances.Search",
            "description": "Searches for real-world implementations of an IP asset across products, SDKs, APIs, documentation, marketing materials, and technical artifacts.",
            "tags": ["implementationSearch", "competitiveIntelligence", "techDiscovery"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Where is this patented method implemented",
                "Find instances of this algorithm in the vendor’s ecosystem"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-instances.search.output.schema.json" }
        },
        {
        "name": "Use-Cases.Infer",
        "description": "Analyzes IP assets to infer potential applications, commercial uses, and strategic value.",
        "tags": ["useCaseInference", "strategicAnalysis", "innovationMapping"],
        "input_modes": ["application/json", "text/plain"],
        "output_modes": ["application/json", "text/plain"],
        "examples": [
            "What could this patent be used for",
            "Infer use cases for this portfolio"
        ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/use-cases.infer.output.schema.json" }
        },
        {
            "name": "IP-Portfolio.Cluster",
            "description": "Groups IP assets into themes, technologies, or product domains to reveal strategic clusters.",
            "tags": ["portfolioClustering", "taxonomy", "classification", "strategicThemes"],
            "input_modes": ["application/json"],
            "output_modes": ["application/json"],
            "examples": [
                "Cluster this company’s patents into technology areas",
                "Group trademarks by product line"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-portfolio.cluster.output.schema.json" }
        },
        {
            "name": "IP-Report.Generate",
            "description": "Produces a structured, regulator-friendly report summarizing discovered IP, implementations, inferred use cases, and strategic insights.",
            "tags": ["reporting", "audit", "documentation", "evidence"],
            "input_modes": ["application/json"],
            "output_modes": ["application/json", "text/plain"],
            "examples": [
                "Create an IP summary for Company X",
                "Generate a report of patents used in proprietary services"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-report.generate.output.schema.json" }
        },
        {
            "name": "IP-Risk.Evaluate",
            "description": "Assesses potential infringement exposure, licensing obligations, exclusivity constraints, and competitive risks.",
            "tags": ["riskAssessment", "infringementRisk", "licensing", "competitiveRisk"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "What risks arise from using this patented method",
                "Evaluate licensing obligations for this portfolio"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-risk.evaluate.output.schema.json" }
        },
        {
            "name": "IP-Provenance.Trace",
            "description": "Tracks ownership history, assignments, transfers, and corporate lineage of IP assets.",
            "tags": ["provenance", "ownership", "assignments", "corporateLineage"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Who originally owned this patent",
                "Trace ownership changes for this portfolio"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-provenance.trace.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/ip-provenance.trace.output.schema.json" }
        },
        {
            "name": "Related-IP.Discover",
            "description": "Identifies similar, adjacent, or competing IP assets across the market.",
            "tags": ["relatedPatents", "competitiveLandscape", "similaritySearch"],
            "input_modes": ["application/json", "text/plain"],
            "output_modes": ["application/json"],
            "examples": [
                "Find patents similar to US-XXXXXXX",
                "Identify competing IP in this domain"
            ],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/related-ip.discover.output.schema.json" }
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}