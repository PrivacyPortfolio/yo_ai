# core/utils/knowledge/load_knowledge.py
#
# Load agent knowledge at initialization — virtual corpus pattern.
#
# Design intent: R-style virtual corpus.
#   At init, build an index of what knowledge exists without loading content.
#   tree-files.txt is the preferred index source — a Windows `tree /f` output
#
#   This keeps agent cold-start fast regardless of training corpus size.
#
# Returns:
#   A MergedKnowledgeBase instance (subclass of KnowledgeBase). Access via:
#     agent.knowledge.query(text, capability_id)
#     agent.knowledge.get_playbook(name)
#     agent.knowledge.list_documents()
#
# Called by: YoAiAgent.__init__() when slim=False

import os
from pathlib import Path
from typing import Any, List

from .knowledge_base import KnowledgeBase
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("load_knowledge")


_SHARED_ROOT = Path(os.environ.get("YO_AI_SHARED_ROOT", "shared")) / "knowledge"
_AGENTS_ROOT = Path(os.environ.get("YO_AI_AGENTS_ROOT", "agents"))
_TREE_MANIFEST = "tree-files.txt"


def load_knowledge(agent: Any) -> "MergedKnowledgeBase":
    agent_name = _resolve_agent_name(agent)
    shared_kb  = _load_directory(_SHARED_ROOT, label="shared")
    agent_kb   = _load_directory(
        _AGENTS_ROOT / agent_name / "training" / "knowledge",
        label=f"agent:{agent_name}",
    )
    return MergedKnowledgeBase(agent_kb=agent_kb, shared_kb=shared_kb, agent_name=agent_name)


def _load_directory(path: Path, label: str) -> KnowledgeBase:
    if not path.exists():
        LOG.debug("load_knowledge: %s path not found: %s", label, path)
        return KnowledgeBase()

    tree_file = path / _TREE_MANIFEST
    if tree_file.exists():
        LOG.info("load_knowledge: %s — using tree-files.txt at %s", label, tree_file)
        return KnowledgeBase.from_tree_file(tree_file, root=path)

    LOG.info("load_knowledge: %s — scanning filesystem at %s", label, path)
    return KnowledgeBase.from_filesystem(root=path)


def _resolve_agent_name(agent: Any) -> str:
    card = getattr(agent, "card", {}) or {}
    return (
        card.get("name")
        or getattr(agent, "name", None)
        or getattr(agent, "actor_name", None)
        or agent.__class__.__name__
    )


class MergedKnowledgeBase(KnowledgeBase):
    """
    Composite KnowledgeBase — agent-specific knowledge first, shared second.
    Exposed as agent.knowledge. Full KnowledgeBase interface preserved.
    """

    def __init__(self, agent_kb: KnowledgeBase, shared_kb: KnowledgeBase, agent_name: str):
        super().__init__()
        self._agent_kb   = agent_kb
        self._shared_kb  = shared_kb
        self._agent_name = agent_name

    def query(self, text: str, capability_id: str = "", max_fragments: int = 5) -> List:
        agent_frags  = self._agent_kb.query(text, capability_id, max_fragments)
        shared_frags = self._shared_kb.query(text, capability_id, max_fragments)
        for f in agent_frags:
            f["scope"] = "agent"
        for f in shared_frags:
            f["scope"] = "shared"
        combined = agent_frags + shared_frags
        combined.sort(key=lambda f: (-f["relevance"], 0 if f["scope"] == "agent" else 1))
        return combined[:max_fragments]

    def get_playbook(self, name: str):
        return self._agent_kb.get_playbook(name) or self._shared_kb.get_playbook(name)

    def list_documents(self) -> List[str]:
        return (
            [f"agent:{p}"  for p in self._agent_kb.list_documents()] +
            [f"shared:{p}" for p in self._shared_kb.list_documents()]
        )

    def reload(self):
        self._agent_kb.reload()
        self._shared_kb.reload()
        LOG.info("load_knowledge: reloaded for agent %s", self._agent_name)
