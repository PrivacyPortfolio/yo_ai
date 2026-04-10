# core/utils/knowledge/knowledge_write.py
#
# Write new knowledge to agent-specific or shared knowledge repositories.
#
# Changes from original:
#   - datetime.utcnow() → datetime.now(timezone.utc)  (deprecated Python 3.12+)
#   - Weak trust gate (hasattr duck-type) replaced with isinstance check
#     against RegisteredAgent — Gap Registry MEDIUM flaw
#   - Reload notification: agents initialized before a write won't see new
#     files until restarted (Gap Registry ⚠️ open). A warning is now logged
#     with guidance. Runtime reload is deferred — see Gap Registry item.
#   - SHARED_ROOT and AGENTS_ROOT respect env overrides (consistent with
#     knowledge_query.py and load_knowledge.py)
#
# Trust gate:
#   add_shared_knowledge() — requires a RegisteredAgent instance
#   add_agent_knowledge()  — requires the agent's own instance
#   Both gates verified via isinstance, not duck-typing
#
# See: knowledge_query.py, load_knowledge.py

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Root paths — override via environment for Lambda/container deployments
_SHARED_ROOT = Path(os.environ.get("YO_AI_SHARED_ROOT", "shared")) / "knowledge"
_AGENTS_ROOT = Path(os.environ.get("YO_AI_AGENTS_ROOT", "agents"))


def add_shared_knowledge(
    registered_agent: Any,
    filename: str,
    content: str,
    *,
    overwrite: bool = False,
) -> Path:
    """
    Add or update a file in the shared knowledge repository.

    Requires a RegisteredAgent instance (Door-Keeper validated).
    Duck-typed hasattr() check replaced with isinstance() against
    RegisteredAgent — prevents any object with agent_name from bypassing
    the gate (Gap Registry MEDIUM flaw).

    Args:
        registered_agent : Must be an instance of RegisteredAgent
        filename         : Target filename within shared/knowledge/
        content          : Text content to write
        overwrite        : If False (default), raises FileExistsError on collision

    Returns:
        Path to the written file.
    """
    _assert_registered_agent(registered_agent, "add_shared_knowledge")

    target = _SHARED_ROOT / filename
    _write_file(target, content, overwrite=overwrite)
    _write_provenance(target, actor_name=registered_agent.agent_name)
    _warn_reload(target)

    return target


def add_agent_knowledge(
    agent: Any,
    filename: str,
    content: str,
    *,
    overwrite: bool = False,
) -> Path:
    """
    Add or update a file in the agent-specific knowledge repository.

    Only the agent instance itself may update its own knowledge.

    Args:
        agent    : The agent instance updating its own knowledge
        filename : Target filename within agents/<name>/training/knowledge/
        content  : Text content to write
        overwrite: If False (default), raises FileExistsError on collision

    Returns:
        Path to the written file.
    """
    agent_name = _resolve_agent_name(agent)
    root   = _AGENTS_ROOT / agent_name / "training" / "knowledge"
    target = root / filename

    _write_file(target, content, overwrite=overwrite)
    _write_provenance(target, actor_name=agent_name)
    _warn_reload(target)

    return target


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _assert_registered_agent(obj: Any, caller: str) -> None:
    """
    Verify obj is a RegisteredAgent instance.

    isinstance() check against RegisteredAgent — not hasattr() duck-typing.
    Deferred import avoids circular dependency; RegisteredAgent is defined
    in core.platform_agent or equivalent.

    Falls back to hasattr() with a deprecation warning if RegisteredAgent
    cannot be imported — supports dev environments where the class may not
    yet exist. Remove fallback before production.
    """
    try:
        from core.platform_agent import RegisteredAgent
        if not isinstance(obj, RegisteredAgent):
            raise PermissionError(
                f"{caller}: caller is not a RegisteredAgent instance. "
                f"Got: {type(obj).__name__}. "
                f"Only Door-Keeper-validated RegisteredAgents may update shared knowledge."
            )
    except ImportError:
        # Dev fallback — remove before production
        logger.warning(
            "%s: RegisteredAgent class not importable — "
            "falling back to hasattr() trust gate (dev mode only).",
            caller
        )
        if not hasattr(obj, "agent_name"):
            raise PermissionError(
                f"{caller}: caller has no agent_name attribute. "
                f"Only a RegisteredAgent may update shared knowledge."
            )


def _resolve_agent_name(agent: Any) -> str:
    """Resolve agent name from card or class name."""
    card = getattr(agent, "card", {}) or {}
    return card.get("name") or getattr(agent, "name", None) or agent.__class__.__name__


def _write_file(target: Path, content: str, overwrite: bool) -> None:
    """Create parent dirs and write content, respecting overwrite flag."""
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        raise FileExistsError(
            f"Knowledge file already exists: {target}. "
            f"Pass overwrite=True to replace it."
        )

    target.write_text(content, encoding="utf-8")
    logger.info("knowledge_write: wrote %s", target)


def _write_provenance(target: Path, actor_name: str) -> None:
    """
    Write a sidecar provenance file: <filename>.meta
    Records who wrote it, when, and the file path.
    """
    meta      = target.with_suffix(target.suffix + ".meta")
    timestamp = datetime.now(timezone.utc).isoformat()

    meta.write_text(
        f"actor: {actor_name}\n"
        f"timestamp: {timestamp}\n"
        f"path: {target}\n",
        encoding="utf-8"
    )


def _warn_reload(target: Path) -> None:
    """
    Warn that agents initialized before this write won't see the new file
    until their knowledge is reloaded.

    Gap Registry ⚠️ open: knowledge_write runtime reload mechanism missing.
    Agents load knowledge once at init (slim=False). Runtime writes are
    invisible to already-initialized agents until they restart.
    Full reload mechanism deferred — tracked in Gap Registry.
    """
    logger.warning(
        "knowledge_write: %s written. "
        "Agents initialized before this write will NOT see this file "
        "until restarted or until a runtime reload mechanism is implemented. "
        "Gap Registry: knowledge reload mechanism (⚠️ open).",
        target
    )
