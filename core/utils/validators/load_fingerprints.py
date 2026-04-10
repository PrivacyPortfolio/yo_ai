# # core/utils/validators/load_fingerprints.py
#
# Compute stable fingerprints for agents based on their card and extended card.
#
# Fixes applied (Gap Registry v2, Section 1 + Section 3):
#   - _load_fingerprints() was indented as a class method with no class — moved
#     to module level as load_fingerprints(card, extended)
#   - sorted() called on lists of dicts → TypeError; fixed with key=lambda
#   - Fingerprint verification against registered card was absent — stub added
#   - PLACEHOLDER_COMPUTE_AT_REGISTRATION values bypass verification in dev mode
#
# Called by: BaseAgent.__init__() when slim=False
# Consumed by: Door-Keeper Agent.Register, Agent.Authenticate (verification gap)

import hashlib
import json
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------------
# Internal: stable hash
# ------------------------------------------------------------------
def _stable_hash(value: Any) -> str:
    """
    Produce a deterministic SHA256 hash for any JSON-serializable value.
    Ensures stable ordering for dicts. Lists of dicts sorted by JSON repr.
    """
    normalized = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _sort_list(items: List[Any]) -> List[Any]:
    """
    Sort a list that may contain dicts, strings, or mixed values.
    Dicts are not directly comparable — sort by their stable JSON repr.
    Fixes Gap Registry TypeError: sorted() on lists of dicts.
    """
    if not items:
        return []
    if all(isinstance(i, dict) for i in items):
        return sorted(items, key=lambda d: json.dumps(d, sort_keys=True, separators=(",", ":")))
    if all(isinstance(i, str) for i in items):
        return sorted(items)
    # Mixed: sort by repr as fallback
    return sorted(items, key=lambda i: json.dumps(i, sort_keys=True, default=str))


# ------------------------------------------------------------------
# Public: compute fingerprints
# ------------------------------------------------------------------
def load_fingerprints(card: Optional[Dict], extended: Optional[Dict]) -> Dict[str, Any]:
    """
    Compute stable, deterministic fingerprints for an agent based on
    its public card and extended card.

    Fingerprint surfaces:
        identity     — name, version, description, domain
        capabilities — skills / capability declarations
        tools        — tool artifacts (x-artifacts type=tool)
        schemas      — declared message schemas
        routing      — routes surface
        contract     — full merged card (canonical integrity check)

    Returns a structured fingerprint dict. Store this at registration time.
    Compare contract_signature at authentication time to detect card drift.

    Dev mode: if all signatures are PLACEHOLDER_COMPUTE_AT_REGISTRATION,
    verification is bypassed with a warning. Remove before production.
    """

    # Merge card + extended card
    merged_card: Dict[str, Any] = {}
    merged_card.update(card or {})
    if extended:
        merged_card.update(extended)

    # Extract and normalize each surface
    identity_block = {
        "name":        merged_card.get("name"),
        "version":     merged_card.get("version"),
        "description": merged_card.get("description"),
        "domain":      merged_card.get("domain"),
    }

    # Skills in agent cards are dicts — must use _sort_list, not sorted()
    capabilities = _sort_list(merged_card.get("capabilities", []))
    tools        = _sort_list(merged_card.get("tools", []))
    schemas      = _sort_list(merged_card.get("schemas", []))
    routing      = _sort_list(merged_card.get("routes", []))

    # Compute signatures
    identity_signature    = _stable_hash(identity_block)
    capability_signature  = _stable_hash(capabilities)
    tooling_signature     = _stable_hash(tools)
    schema_signature      = _stable_hash(schemas)
    routing_signature     = _stable_hash(routing)
    contract_signature    = _stable_hash(merged_card)

    return {
        "identity_signature":   identity_signature,
        "capability_signature": capability_signature,
        "tooling_signature":    tooling_signature,
        "schema_signature":     schema_signature,
        "routing_signature":    routing_signature,
        "contract_signature":   contract_signature,
        "raw": {
            "identity":     identity_block,
            "capabilities": capabilities,
            "tools":        tools,
            "schemas":      schemas,
            "routes":       routing,
        },
    }


# ------------------------------------------------------------------
# Public: verify fingerprints
# ------------------------------------------------------------------
PLACEHOLDER = "PLACEHOLDER_COMPUTE_AT_REGISTRATION"

def verify_fingerprints(
    computed: Dict[str, Any],
    registered: Dict[str, Any],
    dev_mode: bool = False,
) -> Dict[str, Any]:
    """
    Compare computed fingerprints against the fingerprints stored at
    registration time. Returns a verification result dict.

    Used by Door-Keeper:
        Agent.Register    — stores computed fingerprints as the baseline
        Agent.Authenticate — calls verify_fingerprints() to detect card drift

    Args:
        computed   : Result of load_fingerprints() for the presented card
        registered : Fingerprints stored at registration time
        dev_mode   : If True, PLACEHOLDER values bypass verification with warning

    Returns:
        {
            "verified": bool,
            "drifted_surfaces": [list of surface names that changed],
            "dev_mode_bypass": bool,
            "warnings": [list of warning strings]
        }
    """
    surfaces = [
        "identity_signature",
        "capability_signature",
        "tooling_signature",
        "schema_signature",
        "routing_signature",
        "contract_signature",
    ]

    warnings     = []
    drifted      = []
    dev_bypass   = False

    for surface in surfaces:
        registered_val = registered.get(surface, "")
        computed_val   = computed.get(surface, "")

        # Dev mode: skip PLACEHOLDER values
        if registered_val == PLACEHOLDER:
            if dev_mode:
                dev_bypass = True
                warnings.append(
                    f"{surface}: PLACEHOLDER — verification bypassed (dev_mode=True). "
                    f"Compute and store real fingerprint before production."
                )
                continue
            else:
                # PLACEHOLDER in production is itself a drift signal
                drifted.append(surface)
                warnings.append(
                    f"{surface}: PLACEHOLDER found in registered card — "
                    f"registration was incomplete. Treat as drift."
                )
                continue

        if computed_val != registered_val:
            drifted.append(surface)

    verified = len(drifted) == 0

    return {
        "verified":        verified,
        "drifted_surfaces": drifted,
        "dev_mode_bypass": dev_bypass,
        "warnings":        warnings,
    }
