# observer_app.py
import streamlit as st
import requests, json, time

st.set_page_config(page_title="Agent Observer", layout="wide")
st.title("🔍 Agent Conversation Stream")

BRIDGE_URL = "http://localhost:8000/stream?topics=agent-chat,agent-actions"

# Maintain message history across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

feed = st.container()
status = st.sidebar.empty()

def render_event(event: dict):
    value = event["value"]
    agent_id = value.get("agent_id", "unknown")
    role = value.get("role", "agent")
    content = value.get("content", "")
    topic = event["topic"]

    with feed:
        with st.chat_message(role):
            st.caption(f"`{agent_id}` via `{topic}`")
            st.markdown(content)

# Polling loop — runs on each Streamlit script execution
placeholder = st.empty()
with requests.get(BRIDGE_URL, stream=True, timeout=60) as resp:
    for raw_line in resp.iter_lines():
        if raw_line and raw_line.startswith(b"data: "):
            event = json.loads(raw_line[6:])
            st.session_state.messages.append(event)
            render_event(event)
            status.metric("Events received", len(st.session_state.messages))