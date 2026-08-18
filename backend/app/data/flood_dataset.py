import datetime
from typing import List, Dict
from app.models.schemas import (
    Zone, RoadSegment, Infrastructure, RescueTeam, DisasterEvent,
    ConnectivityStatus, RoadStatus, InfraType, InfraStatus, GeoPolygon
)

# Deterministic Simulation Baseline Dataset for Urban Flood (River Basin District)
SIMULATION_TIMESTAMP = "2026-08-15T10:00:00Z"

# 12 Geographic Zones
ZONES_DATA: List[Zone] = [
    Zone(
        id="zone-1",
        code="Z-01",
        name="Zone 1 — Downtown Core & Civic Center",
        district="Central Basin",
        population=18500,
        elevation_meters=18.5,
        current_flood_depth_cm=25.0,
        rainfall_rate_mmh=42.0,
        river_level_meters=4.2,
        primary_risk_score=38,
        secondary_risks={"power": 20, "medical": 15, "water": 25, "telecom": 10, "roads": 30},
        cascading_risk_score=42,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=88,
        hospital_accessibility_percent=92,
        sos_reports_last_hour=14,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.580, 12.960], [77.605, 12.960], [77.605, 12.980], [77.580, 12.980], [77.580, 12.960]
        ]]),
        center=[77.5925, 12.9700],
        is_silent_risk=False,
        silent_risk_score=12,
        escalation_time_minutes=120,
        predicted_risk_60m=48
    ),
    Zone(
        id="zone-2",
        code="Z-02",
        name="Zone 2 — North River Terrace",
        district="Upper River District",
        population=12400,
        elevation_meters=14.2,
        current_flood_depth_cm=55.0,
        rainfall_rate_mmh=58.0,
        river_level_meters=6.1,
        primary_risk_score=64,
        secondary_risks={"power": 45, "medical": 50, "water": 60, "telecom": 20, "roads": 65},
        cascading_risk_score=68,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=65,
        hospital_accessibility_percent=70,
        sos_reports_last_hour=29,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.580, 12.980], [77.605, 12.980], [77.605, 13.005], [77.580, 13.005], [77.580, 12.980]
        ]]),
        center=[77.5925, 12.9925],
        is_silent_risk=False,
        silent_risk_score=18,
        escalation_time_minutes=75,
        predicted_risk_60m=76
    ),
    Zone(
        id="zone-3",
        code="Z-03",
        name="Zone 3 — East Medical Corridor",
        district="East Heights",
        population=14200,
        elevation_meters=19.8,
        current_flood_depth_cm=18.0,
        rainfall_rate_mmh=38.0,
        river_level_meters=3.8,
        primary_risk_score=32,
        secondary_risks={"power": 25, "medical": 30, "water": 15, "telecom": 10, "roads": 35},
        cascading_risk_score=36,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=90,
        hospital_accessibility_percent=95,
        sos_reports_last_hour=8,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.605, 12.960], [77.635, 12.960], [77.635, 12.980], [77.605, 12.980], [77.605, 12.960]
        ]]),
        center=[77.6200, 12.9700],
        is_silent_risk=False,
        silent_risk_score=8,
        escalation_time_minutes=180,
        predicted_risk_60m=40
    ),
    Zone(
        id="zone-4",
        code="Z-04",
        name="Zone 4 — Riverside Slums & Wetlands",
        district="West Marshlands",
        population=9300,
        elevation_meters=8.1,
        current_flood_depth_cm=145.0,
        rainfall_rate_mmh=78.0,
        river_level_meters=8.4,
        primary_risk_score=92,
        secondary_risks={"power": 95, "medical": 90, "water": 98, "telecom": 100, "roads": 96},
        cascading_risk_score=94,
        connectivity_status=ConnectivityStatus.LOST,
        road_accessibility_percent=12,
        hospital_accessibility_percent=15,
        sos_reports_last_hour=0, # SILENT CRISIS: Tower down!
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.550, 12.960], [77.580, 12.960], [77.580, 12.985], [77.550, 12.985], [77.550, 12.960]
        ]]),
        center=[77.5650, 12.9725],
        is_silent_risk=True,
        silent_risk_score=91,
        escalation_time_minutes=25,
        predicted_risk_60m=98
    ),
    Zone(
        id="zone-5",
        code="Z-05",
        name="Zone 5 — North-East Highland Shelters",
        district="Upper Plateau",
        population=8100,
        elevation_meters=24.5,
        current_flood_depth_cm=10.0,
        rainfall_rate_mmh=32.0,
        river_level_meters=3.1,
        primary_risk_score=22,
        secondary_risks={"power": 15, "medical": 20, "water": 10, "telecom": 5, "roads": 25},
        cascading_risk_score=24,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=95,
        hospital_accessibility_percent=92,
        sos_reports_last_hour=5,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.605, 12.980], [77.635, 12.980], [77.635, 13.005], [77.605, 13.005], [77.605, 12.980]
        ]]),
        center=[77.6200, 12.9925],
        is_silent_risk=False,
        silent_risk_score=6,
        escalation_time_minutes=240,
        predicted_risk_60m=28
    ),
    Zone(
        id="zone-6",
        code="Z-06",
        name="Zone 6 — South Power & Industrial Hub",
        district="South Basin",
        population=11200,
        elevation_meters=11.4,
        current_flood_depth_cm=70.0,
        rainfall_rate_mmh=62.0,
        river_level_meters=6.8,
        primary_risk_score=72,
        secondary_risks={"power": 85, "medical": 65, "water": 70, "telecom": 40, "roads": 75},
        cascading_risk_score=79,
        connectivity_status=ConnectivityStatus.DEGRADED,
        road_accessibility_percent=52,
        hospital_accessibility_percent=58,
        sos_reports_last_hour=21,
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.580, 12.935], [77.605, 12.935], [77.605, 12.960], [77.580, 12.960], [77.580, 12.935]
        ]]),
        center=[77.5925, 12.9475],
        is_silent_risk=False,
        silent_risk_score=34,
        escalation_time_minutes=55,
        predicted_risk_60m=84
    ),
    Zone(
        id="zone-7",
        code="Z-07",
        name="Zone 7 — River Bend Lowlands & Hospital Delta",
        district="Central River Basin",
        population=8240,
        elevation_meters=9.2,
        current_flood_depth_cm=95.0,
        rainfall_rate_mmh=74.0,
        river_level_meters=7.9,
        primary_risk_score=82,
        secondary_risks={"power": 72, "medical": 81, "water": 64, "telecom": 58, "roads": 91},
        cascading_risk_score=87,
        connectivity_status=ConnectivityStatus.DEGRADED,
        road_accessibility_percent=42,
        hospital_accessibility_percent=61,
        sos_reports_last_hour=48,
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.550, 12.935], [77.580, 12.935], [77.580, 12.960], [77.550, 12.960], [77.550, 12.935]
        ]]),
        center=[77.5650, 12.9475],
        is_silent_risk=False,
        silent_risk_score=45,
        escalation_time_minutes=42, # PREDICTED TO ISOLATE IN 42 MINUTES!
        predicted_risk_60m=94
    ),
    Zone(
        id="zone-8",
        code="Z-08",
        name="Zone 8 — East Lake View & Residential",
        district="East Heights",
        population=13600,
        elevation_meters=17.0,
        current_flood_depth_cm=30.0,
        rainfall_rate_mmh=45.0,
        river_level_meters=4.0,
        primary_risk_score=44,
        secondary_risks={"power": 30, "medical": 35, "water": 40, "telecom": 20, "roads": 45},
        cascading_risk_score=46,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=82,
        hospital_accessibility_percent=85,
        sos_reports_last_hour=16,
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.605, 12.935], [77.635, 12.935], [77.635, 12.960], [77.605, 12.960], [77.605, 12.935]
        ]]),
        center=[77.6200, 12.9475],
        is_silent_risk=False,
        silent_risk_score=14,
        escalation_time_minutes=110,
        predicted_risk_60m=54
    ),
    Zone(
        id="zone-9",
        code="Z-09",
        name="Zone 9 — River Confluence South Outskirts",
        district="Lower Marshlands",
        population=4100,
        elevation_meters=7.4,
        current_flood_depth_cm=110.0,
        rainfall_rate_mmh=70.0,
        river_level_meters=8.1,
        primary_risk_score=88,
        secondary_risks={"power": 90, "medical": 88, "water": 92, "telecom": 95, "roads": 94},
        cascading_risk_score=91,
        connectivity_status=ConnectivityStatus.LOST,
        road_accessibility_percent=18,
        hospital_accessibility_percent=22,
        sos_reports_last_hour=0, # SILENT CRISIS: Tower destroyed!
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.550, 12.910], [77.580, 12.910], [77.580, 12.935], [77.550, 12.935], [77.550, 12.910]
        ]]),
        center=[77.5650, 12.9225],
        is_silent_risk=True,
        silent_risk_score=83,
        escalation_time_minutes=30,
        predicted_risk_60m=95
    ),
    Zone(
        id="zone-10",
        code="Z-10",
        name="Zone 10 — West Transit Junction",
        district="West Basin",
        population=7800,
        elevation_meters=15.6,
        current_flood_depth_cm=45.0,
        rainfall_rate_mmh=50.0,
        river_level_meters=5.2,
        primary_risk_score=52,
        secondary_risks={"power": 40, "medical": 45, "water": 35, "telecom": 20, "roads": 60},
        cascading_risk_score=56,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=72,
        hospital_accessibility_percent=78,
        sos_reports_last_hour=19,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.550, 12.985], [77.580, 12.985], [77.580, 13.005], [77.550, 13.005], [77.550, 12.985]
        ]]),
        center=[77.5650, 12.9950],
        is_silent_risk=False,
        silent_risk_score=15,
        escalation_time_minutes=95,
        predicted_risk_60m=62
    ),
    Zone(
        id="zone-11",
        code="Z-11",
        name="Zone 11 — South-East Forest Buffer",
        district="South Heights",
        population=3500,
        elevation_meters=21.0,
        current_flood_depth_cm=15.0,
        rainfall_rate_mmh=35.0,
        river_level_meters=3.2,
        primary_risk_score=26,
        secondary_risks={"power": 15, "medical": 20, "water": 15, "telecom": 10, "roads": 25},
        cascading_risk_score=28,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=92,
        hospital_accessibility_percent=88,
        sos_reports_last_hour=3,
        active_rescue_teams=1,
        geometry=GeoPolygon(coordinates=[[
            [77.605, 12.910], [77.635, 12.910], [77.635, 12.935], [77.605, 12.935], [77.605, 12.910]
        ]]),
        center=[77.6200, 12.9225],
        is_silent_risk=False,
        silent_risk_score=7,
        escalation_time_minutes=200,
        predicted_risk_60m=32
    ),
    Zone(
        id="zone-12",
        code="Z-12",
        name="Zone 12 — South Canal Catchment",
        district="South Basin",
        population=6900,
        elevation_meters=12.1,
        current_flood_depth_cm=65.0,
        rainfall_rate_mmh=55.0,
        river_level_meters=6.4,
        primary_risk_score=68,
        secondary_risks={"power": 60, "medical": 55, "water": 65, "telecom": 30, "roads": 70},
        cascading_risk_score=71,
        connectivity_status=ConnectivityStatus.NORMAL,
        road_accessibility_percent=60,
        hospital_accessibility_percent=65,
        sos_reports_last_hour=24,
        active_rescue_teams=0,
        geometry=GeoPolygon(coordinates=[[
            [77.580, 12.910], [77.605, 12.910], [77.605, 12.935], [77.580, 12.935], [77.580, 12.910]
        ]]),
        center=[77.5925, 12.9225],
        is_silent_risk=False,
        silent_risk_score=21,
        escalation_time_minutes=68,
        predicted_risk_60m=78
    )
]

