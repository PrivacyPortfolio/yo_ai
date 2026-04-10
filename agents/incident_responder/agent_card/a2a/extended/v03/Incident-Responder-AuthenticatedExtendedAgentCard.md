/**
 * This Incident-Responder AuthenticatedExtendedCard conveys:
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 * - Tasks, messages, and tools for Registered Agents.
 */

/**
* Incident-Responder Authenticated Extended Agent Card¶
*/
{
    "name": "Incident-Responder",
    "description": "Handles all unhandled exceptions and responds to platform incidents. (aka Agent-terminator, Kill-switch, etc)",
    "url": "https://privacyportfolio.com/agent-registry/incident-responder/auth/agent.json",
    "provider": {
      "organization": "PrivacyPortfolio",
      "url": "https://www.PrivacyPortfolio.com"
      },
    "iconUrl": "https://privacyportfolio.com/agent-registry/incident-responder/incident-responder-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/incident-responder/auth/Incident-Responder-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Handle.Exception"}
    ],
    "x-capabilities": [
        {
          "Handle.Exception": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Handle.Exception"}},
                  {"artifact": {"type": "task", "name": "Handle.Exception"}},
                  {"artifact": {"type": "tool", "name": "Handle.Exception"}},
                  {"artifact": {"type": "handler", "name": "Handle.Exception"}},
                  {"artifact": {"type": "messageType", "name": "Handle.Exception.Input"}},
                  {"artifact": {"type": "messageType", "name": "Handle.Exception.Output"}}
              ]
          }
        }
    ],
    "x-artifacts": [
        {
          "name": "Handle.Exception",
          "version": "1.0.0",
          "artifactType": "skill",
          "description": "Handle unhandled exception.",
          "tags": ["issue", "anomaly", "falsePositive", "warning"],
          "examples": [
            "Identify the code module",
            "Evaluate impact",
            "Build remediation workflow"
          ]
        },
        {
          "name": "Handle.Exception",
          "version": "1.0.0",
          "artifactType": "task",
          "description": "Handle unhandled exception.",
          "tags": ["issue", "anomaly", "falsePositive", "warning"],
          "examples": [
            "Identify the code module",
            "Evaluate impact",
            "Build remediation workflow"
          ]
        },
        {
          "name": "Handle.Exception",
          "version": "1.0.0",
          "artifactType": "tool",
          "description": "Handle unhandled exception.",
          "capabilities": ["handle"],
          "path": "/",
          "provider": {
            "name": "PrivacyPortfolio",
            "brand": "Yo-ai",
            "product": "",
            "version": "1.0.0",
            "license": "Yo-ai Internal",
            "url": "https://yo-ai.ai/docs/Handle.Exception.html",
            "config": {
              "backend": ""
            }
          },
          "inputSchema": { "$ref": "https://yo-ai.ai/schemas/handle.exception.input.schema.json" },
          "outputSchema": { "$ref": "https://yo-ai.ai/schemas/handle.exception.output.schema.json" },
          "auth": "apiKey"
        },
        {
          "name": "Handle.Exception",
          "version": "1.0.0",
          "artifactType": "handler",
          "description": "Interface for integrating with tool executable.",
          "path": "/"
        },
        {
          "name": "Handle.Exception.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/handle.exception.input.schema.json"
          },
          "description": "Input schema for the Handle.Exception capability."
        },
        {
          "name": "Handle.Exception.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/handle.exception.output.schema.json"
          },
          "description": "Output schema for the Handle.Exception capability."
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}