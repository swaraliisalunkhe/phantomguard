import uuid
from typing import Any, Dict, Optional

from .attack_evolver import AttackEvolver
from .defend_adapter import DefendAdapter
from .generate_adapter import GenerateAdapter
from .history import FeedbackHistory
from .identify_adapter import IdentifyAdapter
from .model_updater import ModelUpdater
from .schemas import (
    Attack,
    DefenseResult,
    Evaluation,
    Feedback,
    IdentificationResult,
    LoopResult,
)


class FeedbackLoop:
    """
    Complete PhantomGuard closed loop:

        INPUT
          ↓
        IDENTIFY
          ↓
        DEFEND
          ↓
        EVALUATE
          ↓
        FEEDBACK
          ↓
        HISTORY / MODEL UPDATE
          ↓
        ATTACK EVOLUTION
    """

    def __init__(
        self,
        identify=None,
        defend=None,
        generate=None,
        history_path="feedback/history.json",
    ):
        self.identify = IdentifyAdapter(
            identify_fn=identify
        )

        self.defend = DefendAdapter(
            defend_fn=defend
        )

        self.generate = GenerateAdapter(
            generate_fn=generate
        )

        self.history = FeedbackHistory(
            history_path
        )

        self.updater = ModelUpdater()
        self.evolver = AttackEvolver()

    def evaluate(
        self,
        attack: Attack,
        identification: IdentificationResult,
        defense: DefenseResult,
    ) -> Evaluation:

        detected = identification.detected
        blocked = defense.blocked

        if detected and blocked:
            score = 1.0
            reason = "Attack identified and blocked."

        elif detected and not blocked:
            score = 0.5
            reason = "Attack identified but not blocked."

        elif not detected and blocked:
            score = 0.75
            reason = "Attack blocked despite missed identification."

        else:
            score = 0.0
            reason = "Attack was neither identified nor blocked."

        return Evaluation(
            attack_id=attack.attack_id,
            detected=detected,
            defended=blocked,
            score=score,
            reason=reason,
        )

    def run(
        self,
        text: str,
        category: str = "user",
        evolve: bool = True,
        transaction: Optional[Dict[str, Any]] = None,
    ) -> LoopResult:

        attack = Attack(
            attack_id=str(uuid.uuid4()),
            text=text,
            category=category,
        )

        raw_identification = self.identify.run(
            text,
            attack_id=attack.attack_id,
        )

        identification = IdentificationResult(
            attack_id=attack.attack_id,
            detected=bool(
                raw_identification.get("detected", False)
            ),
            score=float(
                raw_identification.get("score", 0.0)
            ),
            category=raw_identification.get(
                "attack_category",
                category,
            ),
            reason=raw_identification.get(
                "reason",
                "",
            ),
            metadata=raw_identification,
        )

        raw_defense = self.defend.run(
            text,
            identification=raw_identification,
            transaction=transaction,
            attack_id=attack.attack_id,
        )

        defense = DefenseResult(
            attack_id=attack.attack_id,
            blocked=bool(
                raw_defense.get("blocked", False)
            ),
            output=str(
                raw_defense.get("output", "")
            ),
            reason=str(
                raw_defense.get("reason", "")
            ),
            metadata=raw_defense,
        )

        evaluation = self.evaluate(
            attack,
            identification,
            defense,
        )

        feedback = Feedback(
            attack_id=attack.attack_id,
            accepted=evaluation.score >= 0.5,
            score=evaluation.score,
            comment=evaluation.reason,
        )

        next_attack = None

        if evolve:
            next_attack = self.evolver.evolve(
                attack
            )

        result = LoopResult(
            attack=attack,
            identification=identification,
            defense=defense,
            evaluation=evaluation,
            feedback=feedback,
            next_attack=next_attack,
        )

        self.history.add(
            self.serialize(result)
        )

        self.updater.update(
            feedback.score
        )

        return result

    @staticmethod
    def serialize(
        result: LoopResult,
    ) -> Dict[str, Any]:

        return {
            "attack": {
                "attack_id": result.attack.attack_id,
                "text": result.attack.text,
                "category": result.attack.category,
                "severity": result.attack.severity,
                "metadata": result.attack.metadata,
            },
            "identification": {
                "attack_id": result.identification.attack_id,
                "detected": result.identification.detected,
                "score": result.identification.score,
                "category": result.identification.category,
                "reason": result.identification.reason,
                "metadata": result.identification.metadata,
            },
            "defense": {
                "attack_id": result.defense.attack_id,
                "blocked": result.defense.blocked,
                "output": result.defense.output,
                "reason": result.defense.reason,
                "metadata": result.defense.metadata,
            },
            "evaluation": {
                "attack_id": result.evaluation.attack_id,
                "detected": result.evaluation.detected,
                "defended": result.evaluation.defended,
                "score": result.evaluation.score,
                "reason": result.evaluation.reason,
                "metadata": result.evaluation.metadata,
            },
            "feedback": {
                "attack_id": result.feedback.attack_id,
                "accepted": result.feedback.accepted,
                "score": result.feedback.score,
                "comment": result.feedback.comment,
                "metadata": result.feedback.metadata,
            },
            "next_attack": (
                {
                    "attack_id": result.next_attack.attack_id,
                    "text": result.next_attack.text,
                    "category": result.next_attack.category,
                    "severity": result.next_attack.severity,
                    "metadata": result.next_attack.metadata,
                }
                if result.next_attack
                else None
            ),
        }

    def stats(self):
        return self.history.stats()