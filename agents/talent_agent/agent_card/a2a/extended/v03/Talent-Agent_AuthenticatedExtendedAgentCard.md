/**
 * This Talent-Agent AuthenticatedExtendedAgentCard conveys:
 * - AuthenticatedExtendedCard contains tasks, messages, artifacts, and tools for Registered Agents.
 * - Tasks: A task encapsulates the entire interaction related to a specific goal or request.
 * - Messages: Messages are used for instructions, prompts, replies, and status updates.
 * - Artifacts: Collection of artifacts created by the agent.
 */

/**
* Talent-Agent Authenticated Extended Agent Card¶
*/
{
    "name": "Talent-Agent",
    "description": "Agent responsible for responding to job postings, pitching consulting services, and managing professional opportunities.",
    "url": "https://privacyportfolio.com/agent-registry/talent-agent/auth/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://www.PrivacyPortfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/talent-agent/talent-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/talent-agent/auth/Talent-Agent-AuthenticatedExtendedAgentCard.md",
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
        {"name": "Job-Postings.Scan"},
        {"name": "Consulting-Services.Pitch"},
        {"name": "Application.Submit"},
        {"name": "Talent-Profile.Request"}
    ],
    "x-capabilities": [
        {
            "Job-Postings.Scan": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Job-Postings.Scan"}},
                    {"artifact": {"type": "task", "name": "Job-Postings.Scan"}},
                    {"artifact": {"type": "tool", "name": "Job-Postings.Scan"}},
                    {"artifact": {"type": "handler", "name": "Job-Postings.Scan"}},
                    {"artifact": {"type": "messageType", "name": "Job-Postings.Scan.Input"}},
                    {"artifact": {"type": "messageType", "name": "Job-Postings.Scan.Output"}}
                ]
            }
        },
        {
            "Consulting-Services.Pitch": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Consulting-Services.Pitch"}},
                    {"artifact": {"type": "task", "name": "Consulting-Services.Pitch"}},
                    {"artifact": {"type": "tool", "name": "Consulting-Services.Pitch"}},
                    {"artifact": {"type": "handler", "name": "Consulting-Services.Pitch"}},
                    {"artifact": {"type": "messageType", "name": "Consulting-Services.Pitch.Input"}},
                    {"artifact": {"type": "messageType", "name": "Consulting-Services.Pitch.Output"}}
                ]
            }
        },
        {
            "Application.Submit": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Application.Submit"}},
                    {"artifact": {"type": "task", "name": "Application.Submit"}},
                    {"artifact": {"type": "tool", "name": "Application.Submit"}},
                    {"artifact": {"type": "handler", "name": "Application.Submit"}},
                    {"artifact": {"type": "messageType", "name": "Application.Submit.Input"}},
                    {"artifact": {"type": "messageType", "name": "Application.Submit.Output"}}
                ]
            }
        },
        {
            "Talent-Profile.Request": {
                "artifacts": [
                    {"artifact": {"type": "skill", "name": "Talent-Profile.Request"}},
                    {"artifact": {"type": "task", "name": "Talent-Profile.Request"}},
                    {"artifact": {"type": "tool", "name": "Talent-Profile.Request"}},
                    {"artifact": {"type": "handler", "name": "Talent-Profile.Request"}},
                    {"artifact": {"type": "messageType", "name": "Talent-Profile.Request.Input"}},
                    {"artifact": {"type": "messageType", "name": "Talent-Profile.Request.Output"}}
                ]
            }
        }
    ],
    "x-artifacts": [
        {
            "name": "Job-Postings.Scan",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Identify job opportunities that match the subject’s skills and preferences.",
            "tags": ["jobs", "opportunity", "matching", "logEvent"],
            "examples": [
                "Scan LinkedIn postings",
                "Identify remote roles",
                "Match consulting opportunities"
            ]
        },
        {
            "name": "Job-Postings.Scan",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Identify job opportunities that match the subject’s skills and preferences.",
            "tags": ["jobs", "opportunity", "matching", "logEvent"],
            "examples": [
                "Scan LinkedIn postings",
                "Identify remote roles",
                "Match consulting opportunities"
            ]
        },
        {
            "name": "Job-Postings.Scan",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Identify job opportunities that match the subject’s skills and preferences.",
            "capabilities": ["scan"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Job-Postings.Scan.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/job-postings.scan.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/job-postings.scan.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Job-Postings.Scan",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
          "name": "Job-Postings.Scan.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/job-postings.scan.input.schema.json"
          },
          "description": "Input schema for the Job-Postings.Scan capability."
        },
        {
          "name": "Job-Postings.Scan.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/job-postings.scan.output.schema.json"
          },
          "description": "Output schema for the Job-Postings.Scan capability."
        },
        {
            "name": "Consulting-Services.Pitch",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Generate and send consulting pitches to prospective clients.",
            "tags": ["consulting", "pitch", "outreach", "logEvent"],
            "examples": [
                "Send consulting proposal",
                "Pitch services to vendor",
                "Respond to RFP"
            ]
        },
        {
            "name": "Consulting-Services.Pitch",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Generate and send consulting pitches to prospective clients.",
            "tags": ["consulting", "pitch", "outreach", "logEvent"],
            "examples": [
                "Send consulting proposal",
                "Pitch services to vendor",
                "Respond to RFP"
            ]
        },
        {
            "name": "Consulting-Services.Pitch",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Generate and send consulting pitches to prospective clients.",
            "capabilities": ["pitch"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Consulting-Services.Pitch.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Consulting-Services.Pitch",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
          "name": "Consulting-Services.Pitch.Input",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.input.schema.json"
          },
          "description": "Input schema for the Consulting-Services.Pitch capability."
        },
        {
          "name": "Consulting-Services.Pitch.Output",
          "version": "1.0.0",
          "artifactType": "messageType",
          "schema": {
            "$ref": "https://yo-ai.ai/schemas/consulting-services.pitch.output.schema.json"
          },
          "description": "Output schema for the Consulting-Services.Pitch capability."
        },
        {
            "name": "Application.Submit",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Submit job applications using minimized profile from Data-Steward.",
            "tags": ["application", "submit", "logEvent"],
            "examples": [
                "Apply to job",
                "Submit resume",
                "Send cover letter"
            ]
        },
        {
            "name": "Application.Submit",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Submit job applications using minimized profile from Data-Steward.",
            "tags": ["application", "submit", "logEvent"],
            "examples": [
                "Apply to job",
                "Submit resume",
                "Send cover letter"
            ]
        },
        {
            "name": "Application.Submit",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Submit job applications using minimized profile from Data-Steward.",
            "capabilities": ["submit"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Application.Submit.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/application.submit.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/application.submit.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Application.Submit",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Application.Submit.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": {
              "$ref": "https://yo-ai.ai/schemas/application.submit.input.schema.json"
            },
            "description": "Input schema for the Application.Submit capability."
        },
        {
            "name": "Application.Submit.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": {
              "$ref": "https://yo-ai.ai/schemas/application.submit.output.schema.json"
            },
            "description": "Output schema for the Application.Submit capability."
        },
        {
            "name": "Talent-Profile.Request",
            "version": "1.0.0",
            "artifactType": "skill",
            "description": "Request minimized resume, skills, and professional profile from Data-Steward.",
            "tags": ["requestData", "resume", "skills", "logEvent"],
            "examples": [
                "Request resume bundle",
                "Request skills profile"
            ]
        },
        {
            "name": "Talent-Profile.Request",
            "version": "1.0.0",
            "artifactType": "task",
            "description": "Request minimized resume, skills, and professional profile from Data-Steward.",
            "tags": ["requestData", "resume", "skills", "logEvent"],
            "examples": [
                "Request resume bundle",
                "Request skills profile"
            ]
        },
        {
            "name": "Talent-Profile.Request",
            "version": "1.0.0",
            "artifactType": "tool",
            "description": "Request minimized resume, skills, and professional profile from Data-Steward.",
            "capabilities": ["request"],
            "path": "/",
            "provider": {
                "name": "PrivacyPortfolio",
                "brand": "Yo-ai",
                "product": "",
                "version": "1.0.0",
                "license": "Yo-ai Internal",
                "url": "https://yo-ai.ai/docs/Talent-Profile.Request.html",
                "config": {"backend": ""}
            },
            "inputSchema": { "$ref": "https://yo-ai.ai/schemas/talent-profile.request.input.schema.json" },
            "outputSchema": { "$ref": "https://yo-ai.ai/schemas/talent-profile.request.output.schema.json" },
            "auth": "apiKey"
        },
        {
            "name": "Talent-Profile.Request",
            "version": "1.0.0",
            "artifactType": "handler",
            "description": "Interface for integrating with tool executable.",
            "path": "/"
        },
        {
            "name": "Talent-Profile.Request.Input",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": {
              "$ref": "https://yo-ai.ai/schemas/talent-profile.request.input.schema.json"
            },
            "description": "Input schema for the Talent-Profile.Request capability."
        },
        {
            "name": "Talent-Profile.Request.Output",
            "version": "1.0.0",
            "artifactType": "messageType",
            "schema": {
              "$ref": "https://yo-ai.ai/schemas/talent-profile.request.output.schema.json"
            },
            "description": "Output schema for the Talent-Profile.Request capability."
        }
    ],
    "supportsAuthenticatedExtendedCard": true
}