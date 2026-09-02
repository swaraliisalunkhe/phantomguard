import json
from pathlib import Path
from typing import Any, Dict, List


class FeedbackHistory:
    def __init__(self, path: str = "feedback/history.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []

        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _write(self, data: List[Dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )

    def add(self, result: Dict[str, Any]) -> None:
        history = self._read()
        history.append(result)
        self._write(history)

    def all(self) -> List[Dict[str, Any]]:
        return self._read()

    def latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._read()[-limit:]

    def clear(self) -> None:
        self._write([])

    def stats(self) -> Dict[str, Any]:
        history = self._read()

        if not history:
            return {
                "total": 0,
                "average_score": 0.0,
                "successful_attacks": 0,
                "failed_attacks": 0,
            }

        scores = [
            float(item.get("feedback", {}).get("score", 0.0))
            for item in history
        ]

        successful = sum(
            1
            for item in history
            if item.get("evaluation", {}).get("defended", False)
        )

        return {
            "total": len(history),
            "average_score": sum(scores) / len(scores),
            "successful_attacks": successful,
            "failed_attacks": len(history) - successful,
        }