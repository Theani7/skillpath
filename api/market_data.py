import copy
from typing import Any, Dict, Optional

from api.seed_data import get_industry_trends, get_market_role_aliases


def get_market_trends_for_role(role: Optional[str]) -> Dict[str, Any]:
    """Get market trends for a role from cache."""
    industry_trends = get_industry_trends()
    mapped_role = _normalize_role(role)
    return copy.deepcopy(industry_trends.get(mapped_role, industry_trends.get("General", {})))


def _normalize_role(role: Optional[str]) -> str:
    """Normalize role name to match industry trends keys."""
    if not role or role == "Unknown":
        return "General"
    
    industry_trends = get_industry_trends()
    role_aliases = get_market_role_aliases()
    
    cleaned = role.strip()
    if cleaned in industry_trends:
        return cleaned
    alias = role_aliases.get(cleaned.lower())
    if alias:
        return alias
    return "General"
