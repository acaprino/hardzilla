"""
Extension domain entity.
"""
from dataclasses import dataclass


@dataclass
class Extension:
    """Represents a Firefox extension available for installation."""
    extension_id: str
    name: str
    description: str
    install_url: str
    breakage_risk: int  # 0-10 scale
    size_mb: float
    icon: str
