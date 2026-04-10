/**
 * Yo-ai-agents-doc.md is the documentationURL for https://privacyportfolio.com/.well-known/agent.json,
 * which contains documentation for:
 * - discovering Yo-ai agents
 * - registering Yo-ai agents
 * - detecting Yo-ai agents
 * - blocking Yo-ai agents
 * - resolving disputes against Yo-ai agents
 * - terms and requirements for using Yo-ai agents
 * - best practices for using Yo-ai agents
 * - additional resources
 */

/**  NOTE: PrivacyPortfolio.com is the business domain for Yo-ai.ai the AI Assurance Platform domain  */

/**  Discovering Yo-ai agents  */
Use https://privacyportfolio.com/.well-known/agent.json to find links to agent cards for all proprietary agents registered on the Yo-ai platform.


/**  Registering A2A-enabled agents  */
All agents that interact with Yo-ai agents MUST register with PrivacyPortfolio by:
1.  emailing registrar with the contact information of a Responsible Human
2.  creating an account for authentication and on-boarding
3.  completing an agent-readiness test to verify A2A capabilities documented in agent cards.


/**  Detecting Yo-ai agents  */
All Yo-ai agents attempt to "leave their calling card" when accessing resources, such as submitting forms, setting cookie values, or getting web pages. Although most agent activity occurs via authenticated API calls, sometimes it's helpful to identify agent activity in weblogs, ticketing systems, etc. Yo-ai agents are designed to be detectable for your security and to protect PrivacyPortfolio from false allegations.


/**  Blocking Yo-ai agents  */
Yo-ai agents always scan for other A2A cards at https://$domain/.well-known/agent.json, which can be detected in the weblogs of your organization's website and blocked if desired.


/**  Resolving disputes against Yo-ai agents  */
In the event that you or your organization has a dispute with Yo-ai agents, please do one of the following:
1. Email responsible-human@privacyportfolio.com with your complaint.
2. Contact JAMS or TRUSTe to lodge your complaint to arbitrate a resolution.
3. Notify the California OAG or the CPPA that you've lodged a complaint against PrivacyPortfolio.
PrivacyPortfolio WILL attempt to directly contact the person lodging a complaint to attempt a mutually-acceptable resolution. 

/**  Terms and requirements for using Yo-ai agents  */
Yo-ai agents always present Terms and Requirements to other A2A-enabled agents:
1. Prior to Registering A2A-enabled agents
2. Prior to initiating each financial transaction
Terms and requirements can vary between PrivacyPortfolio and each organization depending on risk exposure and current capabilities.
Each Terms and Requirements agreement is governed by PrivacyPortfolio's Responsible AI Policy, which is posted at:
https://privacyportfolio.com/AI-Policy.html. 

/**  Best practices for using Yo-ai agents  */
At this time, considering the current state-of-the-art with implementing the A2A Protocol, best practices are "under development".
Issues which best practices are designed to mitigate will be published in this document when they become available to test and monitor. 

/**  Additional resources  */
https://www.yo-ai.ai is the AI Assurance Platform for Consumers and Organizations where additional program and technical information can be found.
https://github.com/craigericksondpo/Yo-ai is the code repository where public-facing documentation and open source code can be accessed.