# This script handles log shipping to Kafka topics for Yo-ai platform agents, registered agents, and subscribers.
# It ensures that logs are sent to the appropriate Kafka topics based on the type of agent or subscriber.
# It also manages the lifecycle of the log shipping process, including startup and shutdown procedures,
# and redacts sensitive information from log entries published to Kafka topics.
