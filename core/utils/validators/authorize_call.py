# core/utils/validators/authorize_call.py

"""
A2A Call Authorization Module

Checks if a calling agent is authorized to invoke methods on this agent
based on JSON policy files in /policies/
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("authorize_call")

class AuthorizationError(Exception):
    """Raised when an A2A call is not authorized"""
    pass


async def run(envelope: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """
    Check if a specific A2A call is authorized.
    
    Args:
        envelope: The A2A call envelope containing caller info and method
        context: Agent context with paths and configuration
        
    Returns:
        bool: True if authorized, False otherwise
        
    Raises:
        AuthorizationError: If authorization check fails critically
    """
    try:
        # Extract caller information from envelope
        caller_name = envelope.get("caller_agent_name")
        method_name = envelope.get("method_name")
        
        if not caller_name:
            LOG.warning("No caller_agent_name in envelope - denying call")
            return False
        
        # Load the authorization policy
        policy = _load_policy(context)
        
        if not policy:
            LOG.warning("No authorization policy found - applying default deny")
            return False
        
        # Check authorization
        is_authorized = _check_authorization(
            caller_name=caller_name,
            method_name=method_name,
            policy=policy
        )
        
        if is_authorized:
            LOG.info(f"Authorized: {caller_name} -> {method_name}")
        else:
            LOG.warning(f"Denied: {caller_name} -> {method_name}")
        
        return is_authorized
        
    except Exception as e:
        LOG.error(f"Authorization check failed: {e}")
        # Fail closed - deny on error
        return False


def _load_policy(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Load authorization policy from training/policies directory.
    
    Args:
        context: Agent context containing agent_name and training_dir
        
    Returns:
        Dict containing the policy, or None if not found/invalid
    """
    agent_name = context.get("agent_name", "unknown")
    training_dir = Path(context.get("training_dir", "/training"))
    
    policy_dir = training_dir / "policies"
    policy_file = policy_dir / f"{agent_name}-authorization.json"
        
    if not policy_file.exists():
        LOG.warning(f"No policy file found: {policy_file}")
        return None
        
    try:
        with open(policy_file, 'r') as f:
            policy = json.load(f)

        # Validate required fields
        if "allowed_callers" not in policy:
            policy["allowed_callers"] = []
        if "denied_callers" not in policy:
            policy["denied_callers"] = []
        if "default_policy" not in policy:
            policy["default_policy"] = "deny"
        if "method_rules" not in policy:
            policy["method_rules"] = {}
            
        return policy    

    except json.JSONDecodeError as e:
        LOG.error(f"Invalid JSON in policy file {policy_file}: {e}")
        return None
    except Exception as e:
        LOG.error(f"Failed to load policy from {policy_file}: {e}")
        return None


def _check_authorization(
    caller_name: str,
    method_name: Optional[str],
    policy: Dict[str, Any]
) -> bool:
    """
    Check if caller is authorized based on policy.
    
    Priority order:
    1. Explicit deny list (denied_callers)
    2. Method-specific rules (if method provided)
    3. General allowed list (allowed_callers)
    4. Default policy
    """
    
    # 1. Check deny list (highest priority)
    denied = policy.get("denied_callers", [])
    if caller_name in denied:
        return False
    
    # 2. Check method-specific rules
    if method_name:
        method_rules = policy.get("method_rules", {})
        if method_name in method_rules:
            method_policy = method_rules[method_name]
            method_allowed = method_policy.get("allowed_callers", [])
            
            # Wildcard means any caller allowed for this method
            if "*" in method_allowed:
                return True
            
            # Check if caller in method-specific allowed list
            if caller_name in method_allowed:
                return True
            
            # Method has specific rules but caller not listed - deny
            return False
    
    # 3. Check general allowed list
    allowed = policy.get("allowed_callers", [])
    if "*" in allowed:
        return True
    
    if caller_name in allowed:
        return True
    
    # 4. Apply default policy
    default = policy.get("default_policy", "deny")
    return default.lower() == "allow"
