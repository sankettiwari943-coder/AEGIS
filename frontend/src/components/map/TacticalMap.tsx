import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { Zone, RoadSegment, Infrastructure, RescueTeam } from '../../types';
import { 
  Layers, 
  Eye, 
  EyeOff, 
  Radio, 
  ShieldAlert, 
  Activity, 
  Maximize2, 
  Minimize2,
  Navigation,
  Compass,
  Zap,
  Info
} from 'lucide-react';

interface TacticalMapProps {
  zones: Zone[];
  roads: RoadSegment[];
  infrastructure: Infrastructure[];
  teams: RescueTeam[];
  selectedZoneId?: string;
  onSelectZone: (zone: Zone) => void;
  onSelectTeam?: (team: RescueTeam) => void;
  highlightSilentRisk?: boolean;
  predictionHorizonMinutes?: number;
  activeMissionRoute?: [number, number][];
  activeMissionTeamCallsign?: string;
}

export const TacticalMap: React.FC<TacticalMapProps> = ({
  zones,
  roads,
  infrastructure,
  teams,
  selectedZoneId,
  onSelectZone,
  onSelectTeam,
  highlightSilentRisk = false,
  predictionHorizonMinutes = 0,
  activeMissionRoute,
  activeMissionTeamCallsign
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  // Layer Visibility States
  const [layers, setLayers] = useState({
    floodIntensity: true,
    populationExposure: true,
    roads: true,
    infrastructure: true,
    rescueTeams: true,
    silentRisk: true,
    predictions: true,
  });

  const [showLayerPanel, setShowLayerPanel] = useState(false);

  // Initialize MapLibre GL Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Tactical Dark Cartography Style using CARTO Dark Matter raster tiles
    const darkStyle: maplibregl.StyleSpecification = {
      version: 8,
      sources: {
        'carto-dark': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'
          ],
          tileSize: 256,
          attribution: '© OpenStreetMap, © CARTO'
        }
      },
      layers: [
        {
          id: 'carto-dark-layer',
          type: 'raster',
          source: 'carto-dark',
          minzoom: 0,
          maxzoom: 19
        }
      ]
    };

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: darkStyle,
      center: [77.5925, 12.9600],
      zoom: 12.35,
      pitch: 35,
      bearing: -8,
      attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
    mapRef.current = map;

    map.on('load', () => {
      renderMapGeoJSON(map);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update GeoJSON Layers whenever zones / roads / horizon / mission route change
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    renderMapGeoJSON(mapRef.current);
  }, [zones, roads, layers, selectedZoneId, predictionHorizonMinutes, activeMissionRoute]);

  // Update HTML Markers (Infrastructure & Rescue Teams)
  useEffect(() => {
    if (!mapRef.current) return;
    renderMarkers(mapRef.current);
  }, [infrastructure, teams, layers]);

  const renderMapGeoJSON = (map: maplibregl.Map) => {
    // 1. Prepare Zones GeoJSON Feature Collection
    const zoneFeatures = zones.map((z) => {
      let activeRisk = z.primary_risk_score;
      if (predictionHorizonMinutes >= 180) {
        activeRisk = Math.min(99, z.predicted_risk_60m + 5);
      } else if (predictionHorizonMinutes >= 60) {
        activeRisk = z.predicted_risk_60m;
      } else if (predictionHorizonMinutes >= 30) {
        activeRisk = Math.min(97, Math.round(z.primary_risk_score + (z.predicted_risk_60m - z.primary_risk_score) * 0.5));
      }

      return {
        type: 'Feature',
        properties: {
          id: z.id,
          code: z.code,
          name: z.name,
          risk: activeRisk,
          predictedRisk: z.predicted_risk_60m,
          cascadingRisk: z.cascading_risk_score,
          floodDepth: z.current_flood_depth_cm,
          population: z.population,
          isSilent: z.is_silent_risk,
          isSelected: z.id === selectedZoneId,
          horizon: predictionHorizonMinutes
        },
        geometry: z.geometry
      };
    });

    const zonesGeoJSON: any = {
      type: 'FeatureCollection',
      features: zoneFeatures
    };

    if (map.getSource('zones-source')) {
      (map.getSource('zones-source') as maplibregl.GeoJSONSource).setData(zonesGeoJSON);
    } else {
      map.addSource('zones-source', {
        type: 'geojson',
        data: zonesGeoJSON
      });

      // Flood Intensity Fill Layer (LOW, MODERATE, HIGH, CRITICAL)
      map.addLayer({
        id: 'zones-fill',
        type: 'fill',
        source: 'zones-source',
        paint: {
          'fill-color': [
            'case',
            ['get', 'isSilent'], '#b91c1c',
            ['>=', ['get', 'risk'], 80], '#dc2626',
            ['>=', ['get', 'risk'], 60], '#d97706',
            ['>=', ['get', 'risk'], 35], '#2563eb',
            '#059669'
          ],
          'fill-opacity': [
            'case',
            ['get', 'isSelected'], 0.70,
            ['get', 'isSilent'], 0.60,
            0.40
          ]
        }
      });

      // Zone Borders / Outlines with Selection Glow
      map.addLayer({
        id: 'zones-outline',
        type: 'line',
        source: 'zones-source',
        paint: {
          'line-color': [
            'case',
            ['get', 'isSelected'], '#00f0ff',
            ['get', 'isSilent'], '#ff0055',
            '#38bdf8'
          ],
          'line-width': [
            'case',
            ['get', 'isSelected'], 4.0,
            ['get', 'isSilent'], 3.0,
            1.5
          ],
          'line-dasharray': [
            'case',
            ['get', 'isSilent'], ['literal', [2, 2]],
            ['literal', [1, 0]]
          ]
        }
      });

      // Zone Labels (Code + Risk Badge)
      map.addLayer({
        id: 'zones-labels',
        type: 'symbol',
        source: 'zones-source',
        layout: {
          'text-field': [
            'case',
            ['get', 'isSilent'],
            ['concat', ['get', 'code'], '\n[SILENT 91%]'],
            ['concat', ['get', 'code'], '\nRISK: ', ['to-string', ['get', 'risk']]]
          ],
          'text-size': 11,
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-anchor': 'center'
        },
        paint: {
          'text-color': [
            'case',
            ['get', 'isSilent'], '#ff6b81',
            ['>=', ['get', 'risk'], 80], '#fca5a5',
            ['>=', ['get', 'risk'], 60], '#fcd34d',
            '#e0f2fe'
          ],
          'text-halo-color': '#070b12',
          'text-halo-width': 2.5
        }
      });

      // Click Interaction on Zone
      map.on('click', 'zones-fill', (e) => {
        if (e.features && e.features[0]) {
          const clickedId = e.features[0].properties.id;
          const found = zones.find((z) => z.id === clickedId);
          if (found) onSelectZone(found);
        }
      });

      map.on('mouseenter', 'zones-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'zones-fill', () => {
        map.getCanvas().style.cursor = '';
      });
    }

    // 2. Prepare Roads GeoJSON Feature Collection
    const roadFeatures = roads.map((r) => ({
      type: 'Feature',
      properties: {
        id: r.id,
        name: r.name,
        status: r.status,
        passability: r.passability_percent,
        isHospitalRoute: r.is_critical_hospital_route
      },
      geometry: {
        type: 'LineString',
        coordinates: r.coordinates
      }
    }));

    const roadsGeoJSON: any = {
      type: 'FeatureCollection',
      features: roadFeatures
    };

    if (map.getSource('roads-source')) {
      (map.getSource('roads-source') as maplibregl.GeoJSONSource).setData(roadsGeoJSON);
    } else {
      map.addSource('roads-source', {
        type: 'geojson',
        data: roadsGeoJSON
      });

      // Roads Line Layer
      map.addLayer({
        id: 'roads-line',
        type: 'line',
        source: 'roads-source',
        layout: {
          'line-cap': 'round',
          'line-join': 'round'
        },
        paint: {
          'line-color': [
            'match',
            ['get', 'status'],
            'blocked', '#ef4444',
            'predicted_blocked', '#f97316',
            'restricted', '#f59e0b',
            'open', '#10b981',
            '#00f0ff'
          ],
          'line-width': [
            'case',
            ['get', 'isHospitalRoute'], 5.0,
            3.5
          ],
          'line-dasharray': [
            'match',
            ['get', 'status'],
            'predicted_blocked', ['literal', [2, 2]],
            'blocked', ['literal', [1, 1]],
            ['literal', [1, 0]]
          ]
        }
      });
    }

    // 3. Active Mission Route Polyline Layer
    const missionFeatures = activeMissionRoute && activeMissionRoute.length >= 2 ? [{
      type: 'Feature' as const,
      properties: {
        team: activeMissionTeamCallsign || 'Rescue Unit'
      },
      geometry: {
        type: 'LineString' as const,
        coordinates: activeMissionRoute
      }
    }] : [];

    const missionGeoJSON: any = {
      type: 'FeatureCollection',
      features: missionFeatures
    };

    if (map.getSource('mission-route-source')) {
      (map.getSource('mission-route-source') as maplibregl.GeoJSONSource).setData(missionGeoJSON);
    } else {
      map.addSource('mission-route-source', {
        type: 'geojson',
        data: missionGeoJSON
      });

      // Glow layer
      map.addLayer({
        id: 'mission-route-glow',
        type: 'line',
        source: 'mission-route-source',
        paint: {
          'line-color': '#00f0ff',
          'line-width': 8,
          'line-opacity': 0.45,
          'line-blur': 4
        }
      });

      // Core pulsing line layer
      map.addLayer({
        id: 'mission-route-line',
        type: 'line',
        source: 'mission-route-source',
        layout: {
          'line-cap': 'round',
          'line-join': 'round'
        },
        paint: {
          'line-color': '#10b981',
          'line-width': 4,
          'line-dasharray': [2, 2]
        }
      });
    }

    // Set Visibility based on Layer Toggles
    if (map.getLayer('zones-fill')) {
      map.setLayoutProperty('zones-fill', 'visibility', layers.floodIntensity ? 'visible' : 'none');
    }
    if (map.getLayer('roads-line')) {
      map.setLayoutProperty('roads-line', 'visibility', layers.roads ? 'visible' : 'none');
    }
    if (map.getLayer('mission-route-line')) {
      map.setLayoutProperty('mission-route-line', 'visibility', activeMissionRoute ? 'visible' : 'none');
    }
    if (map.getLayer('mission-route-glow')) {
      map.setLayoutProperty('mission-route-glow', 'visibility', activeMissionRoute ? 'visible' : 'none');
    }
  };

  const renderMarkers = (map: maplibregl.Map) => {
    // Clear previous markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // Render Infrastructure Markers
    if (layers.infrastructure) {
      infrastructure.forEach((infra) => {
        const el = document.createElement('div');
        el.className = 'tactical-infra-marker cursor-pointer transform transition-transform hover:scale-125';
        
        let iconHtml = '🏥';
        let bgClass = 'bg-blue-600';
        let borderClass = 'border-blue-400';

        if (infra.type === 'hospital') {
          iconHtml = '🏥';
          bgClass = infra.status === 'warning' ? 'bg-amber-600 animate-pulse' : 'bg-blue-600';
          borderClass = infra.status === 'warning' ? 'border-amber-400' : 'border-blue-400';
        } else if (infra.type === 'shelter') {
          iconHtml = '⛺';
          bgClass = 'bg-emerald-600';
          borderClass = 'border-emerald-400';
        } else if (infra.type === 'power_station') {
          iconHtml = '⚡';
          bgClass = infra.status === 'compromised' ? 'bg-red-600 animate-pulse' : 'bg-amber-600';
          borderClass = infra.status === 'compromised' ? 'border-red-400' : 'border-amber-400';
        } else if (infra.type === 'pumping_station') {
          iconHtml = '💧';
          bgClass = infra.status === 'offline' ? 'bg-red-700' : 'bg-cyan-600';
          borderClass = 'border-cyan-400';
        } else if (infra.type === 'telecom_tower') {
          iconHtml = '📡';
          bgClass = infra.status === 'offline' ? 'bg-red-900 border-red-500' : 'bg-indigo-600';
          borderClass = infra.status === 'offline' ? 'border-red-500' : 'border-indigo-400';
        }

        el.innerHTML = `
          <div class="relative flex items-center justify-center w-7 h-7 rounded-full ${bgClass} border-2 ${borderClass} text-white text-xs shadow-lg">
            <span>${iconHtml}</span>
            ${infra.status === 'warning' || infra.status === 'compromised' ? '<span class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>' : ''}
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 15 }).setHTML(`
          <div class="font-mono text-xs p-1">
            <div class="font-bold text-cyan-300 text-[13px]">${infra.name}</div>
            <div class="text-[10px] text-slate-400 uppercase mt-0.5">${infra.type} • Status: <span class="${infra.status === 'operational' ? 'text-emerald-400' : 'text-red-400'} font-bold">${infra.status.toUpperCase()}</span></div>
            <div class="mt-2 pt-1.5 border-t border-slate-700 text-slate-300 space-y-1">
              <div>Capacity / Load: <span class="text-white font-bold">${infra.current_load} / ${infra.capacity}</span></div>
              <div>Water Level: <span class="text-amber-300 font-bold">${infra.current_water_level_cm} cm</span> (Barrier: ${infra.flood_barrier_height_cm} cm)</div>
              <div>Backup Generator: <span class="${infra.has_backup_generator ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}">${infra.has_backup_generator ? 'YES' : 'NONE'}</span></div>
            </div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(infra.coordinates)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      });
    }

    // Render Rescue Teams Markers with Click Support
    if (layers.rescueTeams) {
      teams.forEach((team) => {
        const el = document.createElement('div');
        el.className = 'tactical-team-marker cursor-pointer transform transition-transform hover:scale-125';
        
        el.innerHTML = `
          <div class="relative flex items-center justify-center w-8 h-8 rounded-lg bg-[#070b12] border-2 border-cyan-400 text-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.5)]">
            <span class="text-[10px] font-mono font-black">R${team.id.replace('team-r', '')}</span>
            <span class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${team.status === 'ready' ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse"></span>
          </div>
        `;

        el.addEventListener('click', () => {
          if (onSelectTeam) onSelectTeam(team);
        });

        const popup = new maplibregl.Popup({ offset: 15 }).setHTML(`
          <div class="font-mono text-xs p-1">
            <div class="font-bold text-cyan-300 text-[13px]">${team.callsign}</div>
            <div class="text-[10px] text-slate-400 mt-0.5">${team.unit_type}</div>
            <div class="mt-2 pt-1.5 border-t border-slate-700 text-slate-300 space-y-1">
              <div>Status: <span class="text-emerald-400 font-bold uppercase">${team.status}</span></div>
              <div>Boat: <span class="text-white font-bold">${team.has_boat ? 'YES' : 'NO'}</span> | Medical: <span class="text-white font-bold">${team.has_medical ? 'YES' : 'NO'}</span></div>
              <div>Crew: <span class="text-white font-bold">${team.crew_size} specialists</span></div>
            </div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(team.location_coordinates)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      });
    }
  };

  const toggleLayer = (layerKey: keyof typeof layers) => {
    setLayers((prev) => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  const resetView = () => {
    if (!mapRef.current) return;
    mapRef.current.flyTo({
      center: [77.5925, 12.9600],
      zoom: 12.35,
      pitch: 35,
      bearing: -8,
      essential: true
    });
  };

  return (
    <div className="relative w-full h-full min-h-[480px] rounded-lg overflow-hidden border border-slate-800 bg-[#070b12] shadow-2xl">
      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-full min-h-[480px]" />

      {/* Floating Tactical Map Controls & Layer Switcher */}
      <div className="absolute top-3 left-3 z-10 flex flex-col space-y-2">
        {/* Layer Manager Toggle */}
        <div className="relative">
          <button
            onClick={() => setShowLayerPanel(!showLayerPanel)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-[#070b12]/95 border border-cyan-500/40 hover:border-cyan-400 text-slate-100 text-xs font-mono font-bold shadow-2xl backdrop-blur-md transition-all"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>MAP LAYERS ({Object.values(layers).filter(Boolean).length}/7)</span>
          </button>

          {/* Layer Panel Dropdown */}
          {showLayerPanel && (
            <div className="absolute top-10 left-0 w-64 bg-[#070b12]/95 border border-slate-700 rounded-lg p-3 shadow-2xl backdrop-blur-xl z-20 font-mono text-xs space-y-2">
              <div className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider border-b border-slate-800 pb-1.5 flex justify-between items-center">
                <span>Tactical GIS Layers</span>
                <span className="text-slate-500 text-[10px]">MapLibre GL</span>
              </div>

              <div className="space-y-1.5 pt-1">
                {[
                  { key: 'floodIntensity', label: '1. Flood Intensity (L1)', color: 'text-red-400' },
                  { key: 'populationExposure', label: '2. Population Density (L2)', color: 'text-blue-400' },
                  { key: 'roads', label: '3. Road Network (L3)', color: 'text-emerald-400' },
                  { key: 'infrastructure', label: '4. Critical Infra (L4)', color: 'text-cyan-400' },
                  { key: 'rescueTeams', label: '5. Rescue Teams (L5)', color: 'text-indigo-400' },
                  { key: 'silentRisk', label: '6. Silent-Risk Zones (L6)', color: 'text-pink-400' },
                  { key: 'predictions', label: '7. Escalation Contours (L7)', color: 'text-amber-400' },
                ].map((item) => {
                  const k = item.key as keyof typeof layers;
                  const isActive = layers[k];
                  return (
                    <button
                      key={item.key}
                      onClick={() => toggleLayer(k)}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded transition-all ${
                        isActive ? 'bg-slate-800/80 text-white' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      <span className={item.color}>{item.label}</span>
                      {isActive ? <Eye className="w-3.5 h-3.5 text-cyan-400" /> : <EyeOff className="w-3.5 h-3.5 text-slate-600" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Reset View Button */}
        <button
          onClick={resetView}
          className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md bg-[#070b12]/95 border border-slate-700/80 hover:border-cyan-400 text-slate-300 text-xs font-mono backdrop-blur-md shadow-lg transition-all"
        >
          <Compass className="w-3.5 h-3.5 text-cyan-400" />
          <span>RECENTER</span>
        </button>
      </div>

      {/* Map Legend HUD (Risk States: LOW, MODERATE, HIGH, CRITICAL) */}
      <div className="absolute bottom-3 right-3 z-10 bg-[#070b12]/95 border border-slate-700/80 rounded-md px-3 py-2 text-[10px] font-mono shadow-xl backdrop-blur-md hidden sm:block">
        <div className="font-bold text-slate-300 mb-1 flex items-center justify-between">
          <span>RISK SEVERITY STATES</span>
          <span className="text-[9px] text-cyan-400">12 SECTORS</span>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
            <span className="text-slate-400">LOW</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-blue-600"></span>
            <span className="text-slate-400">MODERATE</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-500"></span>
            <span className="text-slate-400">HIGH</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-red-600 animate-pulse"></span>
            <span className="text-red-400 font-bold">CRITICAL (&gt;80)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
