/**
 * The-Sentinel ExtendedCard conveys:
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 * - ExtendedCard contains tasks and messages for Registered Agents
 */

/**
* The-Sentinel Extended Agent Card¶
*/
{
  "name": "The-Sentinel",
  "description": "Listens for dangerous incidents and trends, and issues alerts.",
  "id": "com.privacyportfolio.the-sentinel",
  "provider": {
    "organization": "PrivacyPortfolio",
    "url": "https://www.PrivacyPortfolio.com"
    },
  "iconUrl": "https://privacyportfolio.com/agent-directory/the-sentinel/the-sentinel-agent-icon.png",
  "protocolVersion": "1.0.0",
  "documentationUrl": "https://privacyportfolio.com/agent-directory/the-sentinel/auth/The-Sentinel-ExtendedAgentCard.md",
  "supportedInterfaces": [
    {      "url": "https://privacyportfolio.com/agents/the_sentinel/a2a",
      "protocolBinding": "JSONRPC_HTTP",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/the_sentinel/mesh",
      "protocolBinding": "RPC",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/the_sentinel/api",
      "protocolBinding": "OPENAI_API",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/the_sentinel/app",
      "protocolBinding": "MCP",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/the_sentinel/op",
      "protocolBinding": "REST",      "protocolVersion": "1.0"    }
  ], 
  "capabilities": {
      "streaming": true,
      "pushNotifications": true,
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
  "security": [{ "yo-ai": [] }],
  "defaultInputModes": ["application/json", "text/plain"],
  "defaultOutputModes": ["application/json", "text/plain"],
  "skills": [
     {"name": "Platform.Monitor"}
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
          "model": "gpt-4-turbo",
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
          "Platform.Monitor": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Platform.Monitor"}},
                  {"artifact": {"type": "task", "name": "Platform.Monitor"}},
                  {"artifact": {"type": "tool", "name": "Platform.Monitor"}},
                  {"artifact": {"type": "handler", "name": "Platform.Monitor"}},
                  {"artifact": {"type": "messageType", "name": "Platform.Monitor.Input"}},
                  {"artifact": {"type": "messageType", "name": "Platform.Monitor.Output"}}
              ]
          }
        }
    ],
    "x-artifacts": [
        {
          "name": "Platform.Monitor",
          "version": "1.0.0",
          "artifactType": "skill",
          "description": "Monitor platform for adverse events.",
          "tags": ["adverseEvent", "Listening"],
          "examples": [
              "Listening",
              "Get adverseEvent"
          ]
        },
        {
          "name": "Platform.Monitor",
          "version": "1.0.0",
          "artifactType": "task",
          "description": "Monitor platform for adverse events.",
          "tags": ["adverseEvent", "Listening"],
          "examples": [
              "Listening",
              "Get adverseEvent"
          ]
        },
        {
            "name": "Platform.Monitor",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Monitor platform for adverse events.",
            "capabilities": ["monitor"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Platform.Monitor.html",
                "config": {
                "backend": ""
                }
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/platform.monitor.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/platform.monitor.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Platform.Monitor",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
          "name": "Platform.Monitor.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/platform.monitor.input.schema.json"
          },
          "description": "Input schema for the Platform.Monitor capability."
        },
        {
          "name": "Platform.Monitor.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/platform.monitor.output.schema.json"
          },
          "description": "Output schema for the Platform.Monitor capability."
        }
    ]
}