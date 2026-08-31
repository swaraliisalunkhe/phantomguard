from identify.attack_generator_llm import AttackGenerator
from identify.attack_database import AttackDatabase


class ThreatMiner:
    """
    PhantomGuard Threat Miner.

    Combines threat information and uses the LLM attack generator
    to produce a structured AttackHypothesis, then stores the
    discovered attack in the Attack Database.
    """

    def __init__(self):

        self.generator = AttackGenerator()
        self.database = AttackDatabase()

    def mine_threat(
        self,
        fraud_pattern: str,
        genai_capability: str,
        payment_vulnerability: str
    ):
        """
        Analyze a potential threat and store the resulting
        AttackHypothesis in the attack database.
        """

        print("\n========== THREAT MINING ==========\n")

        print("Fraud Pattern:", fraud_pattern)
        print("GenAI Capability:", genai_capability)
        print("Payment Vulnerability:", payment_vulnerability)

        # Ask Gemini to identify the attack.
        attack = self.generator.generate_attack(
            fraud_pattern=fraud_pattern,
            genai_capability=genai_capability,
            payment_vulnerability=payment_vulnerability
        )

        print("\n========== ATTACK DISCOVERED ==========\n")

        print(
            attack.model_dump_json(indent=2)
        )

        # Store the discovered attack.
        added = self.database.add_attack(attack)

        print("\n========== DATABASE RESULT ==========\n")

        if added:
            print("Attack successfully added to database.")
        else:
            print("Attack already exists in database.")

        print(
            f"Total attacks in database: "
            f"{self.database.count()}"
        )

        return attack


if __name__ == "__main__":

    print("\n========== PHANTOMGUARD THREAT MINER ==========\n")

    miner = ThreatMiner()

    attack = miner.mine_threat(
        fraud_pattern="Account Takeover",
        genai_capability="Voice Cloning",
        payment_vulnerability="Call-center identity verification"
    )

    print("\n========== THREAT MINING COMPLETE ==========\n")

    print(
        "Discovered attack:",
        attack.attack_name
    )