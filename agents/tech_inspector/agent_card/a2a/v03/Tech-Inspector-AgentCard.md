/**
 * This Tech-Inspector AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 * - AuthenticatedExtendedCard contains tasks and messages for Registered Agents
 */

/**
* Tech-Inspector AgentCard¶
*/
{
    "name": "Tech-Inspector",
    "description": "Discovers technology vendors of a specific organization.",
    "url": "https://privacyportfolio.com/agent-registry/tech-inspector/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/tech-inspector/tech-inspector-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/tech-inspector/Tech-Inspector-AgentCard.md",
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
        "name": "Third-Party-Assets.Discover",
        "description": "Identifies third-party technologies, services, SDKs, APIs, data feeds, modules, and vendor-provided assets used by an organization.",
        "tags": ["thirdParty", "assetDiscovery", "vendorTech", "integrationInventory"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "List all third-party technologies used by Vendor X",
            "Discover external services integrated into this product"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/third-party-assets.discover.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/third-party-assets.discover.output.schema.json" }
    },
    {
        "name": "Asset-Integrations.Map",
        "description": "Determines how third-party assets are integrated into organizational systems, workflows, data flows, and technical domains.",
        "tags": ["integrationMapping", "systemArchitecture", "dependencyAnalysis"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "How is this third-party service integrated into our workflow",
            "Map integrations for this vendor-provided SDK"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/asset-integrations.map.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/asset-integrations.map.output.schema.json" }
    },
    {
        "name": "Implementation-Details.Analyze",
        "description": "Examines implementation patterns, configuration, data flows, and operational dependencies of third-party assets.",
        "tags": ["implementationAnalysis", "configuration", "dataFlow", "technicalAssessment"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Analyze how this API is implemented",
            "Review configuration and data flow for this integration"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-details.analyze.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/implementation-details.analyze.output.schema.json" }
    },
    {
        "name": "Usage-Instances.Search",
        "description": "Searches for real-world usage instances of third-party assets across systems, documentation, codebases, and operational artifacts.",
        "tags": ["usageDiscovery", "techDiscovery", "integrationSearch"],
        "input_modes": ["application/json", "text/plain"],
        "output_modes": ["application/json"],
        "examples": [
            "Where is this SDK used in our environment",
            "Find all systems that rely on this vendor service"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/usage-instances.search.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/usage-instances.search.output.schema.json" }
    },
    {
        "name": "Technical-Impact.Infer",
        "description": "Infers the operational, architectural, and compliance impact of integrating a third-party asset.",
        "tags": ["impactAnalysis", "architecture", "riskAssessment", "technicalDependencies"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "What is the technical impact of using this vendor service",
            "Infer risks and dependencies for this integration"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/technical-impact.infer.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/technical-impact.infer.output.schema.json" }
    },
    {
        "name": "Asset-Portfolio.Cluster",
        "description": "Groups third-party assets into categories such as infrastructure, analytics, identity, data processing, or operational tooling.",
        "tags": ["portfolioClustering", "taxonomy", "classification", "techDomains"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Cluster all third-party assets used by this vendor",
            "Group integrations by technical domain"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/asset-portfolio.cluster.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/asset-portfolio.cluster.output.schema.json" }
    },
    {
        "name": "Integration-Risk.Evaluate",
        "description": "Assesses security, privacy, operational, and compliance risks associated with third-party integrations.",
        "tags": ["riskAssessment", "security", "privacy", "operationalRisk"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Evaluate risk for integrating this external service",
            "Assess compliance impact of this third-party SDK"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/integration-risk.evaluate.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/integration-risk.evaluate.output.schema.json" }
    },
    {
        "name": "Integration-Provenance.Trace",
        "description": "Tracks the origin, version history, update lineage, and vendor changes for third-party assets.",
        "tags": ["provenance", "versioning", "vendorLineage"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Trace provenance for this SDK",
            "Show version history and vendor changes"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/integration-provenance.trace.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/integration-provenance.trace.output.schema.json" }
    },
    {
        "name": "Related-Assets.Detect",
        "description": "Identifies similar or alternative third-party assets across the market, including competing or complementary technologies.",
        "tags": ["competitiveLandscape", "similaritySearch", "alternatives"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Find alternatives to this vendor service",
            "Identify similar SDKs in this domain"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/related-assets.detect.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/related-assets.detect.output.schema.json" }
    },
    {
        "name": "Tech-Report.Generate",
        "description": "Produces a structured, regulator-friendly report summarizing discovered assets, integrations, risks, and technical impact.",
        "tags": ["reporting", "audit", "documentation", "evidence"],
        "input_modes": ["application/json"],
        "output_modes": ["application/json"],
        "examples": [
            "Generate a tech integration report for Vendor X",
            "Create a summary of all third-party assets used in this system"
        ],
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/tech-report.generate.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/tech-report.generate.output.schema.json" }
    }
  ],
  "supportsAuthenticatedExtendedCard": true
}