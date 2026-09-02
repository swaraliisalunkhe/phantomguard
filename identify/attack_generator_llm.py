import os
import time
import truststore

# Use Windows native certificate store
truststore.inject_into_ssl()

from google import genai
from google.genai import types
from google.genai import errors

from identify.schemas import AttackHypothesis


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

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self.client = None
            print("WARNING: GEMINI_API_KEY not found. Using mock generator.")
        else:
            self.client = genai.Client(api_key=api_key)

        self.model = "gemini-3.7-flash"


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

        prompt = f"""
You are PhantomGuard's AI Threat Identification Agent.

Your task is to identify a plausible payment-fraud attack
by combining:

1. An existing fraud pattern
2. An emerging GenAI capability
3. A payment-system vulnerability

INPUTS:

Existing Fraud Pattern:
{fraud_pattern}

GenAI Capability:
{genai_capability}

Payment-System Vulnerability:
{payment_vulnerability}


SUPPORTED ATTACK TYPES:

You MUST select the closest matching attack_type
from this exact list.

Do NOT invent a new attack_type.

{attack_types_text}


Analyze how the supplied inputs combine into a realistic
payment-fraud scenario.

The attack should be:

- Plausible
- Relevant to payment systems
- Clearly connected to the supplied inputs
- Useful for synthetic transaction generation
- Detectable through behavioral or transaction signals


SCORING:

severity_score:
1 = very low
10 = extremely severe

feasibility_score:
1 = very difficult
10 = highly feasible

novelty_score:
1 = common/known
10 = highly novel

risk_score:
0 = minimal risk
10 = extreme risk


Because this prototype uses the registered attack types,
set known_type to true.

Return exactly ONE AttackHypothesis object.
"""


        if not self.client:
            import uuid
            return AttackHypothesis(
                attack_id=str(uuid.uuid4()),
                attack_name=f"Mock {genai_capability} Attack",
                attack_type="voice_cloning_fraud",
                attack_category="synthetic",
                description=f"Mocked {fraud_pattern} using {genai_capability} targeting {payment_vulnerability}.",
                severity_score=5,
                feasibility_score=5,
                novelty_score=5,
                risk_score=5,
                known_type=True
            )

        # Retry temporary Gemini server failures.
        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AttackHypothesis,
                    ),
                )

                return AttackHypothesis.model_validate_json(
                    response.text
                )

            except errors.ServerError:

                if attempt == max_retries - 1:
                    raise

                wait_time = 2 ** attempt

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)


if __name__ == "__main__":

    generator = AttackGenerator()

    attack = generator.generate_attack(
        fraud_pattern="Account Takeover",
        genai_capability="Voice Cloning",
        payment_vulnerability="Call-center identity verification"
    )

    print(
        "\n========== PHANTOMGUARD ATTACK DISCOVERED ==========\n"
    )

    print(attack.model_dump_json(indent=2))