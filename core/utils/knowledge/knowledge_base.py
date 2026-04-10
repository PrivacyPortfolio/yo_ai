# core/utils/knowledge/knowledge_base.py
#
# Virtual corpus wrapper for the Yo-ai knowledge system.
#
# Design intent: R-style virtual corpus.
#   The KnowledgeBase holds an index of what exists — not the content itself.
#   tree-files.txt is the preferred index source: a Windows `tree` output
#   that maps the training folder structure without loading any file content.
#   Content is materialized on demand by query() and get_playbook().
#
# This means:
#   - Agent init is fast — only the manifest is read, not every document
#   - Large .docx training files don't load until a relevant capability invokes them
#   - The corpus can be arbitrarily large without affecting cold start time
#   - The embedding/search seam is cleanly separated from the loading seam
#
# Relationship to other knowledge files:
#   load_knowledge.py  — constructs KnowledgeBase from tree-files.txt or filesystem
#   knowledge_query.py — external API; delegates to KnowledgeBase.query()
#   knowledge_write.py — writes new files; KnowledgeBase.reload() refreshes the index
#
# Embedding/search seam:
#   _embed_documents() and _semantic_search() are stubs.
#   Plug in sentence-transformers, OpenAI embeddings, or cosine similarity
#   at those two methods without changing anything else.

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Result limits — keep LLM context window manageable
_MAX_FRAGMENTS      = 5
_MAX_FRAGMENT_CHARS = 1200
_MAX_TOTAL_CHARS    = 4000


