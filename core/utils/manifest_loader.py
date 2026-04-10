# core/utils/manifest_loader.py
#
# Fixes applied:
#   - REQUIRED_FIELDS includes "lifespan" — extended agent cards don't have
#     this field, so loading any extended card raised ValueError. Field list
#     split into REQUIRED_BASIC (public cards) and REQUIRED_EXTENDED.
#     load_manifest() accepts a card_type parameter to select validation.
#   - No YAML support — extended cards are stored as .md files containing
#     a JSON block. Added load_json_from_md() for .md files.
#   - Error messages didn't include the file path — added for debuggability.

import json
from pathlib import Path
from typing import Any, Dict, Literal


class ManifestLoader:
    """
    Loads agent manifests (agent cards) from disk.

    Supports:
      - .json files (pure JSON)
      - .md files containing a JSON block (agent card .md format)

    Card type validation:
      - "basic"    : public A2A card — requires id, name, capabilities
      - "extended" : authenticated extended card — requires name, id, skills
      - "none"     : skip validation entirely
    """

    # Public A2A card required fields
    REQUIRED_BASIC = ["id", "name", "capabilities"]

    # Extended card required fields ("lifespan" not required — extended cards don't have it)
    REQUIRED_EXTENDED = ["name", "id", "skills"]

    @staticmethod
    def load_manifest(
        path: str | Path,
        card_type: Literal["basic", "extended", "none"] = "basic",
    ) -> Dict[str, Any]:
        """
        Load a single agent card from disk.

        Args:
            path      : Path to a .json or .md file
            card_type : Validation level — "basic" | "extended" | "none"

        Returns:
            Parsed card dict.

        Raises:
            FileNotFoundError if the file does not exist.
            ValueError if required fields are missing.
            json.JSONDecodeError if the JSON is malformed.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")

        if path.suffix.lower() == ".md":
            data = ManifestLoader.load_json_from_md(path)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))

        if card_type == "basic":
            required = ManifestLoader.REQUIRED_BASIC
        elif card_type == "extended":
            required = ManifestLoader.REQUIRED_EXTENDED
        else:
            required = []

        for field in required:
            if field not in data:
                raise ValueError(
                    f"Manifest '{path}' missing required field: '{field}'. "
                    f"Required for card_type='{card_type}': {required}"
                )

        return data

    @staticmethod
    def load_json_from_md(path: Path) -> Dict[str, Any]:
        """
        Extract a JSON block from a .md file.

        Agent card .md files contain a JavaScript comment block followed
        by a JSON object. This method strips the comment and parses the JSON.

        Example .md file structure:
            /** ... comment ... */
            {
              "name": "Door-Keeper",
              ...
            }
        """
        text = path.read_text(encoding="utf-8", errors="replace")

        # Strip leading JS block comment if present (/** ... */)
        import re
        text = re.sub(r"/\*\*.*?\*/", "", text, flags=re.DOTALL).strip()

        # Find the first { and parse from there
        brace_pos = text.find("{")
        if brace_pos == -1:
            raise ValueError(f"No JSON object found in '{path}'")

        return json.loads(text[brace_pos:])

    @staticmethod
    def load_all(
        directory: str | Path,
        pattern: str = "*.json",
        card_type: Literal["basic", "extended", "none"] = "basic",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Load all agent cards from a directory.

        Args:
            directory : Directory to search
            pattern   : Glob pattern (default: "*.json"; use "*.md" for extended cards)
            card_type : Validation level applied to each file

        Returns:
            Dict keyed by card "id" field.
            Files that fail to load are skipped with a warning printed to stdout.
        """
        import logging
        logger = logging.getLogger(__name__)

        directory  = Path(directory)
        manifests  = {}

        for file in sorted(directory.glob(pattern)):
            try:
                manifest = ManifestLoader.load_manifest(file, card_type=card_type)
                card_id  = manifest.get("id") or manifest.get("name", str(file))
                manifests[card_id] = manifest
            except Exception as exc:
                logger.warning("ManifestLoader: skipping '%s' — %s", file, exc)

        return manifests
