import math
from typing import List, Dict, Any, Tuple
from app.models.schemas import RescueTeam, Zone, RoadSegment, RoadStatus
from app.data.flood_dataset import ROADS_DATA

class RouteEstimator:
    """
    Deterministic Routing and Travel Time Estimator for Disaster Response Fleet.
    Models terrain degradation, road network passability, flood depths, and vehicle/boat capabilities.
    """
    def __init__(self, roads: List[RoadSegment] = None):
        self.roads = roads or ROADS_DATA

    def calculate_euclidean_distance_km(self, loc1: List[float], loc2: List[float]) -> float:
        """
        Calculates approximate geographical distance in km for local coordinates
        (1 deg lat ~ 111.0 km, 1 deg lng ~ 108.0 km around Bangalore/Karnataka coordinates).
        """
        d_lng = (loc1[0] - loc2[0]) * 108.0
        d_lat = (loc1[1] - loc2[1]) * 111.0
        dist = math.sqrt(d_lat * d_lat + d_lng * d_lng)
        return max(0.5, round(dist, 1))

    def estimate_travel_metrics(
        self,
        team: RescueTeam,
        zone: Zone
    ) -> Dict[str, Any]:
        """
        Calculates realistic travel time, road impact level, and route safety.
        Takes into account deep water barriers, road blockages, and specialized team mobility.
        """
        distance_km = self.calculate_euclidean_distance_km(team.location_coordinates, zone.center)
        normal_speed_kmh = 40.0
        normal_eta_min = max(3, round((distance_km / normal_speed_kmh) * 60))

        flood_depth = zone.current_flood_depth_cm
        road_access = zone.road_accessibility_percent

        # Determine effective speed and condition impact based on assets
        if getattr(team, 'has_amphibious', False) or (getattr(team, 'unit_type', '') and 'Air' in team.unit_type):
            if 'Air' in getattr(team, 'unit_type', ''):
                effective_speed_kmh = 100.0
                impact_label = "AERIAL TRANSIT (CLEAR)"
                route_safety = 98
            else:
                effective_speed_kmh = 28.0
                impact_label = "AMPHIBIOUS TERRAIN BYPASS"
                route_safety = 94
        elif team.has_boat:
            if flood_depth >= 60.0:
                effective_speed_kmh = 22.0
                impact_label = "DEEP FLOOD WATERWAY TRANSIT"
                route_safety = 90
            elif road_access < 40:
                effective_speed_kmh = 18.0
                impact_label = "HIGH IMPACT / HYBRID BOAT TRANSIT"
                route_safety = 85
            else:
                effective_speed_kmh = 30.0
                impact_label = "MODERATE FLOOD CONDITIONS"
                route_safety = 88
        else:
            # Land vehicle / foot without boat in flooded or blocked zone
            if flood_depth >= 75.0 or road_access <= 25:
                effective_speed_kmh = 7.0
                impact_label = "CRITICAL IMPASSABLE WATERWAYS"
                route_safety = 25
            elif flood_depth >= 40.0 or road_access <= 55:
                effective_speed_kmh = 12.0
                impact_label = "SEVERE ROAD DEGRADATION"
                route_safety = 50
            else:
                effective_speed_kmh = 28.0
                impact_label = "MINOR ROAD IMPACT"
                route_safety = max(60, road_access)

        estimated_eta_min = max(4, round((distance_km / effective_speed_kmh) * 60))

        # Generate deterministic waypoints for tactical map rendering
        waypoints = self._generate_route_waypoints(team.location_coordinates, zone.center)

        return {
            "distance_km": distance_km,
            "normal_eta_minutes": normal_eta_min,
            "travel_time_minutes": estimated_eta_min,
            "road_condition_impact": impact_label,
            "route_safety_score": route_safety,
            "effective_speed_kmh": effective_speed_kmh,
            "route_waypoints": waypoints
        }

    def _generate_route_waypoints(self, start: List[float], end: List[float]) -> List[List[float]]:
        """
        Generates realistic intermediate navigation waypoints between team and zone center.
        """
        mid_x = (start[0] + end[0]) / 2.0
        mid_y = (start[1] + end[1]) / 2.0
        # Add slight tactical curve offset for GIS route visualization
        offset_x = (end[1] - start[1]) * 0.15
        offset_y = -(end[0] - start[0]) * 0.15
        wp1 = [round(start[0] * 0.75 + end[0] * 0.25 + offset_x * 0.5, 4), round(start[1] * 0.75 + end[1] * 0.25 + offset_y * 0.5, 4)]
        wp2 = [round(mid_x + offset_x, 4), round(mid_y + offset_y, 4)]
        wp3 = [round(start[0] * 0.25 + end[0] * 0.75 + offset_x * 0.5, 4), round(start[1] * 0.25 + end[1] * 0.75 + offset_y * 0.5, 4)]
        return [
            [round(start[0], 4), round(start[1], 4)],
            wp1,
            wp2,
            wp3,
            [round(end[0], 4), round(end[1], 4)]
        ]

route_estimator = RouteEstimator()
