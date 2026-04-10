# 4. data.world publishing workflow
# At a high level:
# 1.	Authoritative store: CommunicationEvents live in your audit/event store.
# 2.	Materialized view: A periodic job (or on event trigger) builds a denormalized table tailored for public reporting.
# 3.	data.world sync: 
#    o	Use their API to: 
#       	create or update a dataset
#       	upload/replace a CSV or JSONL file
#       	optionally maintain partitions by year/month.
#       Conceptual steps:
# •	Extract: query all CommunicationEvents (or incremental by timestamp).
# •	Transform: map into ActivityLog columns (e.g., org, status, risk_band, dates, etc.).
# •	Load: call data.world API with the resulting CSV.
# Sketch:

import csv
import io
import requests
from datetime import datetime, timezone

DATAWORLD_API_TOKEN = "DW_API_TOKEN"
DATAWORLD_OWNER = "privacyportfolio"
DATAWORLD_DATASET = "activity-log"


def build_activitylog_rows(events: list[dict]) -> list[dict]:
    rows = []
    for ev in events:
        rows.append({
            "organization": ev["organization"],
            "channel": ev["channel"],
            "direction": ev["direction"],
            "request_type": ev.get("request_type"),
            "status": ev.get("status"),
            "timestamp": ev["timestamp"],
            "risk_score": ev["risk_score"],
            "behavioral_risk_band": ev["behavioral_risk_band"],
            "representative_identity": ev["representative_identity"],
            "representative_name": ev.get("representative_name"),
            "response_time_hours": ev.get("response_time_hours"),
            "flow_type": ev.get("flow_type"),
            "content_hash": ev["content_hash"],
            "raw_content_location": ev["raw_content_location"],
            "summary": ev.get("summary"),
        })
    return rows


def rows_to_csv_bytes(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    if not rows:
        return b""
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def upload_to_dataworld(csv_bytes: bytes, filename: str):
    url = f"https://api.data.world/v0/uploads/{DATAWORLD_OWNER}/{DATAWORLD_DATASET}/files/{filename}"
    headers = {
        "Authorization": f"Bearer {DATAWORLD_API_TOKEN}",
        "Content-Type": "text/csv"
    }
    resp = requests.put(url, headers=headers, data=csv_bytes)
    resp.raise_for_status()


async def sync_activitylog_to_dataworld(events_repo):
    since = ...  # last sync timestamp
    events = await events_repo.query_since(since)
    rows = build_activitylog_rows(events)
    csv_bytes = rows_to_csv_bytes(rows)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"activitylog_{ts}.csv"
    upload_to_dataworld(csv_bytes, filename)

# You can either overwrite a canonical file or append timestamped snapshots.