class KnowledgeBase:
    """
    Virtual corpus for an agent's knowledge repository.

    Holds a manifest of available documents (from tree-files.txt or
    filesystem scan) and materializes content on demand.

    Construction:
        KnowledgeBase.from_tree_file(tree_file_path, root_path)
        KnowledgeBase.from_filesystem(root_path)
        KnowledgeBase(documents={...})   # direct, for testing

    Args:
        documents: Optional pre-loaded dict {relative_path: content}.
                   Used when content is already available (test harness,
                   small corpora where eager load is acceptable).
    """

    def __init__(self, documents: Dict[str, str] | None = None):
        # Pre-loaded content — used for direct construction and testing
        self._documents: Dict[str, str] = documents or {}

        # Manifest: relative_path → absolute Path on disk
        # Populated by from_tree_file() or from_filesystem()
        self._manifest: Dict[str, Path] = {}

        # Root path — needed to resolve manifest entries to real files
        self._root: Optional[Path] = None

        # Embedding index — stub, replaced by real embeddings when ready
        self._index = self._embed_documents(self._documents)

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_tree_file(cls, tree_file: Path, root: Path) -> "KnowledgeBase":
        """
        Build a KnowledgeBase index from a tree-files.txt manifest.

        Parses the Windows `tree` output to extract file paths relative
        to root. No file content is loaded — the manifest is the index.
        Content is materialized on demand by query() and get_playbook().

        Args:
            tree_file : Path to tree-files.txt
            root      : The root directory tree-files.txt describes
        """
        kb = cls()
        kb._root = root
        kb._manifest = _parse_tree_manifest(tree_file, root)
        logger.info(
            "KnowledgeBase: indexed %d file(s) from %s",
            len(kb._manifest), tree_file
        )
        return kb

    @classmethod
    def from_filesystem(cls, root: Path) -> "KnowledgeBase":
        """
        Build a KnowledgeBase index by scanning the filesystem.

        Used when tree-files.txt is absent. Same result — manifest only,
        content materialized on demand.

        Args:
            root: Directory to scan recursively
        """
        kb = cls()
        kb._root = root
        kb._manifest = {
            str(f.relative_to(root)): f
            for f in root.rglob("*")
            if f.is_file() and not f.suffix.lower() == ".meta"
        }
        logger.info(
            "KnowledgeBase: indexed %d file(s) from filesystem scan of %s",
            len(kb._manifest), root
        )
        return kb

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def query(
        self,
        text: str,
        capability_id: str = "",
        max_fragments: int = _MAX_FRAGMENTS,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge fragments for a query.

        If an embedding index is available (_semantic_search), uses it.
        Otherwise falls back to keyword scoring against materialized content.

        Args:
            text           : Query text (capability ID + payload terms)
            capability_id  : Optional — used to weight capability-specific files
            max_fragments  : Maximum number of fragments to return

        Returns:
            List of fragment dicts:
            {
                "source":    str,   # relative path
                "relevance": float, # 0.0–1.0
                "content":   str,   # truncated text
            }
            Sorted by relevance descending. Returns [] on failure.
        """
        try:
            # If embeddings are real, delegate to semantic search
            if self._has_real_embeddings():
                result = self._semantic_search(text)
                return [{"source": "semantic", "relevance": 1.0, "content": result}] if result else []

            # Keyword fallback: materialize candidates and score them
            return self._keyword_query(text, capability_id, max_fragments)

        except Exception as exc:
            logger.warning("KnowledgeBase.query: failed — %s", exc)
            return []

    def get_playbook(self, name: str) -> Optional[str]:
        """
        Retrieve a specific named document by relative path or filename stem.

        Checks pre-loaded documents first, then resolves from manifest.

        Args:
            name: Relative path (e.g. "policies/Yo-ai-agent-authorization.txt")
                  or filename stem (e.g. "Yo-ai-agent-authorization")
        """
        # Pre-loaded documents (direct construction)
        if name in self._documents:
            return self._documents[name]

        # Exact manifest match
        if name in self._manifest:
            return _read_file(self._manifest[name])

        # Stem match — find first file whose stem matches
        for rel_path, abs_path in self._manifest.items():
            if Path(rel_path).stem == name or Path(rel_path).name == name:
                return _read_file(abs_path)

        logger.debug("KnowledgeBase.get_playbook: '%s' not found in manifest", name)
        return None

    def list_documents(self) -> List[str]:
        """Return all relative paths in the index."""
        if self._manifest:
            return list(self._manifest.keys())
        return list(self._documents.keys())

    def reload(self) -> None:
        """
        Refresh the index after knowledge_write.py adds new files.
        Rescans the filesystem from self._root if available.
        """
        if self._root and self._root.exists():
            self._manifest = {
                str(f.relative_to(self._root)): f
                for f in self._root.rglob("*")
                if f.is_file() and not f.suffix.lower() == ".meta"
            }
            logger.info(
                "KnowledgeBase.reload: re-indexed %d file(s) from %s",
                len(self._manifest), self._root
            )
        else:
            logger.warning("KnowledgeBase.reload: no root path set — cannot reload.")

    # ------------------------------------------------------------------
    # Embedding / search seam (stub — plug in real implementation here)
    # ------------------------------------------------------------------

    def _embed_documents(self, documents: Dict[str, str]) -> Any:
        """
        Build embedding index from pre-loaded documents.

        Stub — replace with:
            sentence-transformers, OpenAI embeddings, FAISS, etc.
        When using the manifest-based corpus, this is called with {}
        at construction and is effectively a no-op until reload() or
        direct document injection.
        """
        return documents  # placeholder

    def _semantic_search(self, text: str) -> str:
        """
        Search the embedding index.

        Stub — replace with cosine similarity, vector search, etc.
        Current behaviour: returns the first pre-loaded document value.
        """
        return next(iter(self._documents.values()), "")

    def _has_real_embeddings(self) -> bool:
        """
        Returns True if a real embedding index is available.
        Stub always returns False — keyword fallback is used.
        Override or replace when plugging in real embeddings.
        """
        return False

    # ------------------------------------------------------------------
    # Keyword fallback query (used until embeddings are real)
    # ------------------------------------------------------------------

    def _keyword_query(
        self,
        text: str,
        capability_id: str,
        max_fragments: int,
    ) -> List[Dict[str, Any]]:
        """
        Score manifest entries by keyword overlap and materialize the
        top candidates. Content is read from disk only for scored files.
        """
        query_terms = _extract_terms(text + " " + capability_id)
        if not query_terms:
            return []

        candidates = []

        # Score manifest entries by filename relevance first (cheap)
        for rel_path, abs_path in self._manifest.items():
            name_score = _score_name(rel_path, query_terms)
            if name_score > 0:
                candidates.append((name_score, rel_path, abs_path))

        # Sort by name score, take top N*2 to read (avoid reading everything)
        candidates.sort(key=lambda x: -x[0])
        to_read = candidates[:max_fragments * 2]

        # Materialize and re-score by content
        scored = []
        for _, rel_path, abs_path in to_read:
            content = _read_file(abs_path)
            if not content:
                continue
            content_score = _score_content(content, query_terms)
            if content_score > 0:
                scored.append({
                    "source":    rel_path,
                    "relevance": round(content_score, 3),
                    "content":   content,
                })

        scored.sort(key=lambda f: -f["relevance"])

        # Apply character budget
        result     = []
        total_chars = 0
        for frag in scored[:max_fragments]:
            if total_chars >= _MAX_TOTAL_CHARS:
                break
            remaining = _MAX_TOTAL_CHARS - total_chars
            content   = frag["content"][:min(_MAX_FRAGMENT_CHARS, remaining)]
            total_chars += len(content)
            result.append({**frag, "content": content})

        return result


# ---------------------------------------------------------------------------
# tree-files.txt parser
# ---------------------------------------------------------------------------

def _parse_tree_manifest(tree_file: Path, root: Path) -> Dict[str, Path]:
    """
    Parse a Windows `tree /f` output into a {relative_path: abs_path} dict.

    Windows tree output format:
        Folder PATH listing...
        Volume serial number is XXXX-XXXX
        ROOTNAME
           file.txt
        +---subfolder
               nested_file.docx

    Files are indicated by lines that don't start with `+---`.
    Folders are indicated by `+---name` lines.
    Indentation determines depth.
    """
    manifest: Dict[str, Path] = {}

    try:
        text  = tree_file.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
    except Exception as exc:
        logger.warning("KnowledgeBase: could not read tree-files.txt — %s", exc)
        return manifest

    folder_stack: List[str] = []   # current folder path components
    current_depth = 0

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue

        # Skip header lines
        if any(stripped.startswith(h) for h in (
            "Folder PATH", "Volume serial", "Volume in drive"
        )):
            continue

        # Folder line: contains +---
        if "+---" in stripped:
            # Depth determined by position of +--- in line
            depth = stripped.index("+---") // 4  # 4 spaces per indent level
            folder_name = stripped.split("+---", 1)[1].strip()

            # Trim stack to current depth
            folder_stack = folder_stack[:depth]
            folder_stack.append(folder_name)
            current_depth = depth + 1
            continue

        # File line: indented, no +---, has an extension or is a known file
        # Skip lines that are just the root folder name (no dots, short)
        if "." in stripped or stripped.strip() in ("__init__.py", "tree-files.txt"):
            filename = stripped.strip()
            if filename and not filename.startswith("+"):
                rel_path = "/".join(folder_stack + [filename]) if folder_stack else filename
                abs_path = root / Path(rel_path.replace("/", os.sep if hasattr(__builtins__, '__import__') else "/"))

                # Only add to manifest if file actually exists on disk
                candidate = root / Path(*rel_path.split("/"))
                if candidate.exists():
                    manifest[rel_path] = candidate
                else:
                    # File listed in tree but not on disk — record path anyway
                    # so get_playbook() can inform the caller it's missing
                    logger.debug(
                        "KnowledgeBase: tree entry not on disk: %s", rel_path
                    )

    return manifest


# ---------------------------------------------------------------------------
# File reading helpers
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> Optional[str]:
    """Read a file to plain text. Supports .txt, .md, .json, .docx."""
    if not path or not path.exists():
        return None

    suffix = path.suffix.lower()

    try:
        if suffix in (".txt", ".md"):
            return path.read_text(encoding="utf-8", errors="replace")

        if suffix == ".json":
            raw  = path.read_text(encoding="utf-8", errors="replace")
            data = json.loads(raw)
            return _flatten_json(data)

        if suffix == ".docx":
            return _read_docx(path)

        # Other text-like files
        return path.read_text(encoding="utf-8", errors="replace")

    except Exception as exc:
        logger.debug("KnowledgeBase._read_file: could not read %s — %s", path, exc)
        return None


def _read_docx(path: Path) -> Optional[str]:
    """Extract plain text via pandoc. Returns None if pandoc unavailable."""
    try:
        result = subprocess.run(
            ["pandoc", str(path), "-t", "plain", "--wrap=none"],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _flatten_json(obj: Any, prefix: str = "") -> str:
    """Flatten JSON to readable key: value lines for keyword matching."""
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            lines.append(_flatten_json(v, prefix=key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            lines.append(_flatten_json(v, prefix=f"{prefix}[{i}]"))
    else:
        lines.append(f"{prefix}: {obj}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Keyword scoring helpers
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "is",
    "it", "this", "that", "with", "true", "false", "none", "null",
    "stub", "id", "type", "txt", "md", "json", "docx", "py",
}

import os
import re


def _extract_terms(text: str) -> List[str]:
    """Extract meaningful lowercase tokens from query text."""
    # Split on dot, camelCase boundaries, spaces, underscores
    tokens = re.sub(r"([A-Z])", r" \1", text).lower().split()
    tokens = re.sub(r"[._\-/]", " ", " ".join(tokens)).split()
    seen, unique = set(), []
    for t in tokens:
        if t not in _STOPWORDS and len(t) > 2 and t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def _score_name(rel_path: str, query_terms: List[str]) -> float:
    """Score a file path by how many query terms appear in it."""
    if not query_terms:
        return 0.0
    path_lower = rel_path.lower()
    matched = sum(1 for t in query_terms if t in path_lower)
    return matched / len(query_terms)


def _score_content(content: str, query_terms: List[str]) -> float:
    """Score file content by fraction of query terms present."""
    if not query_terms or not content:
        return 0.0
    content_lower = content.lower()
    matched = sum(1 for t in query_terms if t in content_lower)
    return matched / len(query_terms)
