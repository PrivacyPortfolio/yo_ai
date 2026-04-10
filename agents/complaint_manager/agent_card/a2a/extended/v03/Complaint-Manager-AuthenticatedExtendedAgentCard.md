/**
 * This Complaint-Manager AuthenticatedExtendedCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, tools, and artifacts for Registered Agents
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Complaint-Manager Authenticated Extended Agent Card¶
*/
{
    "name": "Complaint-Manager",
    "description": "Manages discovery, generation, submission, stakeholder notification, and publication of complaints to regulators, organizations, and named stakeholders.",
    "url": "https://privacyportfolio.com/agent-registry/complaint-manager/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
        },
    "iconUrl": "https://privacyportfolio.com/agent-registry/complaint-manager/complaint-manager-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/complaint-manager/auth/Complaint-Manager-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Liability.Discover"},
        {"name": "EnforcementAgency.Get"},
        {"name": "Stakeholders.Get"},
        {"name": "Complaint.Generate"},
        {"name": "Complaint.Submit"},
        {"name": "Complaint.Publish"},
        {"name": "Stakeholder.Notify"}
    ],
        "x-capabilities": [
        {
          "Liability.Discover": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Liability.Discover"}},
                  {"artifact": {"type": "task", "name": "Liability.Discover"}},
                  {"artifact": {"type": "tool", "name": "Liability.Discover"}},
                  {"artifact": {"type": "handler", "name": "Liability.Discover"}},
                  {"artifact": {"type": "messageType", "name": "Liability.Discover.Input"}},
                  {"artifact": {"type": "messageType", "name": "Liability.Discover.Output"}}
              ]
          }
        },
        {
          "EnforcementAgency.Get": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "EnforcementAgency.Get"}},
                  {"artifact": {"type": "task", "name": "EnforcementAgency.Get"}},
                  {"artifact": {"type": "tool", "name": "EnforcementAgency.Get"}},
                  {"artifact": {"type": "handler", "name": "EnforcementAgency.Get"}},
                  {"artifact": {"type": "messageType", "name": "EnforcementAgency.Get.Input"}},
                  {"artifact": {"type": "messageType", "name": "EnforcementAgency.Get.Output"}}
              ]
          }
        },
        {
          "Stakeholders.Get": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Stakeholders.Get"}},
                  {"artifact": {"type": "task", "name": "Stakeholders.Get"}},
                  {"artifact": {"type": "tool", "name": "Stakeholders.Get"}},
                  {"artifact": {"type": "handler", "name": "Stakeholders.Get"}},
                  {"artifact": {"type": "messageType", "name": "Stakeholders.Get.Input"}},
                  {"artifact": {"type": "messageType", "name": "Stakeholders.Get.Output"}}
              ]
          }
        },
        {
          "Complaint.Generate": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Complaint.Generate"}},
                  {"artifact": {"type": "task", "name": "Complaint.Generate"}},
                  {"artifact": {"type": "tool", "name": "Complaint.Generate"}},
                  {"artifact": {"type": "handler", "name": "Complaint.Generate"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Generate.Input"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Generate.Output"}}
              ]
          }
        },
        {
          "Complaint.Submit": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Complaint.Submit"}},
                  {"artifact": {"type": "task", "name": "Complaint.Submit"}},
                  {"artifact": {"type": "tool", "name": "Complaint.Submit"}},
                  {"artifact": {"type": "handler", "name": "Complaint.Submit"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Submit.Input"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Submit.Output"}}
              ]
          }
        },
        {
          "Complaint.Publish": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Complaint.Publish"}},
                  {"artifact": {"type": "task", "name": "Complaint.Publish"}},
                  {"artifact": {"type": "tool", "name": "Complaint.Publish"}},
                  {"artifact": {"type": "handler", "name": "Complaint.Publish"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Publish.Input"}},
                  {"artifact": {"type": "messageType", "name": "Complaint.Publish.Output"}}
              ]
          }
        },
        {
          "Stakeholder.Notify": {
              "artifacts": [
                  {"artifact": {"type": "skill", "name": "Stakeholder.Notify"}},
                  {"artifact": {"type": "task", "name": "Stakeholder.Notify"}},
                  {"artifact": {"type": "tool", "name": "Stakeholder.Notify"}},
                  {"artifact": {"type": "handler", "name": "Stakeholder.Notify"}},
                  {"artifact": {"type": "messageType", "name": "Stakeholder.Notify.Input"}},
                  {"artifact": {"type": "messageType", "name": "Stakeholder.Notify.Output"}}
              ]
          }
        }
    ],
    "x-artifacts": [
      {
        "name": "Liability.Discover",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Identifies potential liability, obligations, or violations based on facts, evidence, and applicable mandates.",
        "tags": ["liability", "compliance", "complaints"]
      },
      {
        "name": "Liability.Discover",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Identifies potential liability, obligations, or violations based on facts, evidence, and applicable mandates.",
        "tags": ["liability", "compliance", "complaints"]
      },
      {
        "name": "Liability.Discover",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Identifies potential liability, obligations, or violations based on facts, evidence, and applicable mandates.",
        "capabilities": ["discover"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Liability.Discover.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/liability.discover.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/liability.discover.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Liability.Discover",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Liability.Discover.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/liability.discover.input.schema.json"
        },
        "description": "Input schema for the Liability.Discover capability."
      },
      {
        "name": "Liability.Discover.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/liability.discover.output.schema.json"
        },
        "description": "Output schema for the Liability.Discover capability."
      },
      {
        "name": "EnforcementAgency.Get",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Determines the appropriate enforcement agency based on the mandate, jurisdiction, and organization.",
        "tags": ["regulators", "routing"]
      },
      {
        "name": "EnforcementAgency.Get",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Determines the appropriate enforcement agency based on the mandate, jurisdiction, and organization.",
        "tags": ["regulators", "routing"]
      },
      {
        "name": "EnforcementAgency.Get",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Determines the appropriate enforcement agency based on the mandate, jurisdiction, and organization.",
        "capabilities": ["get"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/EnforcementAgency.Get.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "EnforcementAgency.Get",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "EnforcementAgency.Get.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.input.schema.json"
        },
        "description": "Input schema for the EnforcementAgency.Get capability."
      },
      {
        "name": "EnforcementAgency.Get.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/enforcementagency.get.output.schema.json"
        },
        "description": "Output schema for the EnforcementAgency.Get capability."
      },
      {
        "name": "Stakeholders.Get",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Retrieves stakeholders who must be notified or included in the complaint lifecycle.",
        "tags": ["stakeholders"]
      },
      {
        "name": "Stakeholders.Get",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Retrieves stakeholders who must be notified or included in the complaint lifecycle.",
        "tags": ["stakeholders"]
      },
      {
        "name": "Stakeholders.Get",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Retrieves stakeholders who must be notified or included in the complaint lifecycle.",
        "capabilities": ["get"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Stakeholders.Get.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholders.get.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholders.get.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Stakeholders.Get",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Stakeholders.Get.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/stakeholders.get.input.schema.json"
        },
        "description": "Input schema for the Stakeholders.Get capability."
      },
      {
        "name": "Stakeholders.Get.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/stakeholders.get.output.schema.json"
        },
        "description": "Output schema for the Stakeholders.Get capability."
      },
     {
        "name": "Complaint.Generate",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Generates a structured complaint document based on findings, facts, and applicable mandates.",
        "tags": ["complaints", "documents"]
      },
      {
        "name": "Complaint.Generate",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Generates a structured complaint document based on findings, facts, and applicable mandates.",
        "tags": ["complaints", "documents"]
      },
      {
        "name": "Complaint.Generate",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Generates a structured complaint document based on findings, facts, and applicable mandates.",
        "capabilities": ["generate"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Complaint.Generate.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.generate.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.generate.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Complaint.Generate",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Complaint.Generate.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.generate.input.schema.json"
        },
        "description": "Input schema for the Complaint.Generate capability."
      },
      {
        "name": "Complaint.Generate.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.generate.output.schema.json"
        },
        "description": "Output schema for the Complaint.Generate capability."
      },
      {
        "name": "Complaint.Submit",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Submits a complaint to the appropriate enforcement agency or organization.",
        "tags": ["submission", "regulators"]
      },
      {
        "name": "Complaint.Submit",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Submits a complaint to the appropriate enforcement agency or organization.",
        "tags": ["submission", "regulators"]
      },
      {
        "name": "Complaint.Submit",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Submits a complaint to the appropriate enforcement agency or organization.",
        "capabilities": ["submit"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Complaint.Submit.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.submit.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.submit.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Complaint.Submit",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Complaint.Submit.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.submit.input.schema.json"
        },
        "description": "Input schema for the Complaint.Submit capability."
      },
      {
        "name": "Complaint.Submit.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.submit.output.schema.json"
        },
        "description": "Output schema for the Complaint.Submit capability."
      },
      {
        "name": "Complaint.Publish",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Publishes a complaint to designated stakeholders or public registries.",
        "tags": ["publication"]
      },
      {
        "name": "Complaint.Publish",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Publishes a complaint to designated stakeholders or public registries.",
        "tags": ["publication"]
      },
      {
        "name": "Complaint.Publish",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Publishes a complaint to designated stakeholders or public registries.",
        "capabilities": ["publish"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Complaint.Publish.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.publish.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/complaint.publish.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Complaint.Publish",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Complaint.Publish.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.publish.input.schema.json"
        },
        "description": "Input schema for the Complaint.Publish capability."
      },
      {
        "name": "Complaint.Publish.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/complaint.publish.output.schema.json"
        },
        "description": "Output schema for the Complaint.Publish capability."
      },
      {
        "name": "Stakeholder.Notify",
        "version": "1.0.0",
        "artifactType": "skill",
        "description": "Sends a notification to a stakeholder regarding a complaint or enforcement action.",
        "tags": ["notifications"]
      },
      {
        "name": "Stakeholder.Notify",
        "version": "1.0.0",
        "artifactType": "task",
        "description": "Sends a notification to a stakeholder regarding a complaint or enforcement action.",
        "tags": ["notifications"]
      },
      {
        "name": "Stakeholder.Notify",
        "version": "1.0.0",
        "artifactType": "tool",
        "description": "Sends a notification to a stakeholder regarding a complaint or enforcement action.",
        "capabilities": ["notify"],
        "path": "/",
        "provider": {
          "name": "PrivacyPortfolio",
          "brand": "Yo-ai",
          "product": "",
          "version": "1.0.0",
          "license": "Yo-ai Internal",
          "url": "https://yo-ai.ai/docs/Stakeholder.Notify.html",
          "config": {
            "backend": ""
          }
        },
        "inputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.input.schema.json" },
        "outputSchema": { "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.output.schema.json" },
        "auth": "apiKey"
      },
      {
        "name": "Stakeholder.Notify",
        "version": "1.0.0",
        "artifactType": "handler",
        "description": "Interface for integrating with tool executable.",
        "path": "/"
      },
      {
        "name": "Stakeholder.Notify.Input",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.input.schema.json"
        },
        "description": "Input schema for the Stakeholder.Notify capability."
      },
      {
        "name": "Stakeholder.Notify.Output",
        "version": "1.0.0",
        "artifactType": "messageType",
        "schema": {
          "$ref": "https://yo-ai.ai/schemas/stakeholder.notify.output.schema.json"
        },
        "description": "Output schema for the Stakeholder.Notify capability."
      }
    ],
    "supportsAuthenticatedExtendedCard": true
}