from pydantic import BaseModel
from typing import Dict, Any, Optional

class ScanRequest(BaseModel):
    text: str
    category: str = "user"
    evolve: bool = False
    transaction: Optional[Dict[str, Any]] = None

class ThreatMineRequest(BaseModel):
    fraud_pattern: str
    genai_capability: str
    payment_vulnerability: str
