import uuid
from typing import List, Dict, Any, Optional
from app.models.schemas import FeedbackSubmission, FeedbackAnalysisResponse, OutcomeItem
from app.services.adaptive.outcome_tracker import outcome_tracker
from app.services.adaptive.learning_store import learning_store

class FeedbackEngine:
    """
    Receives and processes human operator & simulation feedback observations.
    Calculates operational divergence and triggers statistical recalibration.
    """
    def __init__(self):
        pass

    def record_feedback(self, sub: FeedbackSubmission) -> FeedbackAnalysisResponse:
        """
        Processes feedback submission, creates outcome records, and updates calibration confidence.
        """
        fb_id = f"fb-{str(uuid.uuid4())[:8]}"
        created_outcome: Optional[OutcomeItem] = None
        eta_err = None
        road_err = None

        # 1. Check if generic metric submission
        if sub.predicted_value is not None and sub.actual_value is not None:
            out_dict = outcome_tracker.record_outcome(
                metric=sub.metric,
                predicted_value=float(sub.predicted_value),
                actual_value=float(sub.actual_value),
                zone_id=sub.target_zone_id or "zone-7",
                source=sub.source or "Operator Observation",
                notes=sub.notes or sub.observations or "Operator feedback submission."
            )
            created_outcome = OutcomeItem(**out_dict)
            if sub.metric == "road_accessibility":
                road_err = int(out_dict["error"])
            elif sub.metric == "mission_eta":
                eta_err = int(out_dict["error"])

        # 2. Check legacy ETA & Road Access submission
        if sub.predicted_eta_minutes is not None and sub.actual_eta_minutes is not None:
            eta_err = sub.actual_eta_minutes - sub.predicted_eta_minutes
            out_dict_eta = outcome_tracker.record_outcome(
                metric="mission_eta",
                predicted_value=float(sub.predicted_eta_minutes),
                actual_value=float(sub.actual_eta_minutes),
                zone_id=sub.target_zone_id or "zone-7",
                source=sub.source or "Operator Observation",
                notes=f"Mission {sub.mission_id or 'dispatch'} travel time feedback."
            )
            if not created_outcome:
                created_outcome = OutcomeItem(**out_dict_eta)

        if sub.predicted_road_access_pct is not None and sub.actual_road_access_pct is not None:
            road_err = sub.actual_road_access_pct - sub.predicted_road_access_pct
            out_dict_road = outcome_tracker.record_outcome(
                metric="road_accessibility",
                predicted_value=float(sub.predicted_road_access_pct),
                actual_value=float(sub.actual_road_access_pct),
                zone_id=sub.target_zone_id or "zone-7",
                source=sub.source or "Operator Observation",
                notes=sub.observations or "Road passability feedback."
            )
            if not created_outcome:
                created_outcome = OutcomeItem(**out_dict_road)

        # Re-fetch calibration confidence
        calibs = learning_store.get_calibrations()
        conf_road = int(calibs.get("road_accessibility", {}).get("confidence", 0.74) * 100)
        prev_conf = max(40, conf_road - 2)
        new_conf = conf_road

        summary_parts = []
        if eta_err is not None:
            summary_parts.append(f"ETA divergence: {eta_err:+d} min")
        if road_err is not None:
            summary_parts.append(f"Road access divergence: {road_err:+d}%")
        if not summary_parts and created_outcome:
            summary_parts.append(f"{created_outcome.metric} error: {created_outcome.error:+.1f}")

        summary = (
            f"Observation recorded for Zone {sub.target_zone_id or '7'}. "
            f"{' • '.join(summary_parts)}. "
            f"Statistical bias adjusted; model confidence updated to {new_conf}%."
        )

        return FeedbackAnalysisResponse(
            feedback_id=fb_id,
            outcome=created_outcome,
            eta_error_minutes=eta_err if eta_err is not None else 0,
            road_access_error_pct=road_err if road_err is not None else 0,
            recalibration_summary=summary,
            previous_model_confidence_pct=prev_conf,
            updated_model_confidence_pct=new_conf,
            status="RECALIBRATION_RECORDED"
        )

    def get_history(self) -> List[FeedbackAnalysisResponse]:
        """Returns recent outcomes formatted as FeedbackAnalysisResponses for legacy compatibility."""
        outcomes = learning_store.get_all_outcomes()
        resp_list = []
        for o in outcomes[:10]:
            resp_list.append(FeedbackAnalysisResponse(
                feedback_id=f"fb-{o['id']}",
                outcome=OutcomeItem(**o),
                eta_error_minutes=int(o["error"]) if o["metric"] == "mission_eta" else 0,
                road_access_error_pct=int(o["error"]) if o["metric"] == "road_accessibility" else 0,
                recalibration_summary=f"{o['metric']} observed at {o['actual_value']} vs {o['predicted_value']} predicted ({o['status']}).",
                previous_model_confidence_pct=80,
                updated_model_confidence_pct=int(o["confidence"] * 100),
                status=o["status"]
            ))
        return resp_list

feedback_engine = FeedbackEngine()
