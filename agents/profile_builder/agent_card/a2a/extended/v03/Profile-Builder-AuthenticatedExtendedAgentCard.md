/**
 * This Profile-Builder AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Profile-Builder Authenticated Extended Agent Card¶
*/
{
  "name": "Profile-Builder",
  "description": "Builds and maintains organization profiles.",
  "url": "https://privacyportfolio.com/agent-registry/profile-builder/auth/agent.json",
  "provider": {
    "organization": "PrivacyPortfolio",
    "url": "https://www.PrivacyPortfolio.com"
    },
  "iconUrl": "https://privacyportfolio.com/agent-registry/profile-builder/profile-builder-agent-icon.png",
  "version": "1.0.0",
  "documentationUrl": "https://privacyportfolio.com/agent-registry/profile-builder/auth/Profile-Builder-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Org-Profile.Build"}
    ],
    "x-capabilities": [
        {
          "Org-Profile.Build": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Org-Profile.Build"}},
                  {"artifact": {"type": "task", "name": "Org-Profile.Build"}},
                  {"artifact": {"type": "tool", "name": "Org-Profile.Build"}},
                  {"artifact": {"type": "handler", "name": "Org-Profile.Build"}},
                  {"artifact": {"type": "messageType", "name": "Org-Profile.Build.Input"}},
                  {"artifact": {"type": "messageType", "name": "Org-Profile.Build.Output"}}
              ]
          }
        }
    ],
    "x-artifacts": [
      {
        "name": "Org-Profile.Build",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Build organization profiles based on discovery from IP-Inspector and Tech-Inspector agents.",
        "tags": ["public", "private", "affiliate"]
      },
      {
        "name": "Org-Profile.Build",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Build organization profiles based on discovery from IP-Inspector and Tech-Inspector agents.",
        "tags": ["public", "private", "affiliate"]
      },
      {
        "name": "Org-Profile.Build",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Build organization profiles based on discovery from IP-Inspector and Tech-Inspector agents.",
        "capabilities": ["build"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Org-Profile.Build.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Org-Profile.Build",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Org-Profile.Build.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.input.schema.json" },
        "description": "Input schema for Org-Profile.Build."
      },
      {
        "name": "Org-Profile.Build.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": { "$ref": "https://yo-ai.ai/schemas/org-profile.build.output.schema.json" },
        "description": "Output schema for Org-Profile.Build."
      }
  ],
  "supportsAuthenticatedExtendedCard": true
}