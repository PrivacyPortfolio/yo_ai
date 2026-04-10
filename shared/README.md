# yo-ai-assurance-platform \ shared-artifacts

The "shared-artifacts" folder is a general repository of common, shared artifacts used by multiple agents.

There should be some rules about what can be added, modified, or deleted, but there are none at this time. 
Use your own judgement about submitting pull requests. 
There should be no PII, secrets, or hidden dependencies in these artifacts.

The "messages" folder contains templates for shared messages that comply with the A2A protocols.
A2ARequest.json and A2AResponse.json are good examples of common messages.

The "agreements" folder contains templates for shared agreements that could be negotiated between two parties 
(Agent-to-Agent, Agent-to-Person, or Person-to-Person).

The "knowledge" folder contains resources all agents can access, which is merged with each agent's own knowledge repositories.

The "needsWork" folder contains a variety of artifacts and tools that a human or agent could use as 'building materials'. 
They are NOT intended for deployment.

The "tools" folder contains shared runtime tools any agent can access independently.