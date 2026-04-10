/**
 * The-Oracle AgentCard conveys:
 * - Overall details (version, name, description, uses)
 * - Skills: A set of capabilities the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements (internal ONLY)
 */

/**
* The-Oracle AgentCard¶
*/
{
    "name": "The-Oracle",
    "description": "",
    "url":   "https://privacyportfolio.com/agent-registry/the-oracle/agent.json",
    "provider": {
        "organization": "PrivacyPortfolio",
        "url": "https://privacyportfolio.com"
    },
    "iconUrl": "https://privacyportfolio.com/agent-registry/the-oracle/the-oracle-agent-icon.png",
    "version": "1.0.0",
    "documentationUrl": "https://privacyportfolio.com/agent-registry/the-oracle/The-Oracle-AgentCard.md",
    "capabilities": {
        "streaming": true,
        "pushNotifications": true,
        "stateTransitionHistory": false
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
        {
            "name": "_call_llm_forecasting",
            "description": "Core forecasting logic.",
            "tags": [""],
            "examples": ["Tell me when I'll run out of LLM credits."],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "llm_prompt" },
            "outputSchema": { "llm_response" }
        },
        {
            "name": "learn_from_outcome",
            "description": "Store the delta between forecast and outcome.",
            "tags": [""],
            "examples": [""],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "inputSchema": { "llm_prompt" },
            "outputSchema": { 
              record = {
                "forecastId": forecast_id,
                "actualOutcome": actual_outcome,
                "metadata": metadata
        }
    ],
  "supportsAuthenticatedExtendedCard": false
}