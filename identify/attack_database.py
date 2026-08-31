import json
from pathlib import Path
from typing import List, Optional

from identify.schemas import AttackHypothesis


class AttackDatabase:
    """
    Persistent database for PhantomGuard attack hypotheses.

    Stores discovered attacks as JSON so they can be:
    - added
    - searched
    - retrieved
    - updated
    - persisted between runs
    """

    def __init__(self, db_path: str = "data/attack_database.json"):

        self.db_path = Path(db_path)

        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create empty database if it doesn't exist
        if not self.db_path.exists():
            self._save([])


    def _load(self) -> List[dict]:
        """Load all attacks from the database."""

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            return []


    def _save(self, attacks: List[dict]):
        """Save all attacks to the database."""

        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(
                attacks,
                f,
                indent=2,
                ensure_ascii=False
            )


    def add_attack(self, attack: AttackHypothesis) -> bool:
        """
        Add a new attack to the database.

        Returns:
            True  -> attack was added
            False -> attack already exists
        """

        attacks = self._load()

        # Prevent duplicate attack IDs
        for existing in attacks:

            if existing.get("attack_id") == attack.attack_id:
                return False

        attacks.append(
            attack.model_dump()
        )

        self._save(attacks)

        return True


    def get_attack(self, attack_id: str) -> Optional[AttackHypothesis]:
        """Retrieve an attack using its attack_id."""

        attacks = self._load()

        for attack in attacks:

            if attack.get("attack_id") == attack_id:

                return AttackHypothesis.model_validate(attack)

        return None


    def get_all_attacks(self) -> List[AttackHypothesis]:
        """Return all attacks in the database."""

        attacks = self._load()

        return [
            AttackHypothesis.model_validate(attack)
            for attack in attacks
        ]


    def get_by_attack_type(
        self,
        attack_type: str
    ) -> List[AttackHypothesis]:
        """Return all attacks belonging to an attack type."""

        attacks = self.get_all_attacks()

        return [
            attack
            for attack in attacks
            if attack.attack_type == attack_type
        ]


    def get_by_category(
        self,
        category: str
    ) -> List[AttackHypothesis]:
        """Return attacks matching a category."""

        attacks = self.get_all_attacks()

        return [
            attack
            for attack in attacks
            if attack.attack_category.lower() == category.lower()
        ]


    def get_high_risk_attacks(
        self,
        threshold: float = 7.0
    ) -> List[AttackHypothesis]:
        """Return attacks whose risk score meets the threshold."""

        attacks = self.get_all_attacks()

        return [
            attack
            for attack in attacks
            if attack.risk_score >= threshold
        ]


    def count(self) -> int:
        """Return number of attacks in the database."""

        return len(self._load())


    def clear(self):
        """Delete all stored attacks."""

        self._save([])


# ------------------------------------------------------------------
# TEST
# ------------------------------------------------------------------

if __name__ == "__main__":

    from identify.schemas import AttackHypothesis

    database = AttackDatabase()

    test_attack = AttackHypothesis(
        attack_id="TEST-001",
        attack_name="Test Voice Cloning Attack",
        attack_type="voice_cloning_fraud",
        attack_category="Account Takeover",
        description="Test attack for database validation.",
        genai_capability="Voice cloning",
        target="Call-center authentication",
        attack_vector="Voice impersonation",
        required_capabilities=[
            "Voice cloning"
        ],
        potential_impact="Account takeover",
        severity_score=8,
        feasibility_score=7,
        novelty_score=6,
        risk_score=7.2,
        attack_signals=[
            "Credential reset",
            "Unusual transaction"
        ],
        default_channel_bias=[
            "phone_banking"
        ],
        severity_weight=0.8,
        known_type=True
    )

    added = database.add_attack(test_attack)

    print("\n========== ATTACK DATABASE TEST ==========\n")

    print("Attack added:", added)

    print("Total attacks:", database.count())

    retrieved = database.get_attack("TEST-001")

    if retrieved:

        print("\nRetrieved attack:")

        print(
            retrieved.model_dump_json(indent=2)
        )

    else:

        print("Attack not found.")