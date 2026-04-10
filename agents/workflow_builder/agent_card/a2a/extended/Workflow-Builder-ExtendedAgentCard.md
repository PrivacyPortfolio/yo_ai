/**
 * This Workflow-Builder ExtendedCard conveys:
 * - ExtendedCard contains tasks, messages, tools, and artifacts for Registered Agents
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Workflow-Builder Extended AgentCard¶
*/
{
  "name": "Workflow-Builder",
  "description": "Agent that builds workflows connecting agents with endpoints.",
  "id": "com.privacyportfolio.workflow-builder",
  "provider": {
    "organization": "PrivacyPortfolio",
    "url": "https://www.PrivacyPortfolio.com"
    },
  "iconUrl": "https://privacyportfolio.com/agent-directory/workflow-builder/workflow-builder-agent-icon.png",
  "protocolVersion": "1.0.0",
  "documentationUrl": "https://privacyportfolio.com/agent-directory/workflow-builder/auth/Workflow-Builder-ExtendedAgentCard.md",
  "supportedInterfaces": [
    {      "url": "https://privacyportfolio.com/agents/workflow_builder/a2a",
      "protocolBinding": "JSONRPC_HTTP",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/workflow_builder/mesh",
      "protocolBinding": "RPC",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/workflow_builder/api",
      "protocolBinding": "OPENAI_API",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/workflow_builder/app",
      "protocolBinding": "MCP",      "protocolVersion": "1.0"    },
    {      "url": "https://privacyportfolio.com/agents/workflow_builder/op",
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
  "defaultOutputModes": ["application/json", "image/png"],
    "skills": [
        {"name": "Workflow.Build"}
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
          "Workflow.Build": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Workflow.Build"}},
                  {"artifact": {"type": "task", "name": "Workflow.Build"}},
                  {"artifact": {"type": "tool", "name": "Workflow.Build"}},
                  {"artifact": {"type": "handler", "name": "Workflow.Build"}},
                  {"artifact": {"type": "messageType", "name": "Workflow.Build.Input"}},
                  {"artifact": {"type": "messageType", "name": "Workflow.Build.Output"}}
              ]
          }
        }
    ],
    "x-artifacts": [
        {
        "name": "Workflow.Build",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Builds orchestrated workflows connecting agents with endpoints.",
        "tags": ["-wf", "internal", "external"]
        },
        {
        "name": "Workflow.Build",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Builds orchestrated workflows connecting agents with endpoints.",
        "tags": ["-wf", "internal", "external"]
        },
        {
        "name": "Workflow.Build",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Builds orchestrated workflows connecting agents with endpoints.",
        "capabilities": ["build"],
        "path": "/",
        "provider": {
            "name": "PrivacyPortfolio",
            "brand": "Yo-ai",
            "product": "",
            "version": "1.0.0",
            "license": "Yo-ai Internal",
            "url": "https://yo-ai.ai/docs/Workflow.Build.html",
            "config": {
            "backend": ""
            }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/workflow.build.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/workflow.build.output.schema.json" },
        "auth": "apiKey"
        },
        {
        "name": "Workflow.Build",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
        },
        {
          "name": "Workflow.Build.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/workflow.build.input.schema.json"
          },
          "description": "Input schema for the Workflow.Build capability."
        },
        {
          "name": "Workflow.Build.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/workflow.build.output.schema.json"
          },
          "description": "Output schema for the Workflow.Build capability."
        }
    ]
}