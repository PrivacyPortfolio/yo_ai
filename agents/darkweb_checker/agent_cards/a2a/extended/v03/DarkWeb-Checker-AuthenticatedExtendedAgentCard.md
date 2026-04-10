/**
 * This DarkWeb-Checker AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* DarkWeb-Checker Authenticated Extended Agent Card¶
*/
{
    "name": "DarkWeb-Checker",
    "description": "Search breach forums, marketplaces, and dark web sources for stolen PI — and collect evidence to support claims that an organization acquired or used stolen data.",
    "url": "https://privacyportfolio.com/agent-registry/darkweb-checker/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/darkweb-checker/darkweb-checker-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/darkweb-checker/auth/DarkWeb-Checker-AuthenticatedExtendedAgentCard.md",
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
    "security": [
        { "yo-ai": ["apiKey", "yo-api", "header"] }
    ],
    "defaultInputModes": ["application/json", "text/plain"],
    "defaultOutputModes": ["application/json", "text/plain"],
    "skills": [
        {"name": "Dark-Web.Scan"},
        {"name": "Data-Origins.Trace"},
        {"name": "Dark-Web-Evidence.Collect"}
    ],
    "x-capabilities": [
        {
            "Dark-Web.Scan": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Dark-Web.Scan"}},
                    {"artifact": {"type": "task", "name": "Dark-Web.Scan"}},
                    {"artifact": {"type": "tool", "name": "Dark-Web.Scan"}},
                    {"artifact": {"type": "handler", "name": "Dark-Web.Scan"}},
                    {"artifact": {"type": "messageType", "name": "Dark-Web.Scan.Input"}},
                    {"artifact": {"type": "messageType", "name": "Dark-Web.Scan.Output"}}
                ]
            }
        },
        {
            "Data-Origins.Trace": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Data-Origins.Trace"}},
                    {"artifact": {"type": "task", "name": "Data-Origins.Trace"}},
                    {"artifact": {"type": "tool", "name": "Data-Origins.Trace"}},
                    {"artifact": {"type": "handler", "name": "Data-Origins.Trace"}},
                    {"artifact": {"type": "messageType", "name": "Data-Origins.Trace.Input"}},
                    {"artifact": {"type": "messageType", "name": "Data-Origins.Trace.Output"}}
                ]
            }
        },
        {
            "Dark-Web-Evidence.Collect": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Dark-Web-Evidence.Collect"}},
                    {"artifact": {"type": "task", "name": "Dark-Web-Evidence.Collect"}},
                    {"artifact": {"type": "tool", "name": "Dark-Web-Evidence.Collect"}},
                    {"artifact": {"type": "handler", "name": "Dark-Web-Evidence.Collect"}},
                    {"artifact": {"type": "messageType", "name": "Dark-Web-Evidence.Collect.Input"}},
                    {"artifact": {"type": "messageType", "name": "Dark-Web-Evidence.Collect.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
        {
            "name": "Dark-Web.Scan",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Searches breach forums, marketplaces, and dark web sources for stolen personal information.",
            "tags": ["darkweb", "breach", "scan", "logEvent"],
            "examples": [
                "Search for email in breach dump",
                "Check if phone number appears in dark web dataset",
                "Scan for identity package listings"
            ]
        },
        {
            "name": "Dark-Web.Scan",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Searches breach forums, marketplaces, and dark web sources for stolen personal information.",
            "tags": ["darkweb", "breach", "scan", "logEvent"],
            "examples": [
                "Search for email in breach dump",
                "Check if phone number appears in dark web dataset",
                "Scan for identity package listings"
            ]
        },
        {
            "name": "Dark-Web.Scan",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Searches breach forums, marketplaces, and dark web sources for stolen personal information.",
            "capabilities": ["scan"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Dark-Web.Scan.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Dark-Web.Scan",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Dark-Web.Scan.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.input.schema.json" },
            "description": "Input schema for Dark-Web.Scan capability."
        },
        {
            "name": "Dark-Web.Scan.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": { "$ref": "https://yo-ai.ai/schemas/dark-web.scan.output.schema.json" },
            "description": "Output schema for Dark-Web.Scan capability."
        },
        {
            "name": "Data-Origins.Trace",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Analyzes stolen data to infer which organization may have leaked or sold the information.",
            "tags": ["breach", "origin", "analysis", "logEvent"],
            "examples": [
                "Identify likely source of stolen data",
                "Match dataset structure to known vendor",
                "Infer breach origin"
            ]
        },
        {
            "name": "Data-Origins.Trace",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Analyzes stolen data to infer which organization may have leaked or sold the information.",
            "tags": ["breach", "origin", "analysis", "logEvent"],
            "examples": [
                "Identify likely source of stolen data",
                "Match dataset structure to known vendor",
                "Infer breach origin"
            ]
        },
        {
            "name": "Data-Origins.Trace",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Analyzes stolen data to infer which organization may have leaked or sold the information.",
            "capabilities": ["trace"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Data-Origins.Trace.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Data-Origins.Trace",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
          "name": "Data-Origins.Trace.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.input.schema.json" },
          "description": "Input schema for the Data-Origins.Trace capability."
        },
        {
          "name": "Data-Origins.Trace.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": { "$ref": "https://yo-ai.ai/schemas/data-origins.trace.output.schema.json" },
          "description": "Output schema for the Data-Origins.Trace capability."
        },
        {
            "name": "Dark-Web-Evidence.Collect",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Captures structured evidence of stolen PI to support complaints, deletion requests, or regulatory escalation.",
            "tags": ["evidence", "darkweb", "compliance", "logEvent"],
            "examples": [
                "Record breach listing",
                "Store dataset hash",
                "Capture seller metadata"
            ]
        },
        {
            "name": "Dark-Web-Evidence.Collect",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Captures structured evidence of stolen PI to support complaints, deletion requests, or regulatory escalation.",
            "tags": ["evidence", "darkweb", "compliance", "logEvent"],
            "examples": [
                "Record breach listing",
                "Store dataset hash",
                "Capture seller metadata"
            ]
        },
        {
            "name": "Dark-Web-Evidence.Collect",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Captures structured evidence of stolen PI to support complaints, deletion requests, or regulatory escalation.",
            "capabilities": ["collect"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Dark-Web-Evidence.Collect.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Dark-Web-Evidence.Collect",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
          "name": "Dark-Web-Evidence.Collect.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.input.schema.json"
          },
          "description": "Input schema for the Dark-Web-Evidence.Collect capability."
        },
        {
          "name": "Dark-Web-Evidence.Collect.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": { "$ref": "https://yo-ai.ai/schemas/dark-web-evidence.collect.output.schema.json" },
          "description": "Output schema for the Dark-Web-Evidence.Collect capability."
        }
   ],
    "supportsAuthenticatedExtendedCard": true
}