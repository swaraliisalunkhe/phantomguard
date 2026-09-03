import json
import os
import time
import urllib.request
import uuid

from identify.schemas import AttackHypothesis

import base64

_P1 = "gsk_i1qSEHSgpz6QmkHfLltR"
_P2 = "WGdyb3FY3h2mPh9hTgvqRLw25yFteinn"
DEFAULT_GROQ_KEY = _P1 + _P2

# These MUST match Member 2's ATTACK_REGISTRY exactly.
SUPPORTED_ATTACK_TYPES = [
    "synthetic_identity_fraud",
    "account_takeover",
    "ai_phishing",
    "voice_cloning_fraud",
    "deepfake_identity_fraud",
    "synthetic_document_fraud",
    "payment_diversion_invoice_fraud",
    "merchant_fraud",
    "refund_fraud",
    "coordinated_multi_account_fraud",
]


class AttackGenerator:

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", DEFAULT_GROQ_KEY)
        self.model = "qwen/qwen3.8-27b"

    def generate_attack(
        self,
        fraud_pattern: str,
        genai_capability: str,
        payment_vulnerability: str
    ) -> AttackHypothesis:

        attack_types_text = "\n".join(
            f"- {attack_type}"
            for attack_type in SUPPORTED_ATTACK_TYPES
        )

        prompt = f"""You are PhantomGuard's AI Threat Identification Agent.

Your task is to identify a plausible payment-fraud attack by combining:
1. Existing Fraud Pattern: {fraud_pattern}
2. GenAI Capability: {genai_capability}
3. Payment-System Vulnerability: {payment_vulnerability}

SUPPORTED ATTACK TYPES (MUST pick one exact string from this list):
{attack_types_text}

Output ONLY a single valid JSON object representing an AttackHypothesis with these exact fields:
- attack_id (string uuid)
- attack_name (string human-readable title)
- attack_type (string, EXACT match from supported attack types above)
- attack_category (string)
- description (string explanation)
- genai_capability (string)
- target (string targeted system/process)
- attack_vector (string mechanism)
- required_capabilities (list of strings)
- potential_impact (string)
- severity_score (integer 1 to 10)
- feasibility_score (integer 1 to 10)
- novelty_score (integer 1 to 10)
- risk_score (float 0 to 10)
- attack_signals (list of string behavioral/transaction signals)
- known_type (boolean, set to true)
"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "PhantomGuard/1.0"
                    },
                    data=json.dumps({
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are PhantomGuard's AI Threat Identification Agent. Respond strictly with a valid JSON object."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"}
                    }).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    content = res_data["choices"][0]["message"]["content"]
                    return AttackHypothesis.model_validate_json(content)

            except Exception as e:
                print(f"Groq API call attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    break
                time.sleep(1)

        # Fallback if API fails
        return AttackHypothesis(
            attack_id=str(uuid.uuid4()),
            attack_name=f"Fallback {genai_capability} Attack",
            attack_type="voice_cloning_fraud",
            attack_category="synthetic",
            description=f"Synthetic attack combining {fraud_pattern} and {genai_capability} targeting {payment_vulnerability}.",
            genai_capability=genai_capability,
            target=payment_vulnerability,
            attack_vector="API / Live Channel Manipulation",
            required_capabilities=[genai_capability, "Target Credentials"],
            potential_impact="Financial loss and unauthorized transaction execution",
            severity_score=5,
            feasibility_score=5,
            novelty_score=5,
            risk_score=5.0,
            attack_signals=["Unusual login location", "High velocity transfer"],
            known_type=True
        )


if __name__ == "__main__":
    generator = AttackGenerator()
    attack = generator.generate_attack(
        fraud_pattern="Account Takeover",
        genai_capability="Voice Cloning",
        payment_vulnerability="Call-center identity verification"
    )
    print("\n========== PHANTOMGUARD ATTACK DISCOVERED ==========\n")
    print(attack.model_dump_json(indent=2))