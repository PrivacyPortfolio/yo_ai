/**
 * The-Sentinel AuthenticatedExtendedCard conveys:
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 * - AuthenticatedExtendedCard contains tasks and messages for Registered Agents
 */

/**
* The-Sentinel Authenticated Extended Agent Card¶
*/
{
  "name": "The-Sentinel",
  "description": "Listens for dangerous incidents and trends, and issues alerts.",
  "url": "https://privacyportfolio.com/agent-registry/the-sentinel/auth/agent.json",
  "provider": {
    "organization": "PrivacyPortfolio",
    "url": "https://www.PrivacyPortfolio.com"
    },
  "iconUrl": "https://privacyportfolio.com/agent-registry/the-sentinel/the-sentinel-agent-icon.png",
  "version": "1.0.0",
  "documentationUrl": "https://privacyportfolio.com/agent-registry/auth/The-Sentinel-AuthenticatedExtendedAgentCard.md",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true,
    "exposesTasks": true,
    "exposesMessages": true,
    "exposesArtifacts": false,
    "exposesTools": false
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
     {"name": "Platform.Monitor"}
    ],
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
    ],
    "supportsAuthenticatedExtendedCard": true
}