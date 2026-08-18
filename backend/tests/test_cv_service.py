import pytest
from app.services.computer_vision import cv_service, CVAnalysisRequest

def test_cv_service_analysis():
    req = CVAnalysisRequest(target_zone_id="zone-7")
    result = cv_service.analyze_image(req)
    assert result.scan_id == "SCAN-Z07-DRONE-01"
    assert result.target_zone_id == "zone-7"
    assert result.analysis_label == "DEMO CV ANALYSIS"
    assert result.flood_extent_percent > 0
    assert len(result.detections) > 0
    assert result.overall_confidence > 0.8

def test_cv_scans_catalog():
    scans = cv_service.get_scans_catalog()
    assert len(scans) >= 3
    
    # Specific scan query
    scan1 = cv_service.get_scan_by_id("SCAN-Z04-SAR-01")
    assert scan1 is not None
    assert scan1.target_zone_id == "zone-4"
