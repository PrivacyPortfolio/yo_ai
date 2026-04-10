/**
 * This DarkWeb-Checker AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - ExtendedCard contains tasks and messages for Registered Agents
 */

/**
* DarkWeb-Checker AgentCard¶
*/
{
    "name": "DarkWeb-Checker",
    "description": "Search breach forums, marketplaces, and dark web sources for stolen PI — and collect evidence to support claims that an organization acquired or used stolen data.",
    "id": "com.privacyportfolio.darkweb-checker",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-directory/darkweb-checker/darkweb-checker-agent-icon.png",
    "protocolVersion": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-directory/darkweb-checker/DarkWeb-Checker-AgentCard.md",
    "supportedInterfaces": [
      {
        "url": "https://privacyportfolio.com/agents/darkweb_checker/a2a",
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
            "name": "Dark-Web.Scan",
            "description": "Searches breach forums, marketplaces, and dark web sources for stolen personal information.",
            "version": "1.0.0", 
            "tags": ["darkweb", "breach", "scan", "logEvent"],
            "examples": [
                "Search for email in breach dump",
                "Check if phone number appears in dark web dataset",
                "Scan for identity package listings"
            ],
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.output.schema.json" }
        },
        {
            "name": "Data-Origins.Trace",
            "description": "Analyzes stolen data to infer which organization may have leaked or sold the information.",
            "version": "1.0.0", 
            "tags": ["breach", "origin", "analysis", "logEvent"],
            "examples": [
                "Identify likely source of stolen data",
                "Match dataset structure to known vendor",
                "Infer breach origin"
            ],
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.output.schema.json" }
        },
        {
            "name": "Dark-Web-Evidence.Collect",
            "description": "Captures structured evidence of stolen PI to support complaints, deletion requests, or regulatory escalation.",
            "version": "1.0.0", 
            "tags": ["evidence", "darkweb", "compliance", "logEvent"],
            "examples": [
                "Record breach listing",
                "Store dataset hash",
                "Capture seller metadata"
            ],
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.output.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.output.schema.json" }
        }
    ]
}