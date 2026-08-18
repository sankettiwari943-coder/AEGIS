import math
from typing import List, Dict, Any, Optional

class PredictionEvaluator:
    """
    Evaluates predictive accuracy against observed ground truth.
    Computes absolute error, zero-safe relative error, and status classification with configurable tolerances.
    """
    def __init__(self, default_tolerance: float = 5.0):
        self.default_tolerance = default_tolerance

    def calculate_absolute_error(self, predicted: float, actual: float) -> float:
        """Returns abs(predicted - actual) rounded to 2 decimal places."""
        return round(abs(predicted - actual), 2)

    def calculate_error(self, predicted: float, actual: float) -> float:
        """Returns raw difference: actual - predicted (positive means reality was higher than predicted)."""
        return round(actual - predicted, 2)

    def calculate_relative_error_pct(self, predicted: float, actual: float) -> Optional[float]:
        """
        Safe percentage error calculation avoiding zero division.
        If actual is near zero (< 0.001), returns None or uses predicted as denominator.
        """
        if abs(actual) > 0.001:
            return round((abs(predicted - actual) / abs(actual)) * 100.0, 2)
        elif abs(predicted) > 0.001:
            return round((abs(predicted - actual) / abs(predicted)) * 100.0, 2)
        return 0.0

    def classify_status(self, predicted: float, actual: float, tolerance: Optional[float] = None) -> str:
        """
        Classifies outcome based on tolerance threshold:
        - within ±tolerance: "ACCURATE"
        - actual > prediction + tolerance: "UNDERPREDICTED" (disaster/deterioration was worse than predicted)
        - prediction > actual + tolerance: "OVERPREDICTED" (predicted worse than it turned out)
        """
        tol = tolerance if tolerance is not None else self.default_tolerance
        diff = actual - predicted # positive = actual was higher

        if abs(diff) <= tol:
            return "ACCURATE"
        elif diff > tol:
            return "UNDERPREDICTED"
        else:
            return "OVERPREDICTED"

    def evaluate_outcomes(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates aggregate statistics over a list of outcome dictionaries or OutcomeItem objects.
        """
        if not outcomes:
            return {
                "sample_count": 0,
                "accurate_count": 0,
                "underpredicted_count": 0,
                "overpredicted_count": 0,
                "accuracy_percent": 100.0,
                "average_absolute_error": 0.0,
                "average_bias": 0.0
            }

        n = len(outcomes)
        acc_count = 0
        under_count = 0
        over_count = 0
        total_abs_err = 0.0
        total_bias = 0.0

        for o in outcomes:
            pred = o.get("predicted_value", 0.0)
            act = o.get("actual_value", 0.0)
            status = o.get("status") or self.classify_status(pred, act)
            abs_err = o.get("absolute_error", self.calculate_absolute_error(pred, act))
            raw_err = o.get("error", self.calculate_error(pred, act))

            if status == "ACCURATE":
                acc_count += 1
            elif status == "UNDERPREDICTED":
                under_count += 1
            elif status == "OVERPREDICTED":
                over_count += 1

            total_abs_err += abs_err
            total_bias += raw_err

        accuracy_pct = round((acc_count / n) * 100.0, 1)
        avg_abs_err = round(total_abs_err / n, 2)
        avg_bias = round(total_bias / n, 2)

        return {
            "sample_count": n,
            "accurate_count": acc_count,
            "underpredicted_count": under_count,
            "overpredicted_count": over_count,
            "accuracy_percent": accuracy_pct,
            "average_absolute_error": avg_abs_err,
            "average_bias": avg_bias
        }

prediction_evaluator = PredictionEvaluator()
