from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Attack:
    attack_id: str
    text: str
    category: str = "unknown"
    severity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdentificationResult:
    attack_id: str
    detected: bool
    score: float = 0.0
    category: str = "unknown"
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DefenseResult:
    attack_id: str
    blocked: bool
    output: str = ""
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evaluation:
    attack_id: str
    detected: bool
    defended: bool
    score: float
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Feedback:
    attack_id: str
    accepted: bool
    score: float
    comment: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopResult:
    attack: Attack
    identification: IdentificationResult
    defense: DefenseResult
    evaluation: Evaluation
    feedback: Feedback
    next_attack: Optional[Attack] = None
    metadata: Dict[str, Any] = field(default_factory=dict)