"""
Compatibility adapter wrapping the modular prediction service.
"""
from app.services.prediction.prediction_service import prediction_service, PredictionService
from app.services.prediction.risk_model import risk_model, RiskModel
from app.services.prediction.escalation_model import escalation_model, EscalationModel

PredictionEngine = PredictionService
prediction_engine = prediction_service
