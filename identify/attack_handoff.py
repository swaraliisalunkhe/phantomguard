import sys
from pathlib import Path

from identify.schemas import AttackHypothesis
from identify.attack_generator_llm import AttackGenerator


def prepare_generator_input(attack: AttackHypothesis) -> dict:
    """
    Convert Member 1's rich AttackHypothesis
    into the minimal contract required by Member 2.
    """
    return {
        "attack_type": attack.attack_type
    }


def generate_transactions_from_attack(
    attack: AttackHypothesis,
    n: int = 100
):
    """
    Send Member 1's attack_type to Member 2's
    transaction generator.
    """

    generator_input = prepare_generator_input(attack)
    attack_type = generator_input["attack_type"]

    # Member 2's files use local imports such as
    # "import fake_data", so add generate/ to sys.path.
    generate_dir = Path(__file__).resolve().parent.parent / "generate"

    if str(generate_dir) not in sys.path:
        sys.path.insert(0, str(generate_dir))

    from transaction_sim import generate_transactions

    transactions = generate_transactions(
        attack_type=attack_type,
        n=n
    )

    return transactions


if __name__ == "__main__":

    print("\n========== PHANTOMGUARD LLM ==========\n")

    # Create Member 1's Gemini attack generator.
    generator = AttackGenerator()

    # Ask Gemini to identify an attack.
    attack = generator.generate_attack(
        fraud_pattern="Account Takeover",
        genai_capability="Voice Cloning",
        payment_vulnerability="Call-center identity verification"
    )

    print("\n========== ATTACK DISCOVERED BY LLM ==========\n")

    print(
        attack.model_dump_json(indent=2)
    )

    # Convert the rich LLM output into
    # Member 2's minimal contract.
    generator_input = prepare_generator_input(attack)

    print("\n========== MEMBER 2 INPUT ==========\n")

    print(generator_input)

    # Generate synthetic transactions.
    print("\n========== GENERATING TRANSACTIONS ==========\n")

    transactions = generate_transactions_from_attack(
        attack,
        n=100
    )

    print(
        f"Generated {len(transactions)} transactions."
    )

    print("\n========== FIRST 5 TRANSACTIONS ==========\n")

    print(transactions.head())

    # Save generated transactions.
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "phantomguard_attack_test.csv"

    transactions.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nDataset saved to: {output_path}"
    )