import json
from pathlib import Path
from typing import Any, Dict


class ModelUpdater:
    """
    Stores feedback-derived metrics.

    This deliberately does not retrain the production DEFEND models.
    It records feedback that can be used for later retraining.
    """

    def __init__(
        self,
        path: str = "feedback/model_state.json",
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "average_score": 0.0,
            }

        try:
            return json.loads(
                self.path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "average_score": 0.0,
            }

    def _write(self, data: Dict[str, Any]) -> None:
        self.path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def update(self, score: float) -> Dict[str, Any]:
        score = max(0.0, min(1.0, float(score)))

        state = self._read()

        total = int(state["total_feedback"])
        old_average = float(state["average_score"])

        state["total_feedback"] = total + 1

        if score >= 0.5:
            state["positive_feedback"] += 1
        else:
            state["negative_feedback"] += 1

        state["average_score"] = (
            (old_average * total) + score
        ) / (total + 1)

        self._write(state)

        return state

    def state(self) -> Dict[str, Any]:
        return self._read()