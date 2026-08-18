from typing import Dict, Any, List
from pydantic import BaseModel

class RiskWeights(BaseModel):
    RAINFALL_WEIGHT: float = 0.20
    RIVER_LEVEL_WEIGHT: float = 0.25
    FLOOD_DEPTH_WEIGHT: float = 0.25
    TREND_WEIGHT: float = 0.15
    INFRASTRUCTURE_WEIGHT: float = 0.10
    ACCESSIBILITY_WEIGHT: float = 0.05

DEFAULT_WEIGHTS = RiskWeights()

class HistoricalObservations(BaseModel):
    river_level_history: List[float] # [T-60m, T-30m, NOW]
    rainfall_history: List[float]    # [T-60m, T-30m, NOW]
    flood_depth_history: List[float] # [T-60m, T-30m, NOW]
    road_access_history: List[int]   # [T-60m, T-30m, NOW]

def calculate_trend_velocity(history: List[float]) -> float:
    """
    Calculates the normalized rate of change (+/-) from 3-point time-series.
    Returns a value between -1.0 and +1.0.
    """
    if len(history) < 2:
        return 0.0
    delta_1 = history[-1] - history[-2]
    delta_2 = history[-2] - history[-3] if len(history) >= 3 else delta_1
    avg_delta = (delta_1 + delta_2) / 2.0
    # Normalize by scale
    return max(-1.0, min(1.0, avg_delta / max(1.0, history[-1])))

class RiskModel:
    """
    Explainable Weighted Multi-Factor Flood Risk Engine.
    Computes current and future risk contributions based on configurable physical and infrastructural weights.
    """
    def __init__(self, weights: RiskWeights = DEFAULT_WEIGHTS):
        self.weights = weights

    def compute_composite_risk(
        self,
        rainfall_mmh: float,
        river_level_m: float,
        flood_depth_cm: float,
        elevation_m: float,
        road_access_pct: int,
        infra_vulnerability: float, # 0.0 - 1.0
        historical_obs: HistoricalObservations,
        horizon_minutes: int = 0
    ) -> Dict[str, Any]:
        # 1. Normalized Components (0.0 to 1.0)
        rainfall_norm = min(1.0, rainfall_mmh / 100.0)
        river_norm = min(1.0, max(0.0, (river_level_m - 2.0) / 8.0))
        depth_norm = min(1.0, flood_depth_cm / 150.0)
        elevation_penalty = max(0.0, (25.0 - elevation_m) / 25.0)
        road_cutoff_norm = max(0.0, (100 - road_access_pct) / 100.0)

        # 2. Trend Calculations
        river_trend = calculate_trend_velocity(historical_obs.river_level_history)
        rain_trend = calculate_trend_velocity(historical_obs.rainfall_history)
        depth_trend = calculate_trend_velocity(historical_obs.flood_depth_history)
        composite_trend = max(0.0, (river_trend * 0.45 + depth_trend * 0.35 + rain_trend * 0.20))

        # 3. Apply Horizon Progression Multiplier
        # (30m ~ 0.5x growth, 60m ~ 1.0x growth, 180m ~ 1.6x growth)
        time_factor = horizon_minutes / 60.0
        growth_multiplier = 1.0 + (composite_trend * 0.45 + elevation_penalty * 0.35) * time_factor

        # 4. Weighted Risk Score
        raw_score = (
            rainfall_norm * self.weights.RAINFALL_WEIGHT +
            river_norm * self.weights.RIVER_LEVEL_WEIGHT +
            depth_norm * self.weights.FLOOD_DEPTH_WEIGHT +
            composite_trend * self.weights.TREND_WEIGHT +
            infra_vulnerability * self.weights.INFRASTRUCTURE_WEIGHT +
            road_cutoff_norm * self.weights.ACCESSIBILITY_WEIGHT
        ) * 100.0 * growth_multiplier

        final_risk = min(99, max(10, int(raw_score)))

        return {
            "risk_score": final_risk,
            "rainfall_contrib": int(rainfall_norm * self.weights.RAINFALL_WEIGHT * 100),
            "river_contrib": int(river_norm * self.weights.RIVER_LEVEL_WEIGHT * 100),
            "depth_contrib": int(depth_norm * self.weights.FLOOD_DEPTH_WEIGHT * 100),
            "trend_contrib": int(composite_trend * self.weights.TREND_WEIGHT * 100),
            "infra_contrib": int(infra_vulnerability * self.weights.INFRASTRUCTURE_WEIGHT * 100),
            "road_contrib": int(road_cutoff_norm * self.weights.ACCESSIBILITY_WEIGHT * 100),
            "growth_multiplier": round(growth_multiplier, 2)
        }

risk_model = RiskModel()
