# agents/door_keeper/capabilities/score_agreements.py
#
# Agreement scoring for trust tier evaluation.
#
# "0 agreements = 0 promises."
# All Yo-ai agents are strongly encouraged to negotiate signed agreements
# with RegisteredAgents and Subscribers. This module counts and scores
# agreements held by any party — Door-Keeper itself, a RegisteredAgent
# presenting for authentication, or a Subscriber registering on the platform.
#
# Agreement artifacts live in:
#   agents/<agent_name>/agreements/   (agent's own agreements)
#   shared/agreements/                (platform-level agreements)
#
# Agreement files are JSON artifacts matching the agreement-template shape:
#   {
#     "event":          "data_processing_agreement",
#     "timestamp":      "2025-12-18T08:25:00Z",
#     "subscriberId":   "sub-456",
#     "approvedSkills": ["Log-Event"],
#     "conditions":     { "scope": "...", "logging": "...", "expiry": "..." },
#     "issuedBy":       "Data-Steward Agent",
#     "proxy":          "Vendor-Manager Agent"
#   }
#
# Scoring model:
#   0 agreements        → score 0.0  — no promises, no trust contribution
#   1 agreement         → score 0.3  — minimal commitment
#   2 agreements        → score 0.5  — baseline
#   3–4 agreements      → score 0.7  — established
#   5+ agreements       → score 0.9  — well-governed
#
#   Deductions:
#     expired agreement         → -0.1 per expired (broken promise)
#     missing required fields   → -0.05 per malformed artifact
#
#   Score is clamped to [0.0, 1.0]
#
# Called by: trust_assign.py
# See also:  agreement-template.py, blocked-communication-detector.py

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")

_AGENTS_ROOT = Path(os.environ.get("YO_AI_AGENTS_ROOT", "agents"))
_AGREEMENTS_SUBPATH = Path("training") / "artifacts" / "agreements"

_REQUIRED_FIELDS = {"event", "timestamp", "issuedBy"}

_COUNT_SCORES = [
    (0, 0.0),
    (1, 0.3),
    (2, 0.5),
    (4, 0.7),          # 3–4
    (float("inf"), 0.9)  # 5+
]


def score_agreements(
    agent_name: str,
    subject_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Count and score agreements held by an agent or between an agent
    and a specific subject (RegisteredAgent or Subscriber).
    """

    agreements_path = _AGENTS_ROOT / agent_name / _AGREEMENTS_SUBPATH
    agreements = _load_agreements(agreements_path, subject_id)

    valid_count = 0
    expired_count = 0
    malformed_count = 0
    summaries = []
    now = datetime.now(timezone.utc)

    for artifact in agreements:

        # Missing required fields
        missing = _REQUIRED_FIELDS - set(artifact.keys())
        if missing:
            malformed_count += 1
            LOG.debug(
                "Agreement.Malformed",
                payload={
                    "missing_fields": list(missing),
                    "artifact": artifact,
                },
            )
            continue

        # Expiry check
        expiry_str = (artifact.get("conditions") or {}).get("expiry")
        expired = False

        if expiry_str:
            try:
                expiry_dt = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
                if expiry_dt < now:
                    expired = True
                    expired_count += 1
            except ValueError:
                LOG.debug(
                    "Agreement.ExpiryParseFailed",
                    payload={"expiry": expiry_str},
                )

        valid_count += 1
        summaries.append({
            "event": artifact.get("event"),
            "issuedBy": artifact.get("issuedBy"),
            "timestamp": artifact.get("timestamp"),
            "expiry": expiry_str,
            "expired": expired,
            "approvedSkills": artifact.get("approvedSkills", []),
            "proxy": artifact.get("proxy"),
        })

    # Score computation
    base_score = _count_to_score(valid_count)
    deductions = (expired_count * 0.1) + (malformed_count * 0.05)
    score = round(max(0.0, min(1.0, base_score - deductions)), 3)

    rationale = _build_rationale(
        valid_count, expired_count, malformed_count, base_score, deductions, score
    )

    # Final scoring log
    LOG.info(
        "Agreement.ScoreComputed",
        payload={
            "agent": agent_name,
            "subject": subject_id,
            "valid": valid_count,
            "expired": expired_count,
            "malformed": malformed_count,
            "score": score,
        },
    )

    return {
        "agentName": agent_name,
        "subjectId": subject_id,
        "agreementCount": valid_count,
        "expiredCount": expired_count,
        "malformedCount": malformed_count,
        "score": score,
        "scoreRationale": rationale,
        "agreements": summaries,
        "agreementsPath": str(agreements_path),
    }


# ------------------------------------------------------------------
# Internal: agreement loader
# ------------------------------------------------------------------

def _load_agreements(
    base_path: Path,
    subject_id: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Load all .json agreement artifacts from:
      <base_path>/          — agent-level agreements
      <base_path>/<subject_id>/  — subject-specific agreements
    """

    artifacts: List[Dict[str, Any]] = []
    paths_to_scan = [base_path]

    if subject_id:
        paths_to_scan.append(base_path / subject_id)

    for path in paths_to_scan:
        if not path.exists() or not path.is_dir():
            LOG.debug(
                "Agreement.PathMissing",
                payload={"path": str(path)},
            )
            continue

        for file in path.glob("*.json"):
            try:
                raw = file.read_text(encoding="utf-8", errors="replace")
                data = json.loads(raw)

                if isinstance(data, dict):
                    artifacts.append(data)
                else:
                    LOG.debug(
                        "Agreement.NonDictJSON",
                        payload={"file": str(file)},
                    )

            except Exception as exc:
                LOG.warning(
                    "Agreement.JSONParseFailed",
                    payload={"file": str(file), "error": str(exc)},
                )

    return artifacts


# ------------------------------------------------------------------
# Internal: scoring helpers
# ------------------------------------------------------------------

def _count_to_score(count: int) -> float:
    """Map agreement count to base score using threshold table."""
    prev_score = 0.0
    for threshold, score in _COUNT_SCORES:
        if count <= threshold:
            return score
        prev_score = score
    return prev_score


def _build_rationale(
    valid: int,
    expired: int,
    malformed: int,
    base: float,
    deductions: float,
    final: float,
) -> str:
    parts = []

    if valid == 0:
        parts.append("No agreements found — 0 promises made.")
    else:
        parts.append(f"{valid} valid agreement(s) found (base score {base:.2f}).")

    if expired:
        parts.append(
            f"{expired} expired agreement(s) — broken promises deducted "
            f"({expired} × 0.10 = -{expired * 0.1:.2f})."
        )
    if malformed:
        parts.append(
            f"{malformed} malformed artifact(s) — missing required fields "
            f"({malformed} × 0.05 = -{malformed * 0.05:.2f})."
        )
    if deductions:
        parts.append(f"Final score after deductions: {final:.3f}.")

    return " ".join(parts)
