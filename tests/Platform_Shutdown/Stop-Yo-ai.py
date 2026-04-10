# SHUTDOWN-TEST: 
# The Incident-Responder agent shuts down the whole platform by when it is ordered to do so,
# or when The-Sentinel has issued an alert regarding conditional criteria for shutting down.
# 
# When this happens the first priority is to serialize every in-memory request / task that is currently being processed,
# and maintain state of all tasks and workflows.
# After that, all agents are to be cleanly shutdown, ensuring that no tasks are left hanging.
# The last agent to be shutdown is the Solicitor-General, which will log the shutdown event.
# 
