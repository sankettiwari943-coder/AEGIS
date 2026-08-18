"""
Risk Propagation Model for Cascading Disasters
Calculates explainable, deterministic risk propagation across multi-step failure chains
with confidence decay, multi-factor amplification, and normalized bounds (0-100).
"""
from typing import List, Dict, Tuple, Any, Optional
import math

class RiskPropagationModel:
    """
    Explainable propagation model for downstream risk computation.
    All calculations represent model estimates and are strictly bounded between 0 and 100.
    """
    def __init__(
        self,
        base_amplification_threshold: float = 70.0,
        multi_failure_compound_rate: float = 0.05,
        confidence_decay_factor: float = 0.95,
        damping_factor: float = 0.92
    ):
        self.base_amplification_threshold = base_amplification_threshold
        self.multi_failure_compound_rate = multi_failure_compound_rate
        self.confidence_decay_factor = confidence_decay_factor
        self.damping_factor = damping_factor

    def compute_direct_child_risk(
        self,
        parent_risk: float,
        edge_impact: float,
        edge_confidence: float,
        local_vulnerability: float = 1.0
    ) -> Tuple[int, int]:
        """
        Calculate direct child node risk and confidence from parent.
        Child Risk = min(100, Parent Risk * Edge Impact * Edge Confidence * Vulnerability)
        Returns: (child_risk_score, confidence_pct)
        """
        raw_risk = parent_risk * edge_impact * (0.5 + 0.5 * edge_confidence) * local_vulnerability
        child_risk = int(max(0, min(100, round(raw_risk))))
        conf = int(max(10, min(100, round(edge_confidence * 100))))
        return child_risk, conf

    def propagate_chain(
        self,
        root_risk: float,
        edges_sequence: List[Dict[str, Any]],
        initial_confidence: float = 0.90
    ) -> List[Dict[str, Any]]:
        """
        Propagate risk sequentially through a multi-step chain [A -> B -> C -> D].
        Returns list of step results with intermediate risk, confidence, and status.
        """
        steps = []
        current_risk = float(root_risk)
        current_confidence = float(initial_confidence)

        for idx, edge in enumerate(edges_sequence):
            impact = float(edge.get("impact", 0.8))
            confidence = float(edge.get("confidence", 0.85))
            relationship = edge.get("relationship", "causes")

            # Apply attenuation or compounding based on relationship
            if relationship in ["causes", "disables", "cuts_off"]:
                multiplier = 0.90 + 0.15 * impact
            elif relationship == "amplifies":
                multiplier = 0.95 + 0.20 * impact
            elif relationship == "delays":
                multiplier = 0.85 + 0.15 * impact
            else:
                multiplier = 0.85

            # Step Risk calculation
            step_raw = current_risk * impact * multiplier
            step_risk = int(max(0, min(100, round(step_raw))))
            
            # Confidence decay along chain
            current_confidence = current_confidence * confidence * self.confidence_decay_factor
            step_conf_pct = int(max(20, min(100, round(current_confidence * 100))))

            # Assign human-readable action state
            if idx == 0:
                action_state = "INITIATING"
            elif step_risk >= 85:
                action_state = "CRITICAL"
            elif step_risk >= 70:
                action_state = "SURGING"
            elif step_risk >= 50:
                action_state = "ELEVATED"
            else:
                action_state = "MODERATE"

            steps.append({
                "source": edge.get("source"),
                "target": edge.get("target"),
                "relationship": relationship,
                "impact": int(impact * 100),
                "confidence": step_conf_pct,
                "step_risk": step_risk,
                "action_state": action_state,
                "reason": edge.get("reason", "")
            })

            # Next step uses this risk as upstream driver
            current_risk = float(step_risk)

        return steps

    def calculate_compound_cascading_score(
        self,
        primary_risk: int,
        secondary_risks: Dict[str, int],
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Calculates the aggregate systemic cascading risk score and contributor breakdown.
        """
        default_weights = {
            "road_isolation": 0.24,
            "medical_access": 0.22,
            "power_failure": 0.18,
            "communication_loss": 0.14,
            "water_contamination": 0.10,
            "population_isolation": 0.12
        }
        w = weights or default_weights

        # Base weighted sum
        weighted_sum = primary_risk * 0.25
        contributors = []

        total_weight_sec = sum(w.values())
        norm_factor = 0.75 / total_weight_sec if total_weight_sec > 0 else 1.0

        for key, weight in w.items():
            val = secondary_risks.get(key, int(primary_risk * 0.75))
            contrib_pts = int(round(val * weight * norm_factor))
            weighted_sum += contrib_pts
            
            # Format display label
            label = key.replace("_", " ").title()
            contributors.append({
                "name": label,
                "points": contrib_pts,
                "category": key
            })

        # Compounding amplification if 3 or more critical failures coincide (> 70)
        critical_count = sum(1 for v in secondary_risks.values() if v >= self.base_amplification_threshold)
        if critical_count >= 3:
            amplification = (critical_count - 2) * 3.5
            weighted_sum += amplification

        final_score = int(max(0, min(100, round(weighted_sum))))
        
        # Sort contributors descending by points
        contributors.sort(key=lambda x: x["points"], reverse=True)

        return final_score, contributors

risk_propagation_model = RiskPropagationModel()
