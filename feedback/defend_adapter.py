from pathlib import Path
from typing import Any, Dict, Optional


class DefendAdapter:
    """
    Adapter for the existing PhantomGuard DEFEND pipeline.

    If a trained artifact is available, this adapter uses the real
    XGBoost + TCN + GNN + meta-classifier pipeline.

    If no artifact is available, it uses the identification result
    to provide a safe fallback so the web application can still run.
    """

    def __init__(
        self,
        artifact_path: str = (
            "artifacts/defend_full_tcn/"
            "phantomguard_full_architecture.joblib"
        ),
        defend_fn=None,
    ):
        self.artifact_path = Path(artifact_path)
        self.defend_fn = defend_fn

        self.models = None

        if self.defend_fn is None and self.artifact_path.exists():
            try:
                from defend.simulate_live import load_models

                self.models = load_models(str(self.artifact_path))
            except Exception:
                self.models = None

    def run(
        self,
        text: str,
        identification: Optional[Dict[str, Any]] = None,
        transaction: Optional[Dict[str, Any]] = None,
        attack_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        identification = identification or {}

        # Use an explicitly supplied DEFEND function.
        if self.defend_fn is not None:
            result = self.defend_fn(text)

            if isinstance(result, dict):
                return result

            return {
                "attack_id": attack_id,
                "blocked": bool(result),
                "output": (
                    "Request blocked by PhantomGuard."
                    if result
                    else text
                ),
                "source": "defend_fn",
            }

        # Use the actual trained DEFEND pipeline when possible.
        if self.models is not None and transaction is not None:
            try:
                from defend.simulate_live import score_single

                (
                    preprocessor,
                    xgb_model,
                    tcn_model,
                    gnn_model,
                    meta_model,
                    feature_columns,
                    seq_len,
                    max_neighbors,
                ) = self.models

                (
                    xgb_prob,
                    tcn_prob,
                    gnn_prob,
                    meta_prob,
                ) = score_single(
                    transaction,
                    preprocessor,
                    xgb_model,
                    tcn_model,
                    gnn_model,
                    meta_model,
                    feature_columns,
                    seq_len,
                    max_neighbors,
                )

                blocked = meta_prob >= 0.5

                return {
                    "attack_id": attack_id,
                    "blocked": blocked,
                    "risk_score": meta_prob,
                    "xgb_probability": xgb_prob,
                    "tcn_probability": tcn_prob,
                    "gnn_probability": gnn_prob,
                    "meta_probability": meta_prob,
                    "output": (
                        "Transaction blocked by PhantomGuard."
                        if blocked
                        else "Transaction allowed."
                    ),
                    "source": "defend_models",
                }

            except Exception as exc:
                return {
                    "attack_id": attack_id,
                    "blocked": bool(
                        identification.get("detected", False)
                    ),
                    "risk_score": 1.0
                    if identification.get("detected", False)
                    else 0.0,
                    "output": (
                        "Request blocked by PhantomGuard."
                        if identification.get("detected", False)
                        else text
                    ),
                    "source": "fallback_after_model_error",
                    "error": str(exc),
                }

        # Safe fallback for web/API text scanning.
        detected = bool(
            identification.get("detected", False)
        )

        return {
            "attack_id": attack_id,
            "blocked": detected,
            "risk_score": (
                float(identification.get("score", 0.0))
                if detected
                else 0.0
            ),
            "output": (
                "Request blocked by PhantomGuard."
                if detected
                else text
            ),
            "source": "identification_fallback",
        }