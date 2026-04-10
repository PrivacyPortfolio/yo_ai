/**
 * This Solicitor-General AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, tools, and artifacts for Registered Agents
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Solicitor-General Authenticated Extended AgentCard¶
*/
{
    "name": "Solicitor-General",
    "description": "Root Agent that logs all platform events, manages tasks and storage, and correlates requests with responses for routing.",
    "url": "https://privacyportfolio.com/agent-registry/solicitor-general/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/solicitor-general/solicitor-general-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/solicitor-general/auth/Solicitor-General-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Just-Ask"},
        {"name": "Event.Log"}
    ],
    "x-ai": {
        "providers": [
        {
            "provider": "google-gemini",
            "model": "gemini-2.0-pro",
            "api_key_env": "GEMINI_API_KEY",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent"
        },
        {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "api_key_env": "ANTHROPIC_API_KEY"
        },
        {
            "provider": "openai",
            "model": "gpt-4.2",
            "api_key_env": "OPENAI_API_KEY"
        },
        {
            "provider": "azure-openai",
            "deployment": "gpt-4o",
            "endpoint": "https://my-azure.openai.azure.com",
            "api_key_env": "AZURE_OPENAI_KEY"
        }
        ],
        "strategy": "failover",
        "health_ttl_seconds": 300
    },  
    "x-capabilities": [
        {
            "Just-Ask": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Just-Ask"}},
                    {"artifact": {"type": "task", "name": "Just-Ask"}},
                    {"artifact": {"type": "tool", "name": "Just-Ask"}},
                    {"artifact": {"type": "handler", "name": "Just-Ask"}},
                    {"artifact": {"type": "messageType", "name": "Just-Ask.Input"}},
                    {"artifact": {"type": "messageType", "name": "Just-Ask.Output"}}
                ]
            }
        },
        {
            "Event.Log": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Event.Log"}},
                    {"artifact": {"type": "task", "name": "Event.Log"}},
                    {"artifact": {"type": "tool", "name": "Event.Log"}},
                    {"artifact": {"type": "handler", "name": "Event.Log"}},
                    {"artifact": {"type": "messageType", "name": "Event.Log.Input"}},
                    {"artifact": {"type": "messageType", "name": "Event.Log.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
        {
        "name": "Just-Ask",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Default interface with the Yo-ai Platform.",
        "tags": ["introduction"],
        "examples": ["What can I do on the Yo-ai Platform"]
        },
        {
        "name": "Just-Ask",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Default interface with the Yo-ai Platform.",
        "tags": ["introduction"],
        "examples": ["What can I do on the Yo-ai Platform"]
        },
                    {"artifact": {"type": "tool", "name": "Just-Ask"}},
        {
        "name": "Just-Ask",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Default interface with the Yo-ai Platform.",
        "capabilities": ["chat"],
        "path": "/",
        "provider": {
            "name": "PrivacyPortfolio",
            "brand": "Yo-ai",
            "product": "",
            "version": "1.0.0",
            "license": "Yo-ai Internal",
            "url": "https://yo-ai.ai/docs/Just-Ask.html",
            "config": {
            "backend": ""
            }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/just-ask.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/just-ask.output.schema.json" },
        "auth": "apiKey"
        },
        {
        "name": "Just-Ask",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Default interface with the Yo-ai Platform.",
        "path": "/"
        },
        {
        "name": "Just-Ask",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "https://yo-ai.ai/schemas/just-ask.input.schema.json" },
        "description": "Input schema for ."
        },
        {
        "name": "Just-Ask.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "https://yo-ai.ai/schemas/just-ask.output.schema.json" },
        "description": "Output schema for ."
        },
        {
        "name": "Event.Log",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Inserts a record into the EventLog.",
        "tags": ["audit"],
        "examples": ["Log event"]
        },
        {
        "name": "Event.Log",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Inserts a record into the EventLog.",
        "tags": ["audit"],
        "examples": ["Log event"]
        },
        {
        "name": "Event.Log",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Inserts a record into the EventLog.",
        "capabilities": ["log"],
        "path": "/",
        "provider": {
            "name": "PrivacyPortfolio",
            "brand": "Yo-ai",
            "product": "",
            "version": "1.0.0",
            "license": "Yo-ai Internal",
            "url": "https://yo-ai.ai/docs/Event.Log.html",
            "config": {
            "backend": ""
            }
        },
        "inputSchema": { "$ref": "#/schemas/Event.Log.Input" },
        "outputSchema": { "$ref": "#/schemas/Event.Log.Output" },
        "auth": "apiKey"
        },
        {
        "name": "Event.Log",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
        },
        {
        "name": "Event.Log.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "#/schemas/Event.Log#/definitions/Input" },
        "description": "Input schema for ."
        },
        {
        "name": "Event.Log.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "#/schemas/Event.Log#/definitions/Output" },
        "description": "Output schema for ."
        }
   ],
    "supportsAuthenticatedExtendedCard": true
}