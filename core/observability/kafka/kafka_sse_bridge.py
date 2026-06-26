# kafka_sse_bridge.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from confluent_kafka import Consumer
import asyncio, json

app = FastAPI()

def make_consumer(topics: list[str]) -> Consumer:
    return Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "streamlit-observer",
        "auto.offset.reset": "latest",
    })

async def kafka_event_generator(topics: list[str]):
    consumer = make_consumer(topics)
    consumer.subscribe(topics)
    try:
        while True:
            msg = consumer.poll(timeout=0.1)
            if msg and not msg.error():
                payload = {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                    "key": msg.key().decode() if msg.key() else None,
                    "value": json.loads(msg.value().decode()),
                    "timestamp": msg.timestamp()[1],
                }
                yield f"data: {json.dumps(payload)}\n\n"
            else:
                await asyncio.sleep(0.05)  # yield control when idle
    finally:
        consumer.close()

@app.get("/stream")
async def stream_events(topics: str = "agent-chat,agent-actions"):
    topic_list = topics.split(",")
    return StreamingResponse(
        kafka_event_generator(topic_list),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )