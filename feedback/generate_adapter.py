from typing import Any, Dict, Optional


class GenerateAdapter:
    """
    Adapter for PhantomGuard's GENERATE stage.

    Supports an existing generation callable while providing a
    deterministic fallback for local/web-app testing.
    """

    def __init__(self, generate_fn=None):
        self.generate_fn = generate_fn

    def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if self.generate_fn is not None:
            result = self.generate_fn(prompt)

            if isinstance(result, dict):
                return result

            return {
                "prompt": prompt,
                "output": str(result),
                "source": "generate_fn",
            }

        return {
            "prompt": prompt,
            "output": (
                "PhantomGuard safely processed the request."
            ),
            "blocked": False,
            "source": "fallback",
        }