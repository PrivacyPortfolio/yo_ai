# shared_queue.py
import queue, threading
from confluent_kafka import Consumer

_event_queue: queue.Queue = queue.Queue(maxsize=1000)

def start_consumer(topics: list[str]):
    def _run():
        c = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "streamlit-obs",
            "auto.offset.reset": "latest",
        })
        c.subscribe(topics)
        while True:
            msg = c.poll(0.1)
            if msg and not msg.error():
                _event_queue.put({
                    "topic": msg.topic(),
                    "value": json.loads(msg.value())
                })
    threading.Thread(target=_run, daemon=True).start()

# In your Streamlit app:
# start_consumer(["agent-chat"])
# while True:
#     event = _event_queue.get()
#     st.chat_message(...) + st.rerun()