# 18 Strategic Road Corridors
ROADS_DATA: List[RoadSegment] = [
    RoadSegment(
        id="road-14",
        name="Corridor 14 (Central River Bridge)",
        from_zone_id="zone-7",
        to_zone_id="zone-1",
        status=RoadStatus.PREDICTED_BLOCKED, # KEY BOTTLENECK IN DEMO
        passability_percent=38,
        elevation_meters=9.5,
        coordinates=[[77.5650, 12.9475], [77.5780, 12.9550], [77.5925, 12.9700]],
        is_critical_hospital_route=True
    ),
    RoadSegment(
        id="road-04",
        name="Marshlands Causeway West",
        from_zone_id="zone-4",
        to_zone_id="zone-10",
        status=RoadStatus.BLOCKED,
        passability_percent=0,
        elevation_meters=7.8,
        coordinates=[[77.5650, 12.9725], [77.5650, 12.9950]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-07",
        name="Arterial Highway 7 South",
        from_zone_id="zone-7",
        to_zone_id="zone-6",
        status=RoadStatus.RESTRICTED,
        passability_percent=45,
        elevation_meters=10.2,
        coordinates=[[77.5650, 12.9475], [77.5925, 12.9475]],
        is_critical_hospital_route=True
    ),
    RoadSegment(
        id="road-09",
        name="Confluence Access Road",
        from_zone_id="zone-9",
        to_zone_id="zone-12",
        status=RoadStatus.BLOCKED,
        passability_percent=10,
        elevation_meters=7.2,
        coordinates=[[77.5650, 12.9225], [77.5925, 12.9225]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-01",
        name="Civic Center Expressway",
        from_zone_id="zone-1",
        to_zone_id="zone-3",
        status=RoadStatus.OPEN,
        passability_percent=95,
        elevation_meters=18.8,
        coordinates=[[77.5925, 12.9700], [77.6200, 12.9700]],
        is_critical_hospital_route=True
    ),
    RoadSegment(
        id="road-02",
        name="North River Link",
        from_zone_id="zone-1",
        to_zone_id="zone-2",
        status=RoadStatus.RESTRICTED,
        passability_percent=60,
        elevation_meters=15.0,
        coordinates=[[77.5925, 12.9700], [77.5925, 12.9925]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-03",
        name="Highland Relief Arterial",
        from_zone_id="zone-3",
        to_zone_id="zone-5",
        status=RoadStatus.OPEN,
        passability_percent=98,
        elevation_meters=22.0,
        coordinates=[[77.6200, 12.9700], [77.6200, 12.9925]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-06",
        name="Industrial Accessway",
        from_zone_id="zone-1",
        to_zone_id="zone-6",
        status=RoadStatus.RESTRICTED,
        passability_percent=55,
        elevation_meters=12.5,
        coordinates=[[77.5925, 12.9700], [77.5925, 12.9475]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-08",
        name="East Lake Ring Road",
        from_zone_id="zone-3",
        to_zone_id="zone-8",
        status=RoadStatus.OPEN,
        passability_percent=90,
        elevation_meters=17.5,
        coordinates=[[77.6200, 12.9700], [77.6200, 12.9475]],
        is_critical_hospital_route=True
    ),
    RoadSegment(
        id="road-10",
        name="West Transit Overpass",
        from_zone_id="zone-10",
        to_zone_id="zone-2",
        status=RoadStatus.OPEN,
        passability_percent=85,
        elevation_meters=16.0,
        coordinates=[[77.5650, 12.9950], [77.5925, 12.9925]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-11",
        name="South-East Green Corridor",
        from_zone_id="zone-8",
        to_zone_id="zone-11",
        status=RoadStatus.OPEN,
        passability_percent=95,
        elevation_meters=19.5,
        coordinates=[[77.6200, 12.9475], [77.6200, 12.9225]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-12",
        name="Canal Bridge Route",
        from_zone_id="zone-6",
        to_zone_id="zone-12",
        status=RoadStatus.RESTRICTED,
        passability_percent=60,
        elevation_meters=11.8,
        coordinates=[[77.5925, 12.9475], [77.5925, 12.9225]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-13",
        name="West Valley Floodway",
        from_zone_id="zone-4",
        to_zone_id="zone-7",
        status=RoadStatus.BLOCKED,
        passability_percent=5,
        elevation_meters=8.0,
        coordinates=[[77.5650, 12.9725], [77.5650, 12.9475]],
        is_critical_hospital_route=False
    ),
    RoadSegment(
        id="road-15",
        name="South Basin Connector",
        from_zone_id="zone-12",
        to_zone_id="zone-11",
        status=RoadStatus.OPEN,
        passability_percent=88,
        elevation_meters=15.0,
        coordinates=[[77.5925, 12.9225], [77.6200, 12.9225]],
        is_critical_hospital_route=False
    )
]

# Critical Infrastructure (Hospitals, Shelters, Power Stations, Pumping Stations, Telecom Towers)
INFRASTRUCTURE_DATA: List[Infrastructure] = [
    # Hospitals
    Infrastructure(
        id="hosp-01",
        name="Central General Hospital & Trauma Center",
        type=InfraType.HOSPITAL,
        zone_id="zone-1",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.5940, 12.9710],
        capacity=650,
        current_load=480,
        has_backup_generator=True,
        flood_barrier_height_cm=150.0,
        current_water_level_cm=15.0,
        details={"icu_beds_free": 24, "surgical_theatres": 8, "helo_pad": True}
    ),
    Infrastructure(
        id="hosp-02",
        name="Riverbank Memorial Hospital (CRITICAL RISK)",
        type=InfraType.HOSPITAL,
        zone_id="zone-7",
        status=InfraStatus.WARNING,
        coordinates=[77.5670, 12.9490],
        capacity=320,
        current_load=295,
        has_backup_generator=True,
        flood_barrier_height_cm=100.0,
        current_water_level_cm=88.0,
        details={"icu_beds_free": 4, "surgical_theatres": 3, "backup_fuel_hours": 6.5, "ground_floor_threatened": True}
    ),
    Infrastructure(
        id="hosp-03",
        name="St. Jude East Trauma Center",
        type=InfraType.HOSPITAL,
        zone_id="zone-3",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.6220, 12.9690],
        capacity=450,
        current_load=310,
        has_backup_generator=True,
        flood_barrier_height_cm=200.0,
        current_water_level_cm=10.0,
        details={"icu_beds_free": 38, "surgical_theatres": 6, "helo_pad": True}
    ),
    Infrastructure(
        id="hosp-04",
        name="Apex Specialty Emergency Center",
        type=InfraType.HOSPITAL,
        zone_id="zone-8",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.6210, 12.9460],
        capacity=280,
        current_load=190,
        has_backup_generator=True,
        flood_barrier_height_cm=180.0,
        current_water_level_cm=20.0,
        details={"icu_beds_free": 18, "surgical_theatres": 4, "helo_pad": False}
    ),

    # Shelters
    Infrastructure(
        id="shelt-01",
        name="Shelter A — North Stadium Complex",
        type=InfraType.SHELTER,
        zone_id="zone-2",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.5910, 12.9940],
        capacity=2500,
        current_load=1420,
        has_backup_generator=True,
        flood_barrier_height_cm=120.0,
        current_water_level_cm=35.0,
        details={"food_rations_days": 5, "medical_post": True}
    ),
    Infrastructure(
        id="shelt-02",
        name="Shelter B — Highland High School Complex",
        type=InfraType.SHELTER,
        zone_id="zone-5",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.6230, 12.9910],
        capacity=3000,
        current_load=850,
        has_backup_generator=True,
        flood_barrier_height_cm=250.0,
        current_water_level_cm=0.0,
        details={"food_rations_days": 8, "medical_post": True, "spare_capacity": 2150}
    ),
    Infrastructure(
        id="shelt-03",
        name="Shelter C — Civic Auditorium",
        type=InfraType.SHELTER,
        zone_id="zone-1",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.5900, 12.9680],
        capacity=1800,
        current_load=1350,
        has_backup_generator=True,
        flood_barrier_height_cm=180.0,
        current_water_level_cm=15.0,
        details={"food_rations_days": 4, "medical_post": True}
    ),
    Infrastructure(
        id="shelt-04",
        name="Shelter D — West Transit Community Center",
        type=InfraType.SHELTER,
        zone_id="zone-10",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.5670, 12.9930],
        capacity=1500,
        current_load=920,
        has_backup_generator=True,
        flood_barrier_height_cm=160.0,
        current_water_level_cm=25.0,
        details={"food_rations_days": 3, "medical_post": False}
    ),

    # Power Stations
    Infrastructure(
        id="pwr-01",
        name="Substation Delta-1 (Main Industrial Grid)",
        type=InfraType.POWER_STATION,
        zone_id="zone-6",
        status=InfraStatus.WARNING,
        coordinates=[77.5930, 12.9450],
        capacity=500,
        current_load=420,
        has_backup_generator=False,
        flood_barrier_height_cm=110.0,
        current_water_level_cm=68.0,
        details={"supplies_pumping_stations": ["pump-01", "pump-02"], "grid_voltage_kv": 220}
    ),
    Infrastructure(
        id="pwr-02",
        name="Riverfront Substation South (CRITICAL)",
        type=InfraType.POWER_STATION,
        zone_id="zone-7",
        status=InfraStatus.COMPROMISED,
        coordinates=[77.5640, 12.9440],
        capacity=300,
        current_load=280,
        has_backup_generator=False,
        flood_barrier_height_cm=90.0,
        current_water_level_cm=92.0, # OVERTOPPED!
        details={"supplies_pumping_stations": ["pump-01"], "grid_voltage_kv": 110, "auto_shutdown_risk": "IMMINENT"}
    ),

    # Pumping Stations
    Infrastructure(
        id="pump-01",
        name="Basin Drainage Pump Station #1",
        type=InfraType.PUMPING_STATION,
        zone_id="zone-7",
        status=InfraStatus.WARNING,
        coordinates=[77.5620, 12.9460],
        capacity=12000, # liters/sec
        current_load=11400,
        has_backup_generator=False,
        flood_barrier_height_cm=100.0,
        current_water_level_cm=91.0,
        details={"flow_rate_m3s": 11.4, "power_source": "pwr-02", "failure_consequence": "Zone 7 backwater surge"}
    ),
    Infrastructure(
        id="pump-02",
        name="North Drain Relief Pump #2",
        type=InfraType.PUMPING_STATION,
        zone_id="zone-4",
        status=InfraStatus.OFFLINE,
        coordinates=[77.5610, 12.9740],
        capacity=8500,
        current_load=0,
        has_backup_generator=False,
        flood_barrier_height_cm=80.0,
        current_water_level_cm=140.0, # SUBMERGED
        details={"flow_rate_m3s": 0.0, "status_note": "Submerged, power severed"}
    ),

    # Telecom Towers
    Infrastructure(
        id="tower-01",
        name="Tower Alpha (Civic Central)",
        type=InfraType.TELECOM_TOWER,
        zone_id="zone-1",
        status=InfraStatus.OPERATIONAL,
        coordinates=[77.5910, 12.9730],
        capacity=50000,
        current_load=38000,
        has_backup_generator=True,
        flood_barrier_height_cm=300.0,
        current_water_level_cm=0.0,
        details={"coverage_radius_km": 4.5, "cellular_bands": ["5G", "4G", "LTE-M"]}
    ),
    Infrastructure(
        id="tower-04",
        name="Tower Delta-4 (Riverside Slums) — BLACKOUT",
        type=InfraType.TELECOM_TOWER,
        zone_id="zone-4",
        status=InfraStatus.OFFLINE,
        coordinates=[77.5630, 12.9710],
        capacity=25000,
        current_load=0,
        has_backup_generator=False,
        flood_barrier_height_cm=50.0,
        current_water_level_cm=145.0, # DESTROYED BY FLOOD
        details={"status_note": "Tower base flooded, power offline. Causing Zone 4 Silent Crisis."}
    ),
    Infrastructure(
        id="tower-09",
        name="Tower Gamma-9 (Confluence South) — BLACKOUT",
        type=InfraType.TELECOM_TOWER,
        zone_id="zone-9",
        status=InfraStatus.OFFLINE,
        coordinates=[77.5630, 12.9210],
        capacity=15000,
        current_load=0,
        has_backup_generator=False,
        flood_barrier_height_cm=40.0,
        current_water_level_cm=110.0,
        details={"status_note": "Fiber backhaul severed, power failed. Causing Zone 9 Silent Crisis."}
    )
]

# Rescue Teams
RESCUE_TEAMS_DATA: List[RescueTeam] = [
    RescueTeam(
        id="team-r1",
        callsign="Viper-1 (Amphibious Swiftwater)",
        unit_type="Specialized Swiftwater Rescue",
        location_coordinates=[77.5930, 12.9690],
        location_name="Zone 1 — Civic Center Staging Base",
        assigned_zone_id="zone-1",
        has_boat=True,
        has_medical=False, # Demonstrates closest team lacking medical trauma kit
        has_swift_water=True,
        has_amphibious=True,
        crew_size=8,
        evacuation_capacity=12,
        response_speed_kmh=38.0,
        equipment=["Amphibious ARGO-8x8", "Motorized Zodiac", "Sonar Depth Scanner", "Thermal Night Optics"],
        status="ready",
        current_eta_minutes=8
    ),
    RescueTeam(
        id="team-r2",
        callsign="Delta-2 (Heavy Evacuation Unit)",
        unit_type="Mass Evacuation & Flood Transport",
        location_coordinates=[77.5920, 12.9930],
        location_name="Zone 2 — North Stadium Depot",
        assigned_zone_id="zone-2",
        has_boat=True,
        has_medical=True,
        has_swift_water=True,
        has_amphibious=True,
        crew_size=12,
        evacuation_capacity=15,
        response_speed_kmh=32.0,
        equipment=["High-Water 6x6 Troop Transporter", "Dual Rigid-Inflatable Boats", "Field Trauma Stabilization Station", "Portable Defibrillators"],
        status="ready",
        current_eta_minutes=14
    ),
    RescueTeam(
        id="team-r3",
        callsign="Medic-3 (Trauma Response)",
        unit_type="Advanced Field Medical Corps",
        location_coordinates=[77.6210, 12.9680],
        location_name="Zone 3 — St. Jude Trauma Base",
        assigned_zone_id="zone-3",
        has_boat=False,
        has_medical=True,
        has_swift_water=False,
        has_amphibious=False,
        crew_size=6,
        evacuation_capacity=6,
        response_speed_kmh=40.0,
        equipment=["Mobile ICU Van", "Ventilators", "Blood Warmers", "Surgical Field Kits"],
        status="ready",
        current_eta_minutes=12
    ),
    RescueTeam(
        id="team-r4",
        callsign="Guardian-4 (Tactical Flood Medic)",
        unit_type="Tactical Flood & Paramedic Unit",
        location_coordinates=[77.6220, 12.9900],
        location_name="Zone 5 — Highland High Base",
        assigned_zone_id="zone-5",
        has_boat=True,
        has_medical=True,
        has_swift_water=True,
        has_amphibious=False,
        crew_size=10,
        evacuation_capacity=15,
        response_speed_kmh=35.0,
        equipment=["Zodiac MilPro Inflatable", "Advanced Paramedic Trauma Packs", "High-Angle Rope Rescue Rig", "Submersible Flood Pumps"],
        status="ready",
        current_eta_minutes=16
    ),
    RescueTeam(
        id="team-r5",
        callsign="Bravo-5 (Inflatable Zodiac Squad)",
        unit_type="Light Zodiac Rescue",
        location_coordinates=[77.5660, 12.9940],
        location_name="Zone 10 — West Transit Staging",
        assigned_zone_id="zone-10",
        has_boat=True,
        has_medical=False,
        has_swift_water=True,
        has_amphibious=False,
        crew_size=6,
        evacuation_capacity=8,
        response_speed_kmh=30.0,
        equipment=["Twin 40HP Inflatables", "PFDs & Throw Bags", "Submersible LED Floodlights"],
        status="ready",
        current_eta_minutes=10
    ),
    RescueTeam(
        id="team-r6",
        callsign="AirMed-6 (Heli-Winch Medical)",
        unit_type="Air Cavalry Medevac",
        location_coordinates=[77.6210, 12.9210],
        location_name="Zone 11 — South Forest Helipad",
        assigned_zone_id="zone-11",
        has_boat=False,
        has_medical=True,
        has_swift_water=False,
        has_amphibious=False,
        crew_size=4,
        evacuation_capacity=4,
        response_speed_kmh=120.0,
        equipment=["Winch Hoist System", "Aviation Paramedic Rig", "Stretcher Baskets"],
        status="ready",
        current_eta_minutes=6
    )
]

# Overall Event State
CURRENT_EVENT: DisasterEvent = DisasterEvent(
    id="event-urban-flood-01",
    title="Monsoon Urban Flash Flood & River Crest",
    disaster_type="URBAN FLOOD",
    status="ESCALATING",
    simulation_label="SIMULATION / DEMONSTRATION DATA",
    river_basin="River Basin District — Zone 1 to Zone 12",
    peak_crest_time_hours=2.4,
    average_rainfall_rate_mmh=54.5,
    total_population_exposed=11800,
    active_missions_count=4,
    silent_risk_zones_count=2, # Zone 4 & Zone 9
    system_confidence_percent=89,
    last_updated_timestamp=SIMULATION_TIMESTAMP
)
