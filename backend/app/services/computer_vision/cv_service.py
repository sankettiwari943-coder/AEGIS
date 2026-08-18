from typing import List, Dict, Any, Optional
from app.services.computer_vision.cv_models import (
    CVAnalysisRequest, CVAnalysisResult
)
from app.services.computer_vision.demo_provider import demo_cv_provider

class ComputerVisionService:
    """
    AEGIS Computer Vision Service.
    Coordinates aerial/satellite image analytics, damage classification,
    and geo-referenced risk overlays.
    """
    def __init__(self):
        self.provider = demo_cv_provider

    def analyze_image(self, request: CVAnalysisRequest) -> CVAnalysisResult:
        """Runs computer vision analysis on drone/satellite imagery."""
        return self.provider.analyze(request)

    def get_scans_catalog(self) -> List[Dict[str, Any]]:
        """Returns catalog of indexed aerial and SAR satellite reconnaissance scans."""
        return self.provider.list_scans()

    def get_scan_by_id(self, scan_id: str) -> Optional[CVAnalysisResult]:
        """Retrieves complete CV diagnostic result for a specific scan ID."""
        req = CVAnalysisRequest(scan_id=scan_id)
        return self.provider.analyze(req)

cv_service = ComputerVisionService()
