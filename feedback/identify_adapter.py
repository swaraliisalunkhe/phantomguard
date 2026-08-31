from typing import Any, Dict, Optional


class IdentifyAdapter:
    """
    Adapter for PhantomGuard Member 1.

    Member 1 exposes ThreatMiner.mine_threat(), which generates an
    AttackHypothesis rather than directly classifying arbitrary text.

    This adapter therefore supports:
      1. An existing identify callable, if supplied.
      2. A ThreatMiner instance, when threat-mining inputs are supplied.
      3. A lightweight signal-based fallback for web-app text scanning.
    """

    def __init__(
        self,
        identify_fn=None,
        threat_miner=None,
    ):
        self.identify_fn = identify_fn
        self.threat_miner = threat_miner

    def run(
        self,
        text: str,
        attack_id: Optional[str] = None,
        fraud_pattern: Optional[str] = None,
        genai_capability: Optional[str] = None,
        payment_vulnerability: Optional[str] = None,
    ) -> Dict[str, Any]:

        # Use an explicitly supplied identification function first.
        if self.identify_fn is not None:
            result = self.identify_fn(text)

            if isinstance(result, dict):
                return result

            return {
                "detected": bool(result),
                "score": 1.0 if result else 0.0,
                "raw": result,
                "source": "identify_fn",
            }

        # Use Member 1 ThreatMiner when complete threat-mining
        # information is available.
        if (
            self.threat_miner is not None
            and fraud_pattern
            and genai_capability
            and payment_vulnerability
        ):
            attack = self.threat_miner.mine_threat(
                fraud_pattern=fraud_pattern,
                genai_capability=genai_capability,
                payment_vulnerability=payment_vulnerability,
            )

            return {
                "detected": True,
                "score": min(
                    1.0,
                    float(getattr(attack, "risk_score", 0.0)) / 10.0,
                ),
                "attack_id": getattr(
                    attack,
                    "attack_id",
                    attack_id,
                ),
                "attack_name": getattr(
                    attack,
                    "attack_name",
                    "",
                ),
                "attack_type": getattr(
                    attack,
                    "attack_type",
                    "",
                ),
                "attack_category": getattr(
                    attack,
                    "attack_category",
                    "",
                ),
                "severity_score": getattr(
                    attack,
                    "severity_score",
                    0,
                ),
                "risk_score": getattr(
                    attack,
                    "risk_score",
                    0,
                ),
                "raw": (
                    attack.model_dump()
                    if hasattr(attack, "model_dump")
                    else str(attack)
                ),
                "source": "ThreatMiner",
            }

        # Web-app fallback.
        suspicious_signals = {
            "ignore previous instructions": 1.0,
            "ignore all previous instructions": 1.0,
            "bypass": 0.8,
            "jailbreak": 1.0,
            "unrestricted": 0.9,
            "reveal system prompt": 1.0,
            "reveal the system prompt": 1.0,
            "disable safety": 1.0,
            "bypass restrictions": 0.9,
            "act as an unrestricted": 0.9,
        }

        lowered = text.lower()

        matches = [
            signal
            for signal in suspicious_signals
            if signal in lowered
        ]

        score = max(
            [suspicious_signals[m] for m in matches],
            default=0.0,
        )

        return {
            "detected": bool(matches),
            "score": score,
            "matches": matches,
            "attack_id": attack_id,
            "source": "web_fallback",
        }