core/observability/kafka/README.md

Wrapping Kafka-backed Agent Events in a Stream for Streamlit
The core idea is to create a streaming adapter layer that consumes Kafka topics and exposes them as a real-time stream that Streamlit (or similar observer UIs) can consume.

Architecture Overview
Kafka Topics
    │
    ▼
Kafka Consumer (Python)
    │
    ▼
Stream Adapter (SSE / WebSocket / Queue)
    │
    ▼
Streamlit Observer UI


Server-Sent Events (SSE) via FastAPI

SSE is unidirectional (Kafka → UI), matching the read-only observer model
Works natively with st.empty() / st.write_stream() polling loops
No WebSocket handshake complexity
Easily handles multiple topic subscriptions

In-Process Queue (simpler, single-host)
If Streamlit and the Kafka consumer run on the same host, skip HTTP entirely.

Key Design Decisions
Concern                         Recommendation
Multiple observers              SSE bridge (each client gets its own consumer group offset)
Topic filtering per observer    Pass ?topics= as a query param to the SSE endpoint
Replay / history                Store events to a small SQLite/Redis cache in the bridge layer; expose a /history endpoint
Auth                            Add a Bearer token check in the FastAPI middleware
Backpressure                    Use asyncio.Queue with maxsize in the generator to avoid overwhelming slow Streamlit clients