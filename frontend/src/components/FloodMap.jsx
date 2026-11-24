import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { FaWater, FaExclamationTriangle, FaClock, FaCheckCircle, FaTimesCircle } from "react-icons/fa";

// Create custom pin icons based on risk and freshness
function createCustomPin(risk = "LOW", freshness = "RECENT") {
  let color = "#10b981"; // Emerald / Green for LOW
  let borderColor = "#047857";
  let pulse = false;

  if (freshness === "STALE" || freshness === "UNAVAILABLE") {
    color = "#94a3b8"; // Slate / Grey
    borderColor = "#64748b";
  } else if (risk === "EXTREME") {
    color = "#dc2626"; // Red
    borderColor = "#991b1b";
    pulse = true;
  } else if (risk === "HIGH") {
    color = "#ea580c"; // Orange
    borderColor = "#c2410c";
  } else if (risk === "MEDIUM") {
    color = "#d97706"; // Amber / Yellow
    borderColor = "#b45309";
  }

  const pulseClass = pulse ? "animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;" : "";

  return L.divIcon({
    className: "custom-flood-marker",
    html: `
      <div style="position: relative; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center;">
        ${pulse ? `<span style="position: absolute; width: 34px; height: 34px; border-radius: 9999px; background-color: ${color}; opacity: 0.35; ${pulseClass}"></span>` : ""}
        <span style="width: 20px; height: 20px; border-radius: 9999px; background-color: ${color}; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.35); display: block;"></span>
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -14],
  });
}

export default function FloodMap({ stations = [], onSelectStation, selectedStationId }) {
  const [filterBasin, setFilterBasin] = useState("ALL");
  const [filterRisk, setFilterRisk] = useState("ALL");

  // Center of Yadgir District: ~16.74° N, 77.05° E
  const yadgirCenter = [16.7400, 77.0500];

  const filteredStations = stations.filter((st) => {
    if (filterBasin !== "ALL" && st.basin !== filterBasin) return false;
    if (filterRisk !== "ALL" && st.risk !== filterRisk) return false;
    return true;
  });

  const basins = ["ALL", ...Array.from(new Set(stations.map((s) => s.basin).filter(Boolean)))];

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xs sm:p-5">
      {/* Header and map controls */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900 sm:text-xl">
            Yadgir District River Network & Flood Risk Map
          </h2>
          <p className="text-xs text-slate-500">
            Continuous telemetry and ML risk classification across Yadgir district & upstream inflows ({filteredStations.length} stations active)
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Basin selector */}
          <select
            value={filterBasin}
            onChange={(e) => setFilterBasin(e.target.value)}
            className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 outline-none focus:border-blue-500"
          >
            {basins.map((b) => (
              <option key={b} value={b}>
                {b === "ALL" ? "All Basins" : b}
              </option>
            ))}
          </select>

          {/* Risk selector */}
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 outline-none focus:border-blue-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="EXTREME">Extreme Risk</option>
          </select>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-100">
        <MapContainer
          center={yadgirCenter}
          zoom={9}
          scrollWheelZoom={false}
          style={{ height: "480px", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {filteredStations.map((station) => {
            if (!station.latitude || !station.longitude) return null;
            const icon = createCustomPin(station.risk, station.freshness);

            return (
              <Marker
                key={station.station_id}
                position={[station.latitude, station.longitude]}
                icon={icon}
              >
                <Popup className="custom-station-popup">
                  <div className="p-1 text-slate-900 max-w-[280px]">
                    {/* Header */}
                    <div className="flex items-start justify-between border-b border-slate-100 pb-2">
                      <div>
                        <h3 className="text-sm font-bold text-slate-900">{station.station_name}</h3>
                        <p className="text-[11px] text-slate-500 font-medium">
                          {station.river} River · {station.basin}
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${
                          station.risk === "EXTREME"
                            ? "bg-red-100 text-red-700"
                            : station.risk === "HIGH"
                            ? "bg-orange-100 text-orange-700"
                            : station.risk === "MEDIUM"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {station.risk}
                      </span>
                    </div>

                    {/* Freshness Badge */}
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500">Status</span>
                      <span
                        className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${
                          station.freshness === "RECENT"
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${
                            station.freshness === "RECENT" ? "bg-emerald-500" : "bg-slate-400"
                          }`}
                        />
                        {station.freshness} ({station.data_age})
                      </span>
                    </div>

                    {/* Metrics Grid */}
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                      <div className="rounded-lg bg-slate-50 p-1.5">
                        <span className="text-[10px] text-slate-500 block">Water Level</span>
                        <span className="font-bold text-slate-900">
                          {station.water_level != null ? `${Number(station.water_level).toFixed(2)} m` : "N/A"}
                        </span>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-1.5">
                        <span className="text-[10px] text-slate-500 block">Discharge</span>
                        <span className="font-bold text-slate-900">
                          {station.discharge != null ? `${Number(station.discharge).toFixed(1)} m³/s` : "N/A"}
                        </span>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-1.5">
                        <span className="text-[10px] text-slate-500 block">Warning Level</span>
                        <span className="font-semibold text-slate-700">
                          {station.warning_level != null ? `${Number(station.warning_level).toFixed(1)} m` : "Unlisted"}
                        </span>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-1.5">
                        <span className="text-[10px] text-slate-500 block">Danger Level</span>
                        <span className="font-semibold text-slate-700">
                          {station.danger_level != null ? `${Number(station.danger_level).toFixed(1)} m` : "Unlisted"}
                        </span>
                      </div>
                    </div>

                    {/* Source and Updated */}
                    <div className="mt-2 text-[10px] text-slate-400">
                      <span>Source: {station.source}</span> · <span>Updated: {station.last_updated}</span>
                    </div>

                    {/* Action Button */}
                    {onSelectStation && (
                      <button
                        type="button"
                        onClick={() => onSelectStation(station.station_id)}
                        className="mt-2 w-full rounded-lg bg-blue-600 px-3 py-1.5 text-center text-xs font-semibold text-white hover:bg-blue-700 transition"
                      >
                        View Full Details & Trends
                      </button>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Legend */}
        <div className="absolute bottom-3 right-3 z-[1000] rounded-xl bg-white/95 p-2.5 shadow-md backdrop-blur border border-slate-200 text-xs">
          <p className="font-bold text-slate-800 text-[11px] mb-1.5">Risk Status Legend</p>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[10px]">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 inline-block"></span>
              <span className="text-slate-600 font-medium">Low Risk</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500 inline-block"></span>
              <span className="text-slate-600 font-medium">Medium</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-orange-500 inline-block"></span>
              <span className="text-slate-600 font-medium">High Risk</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-red-600 inline-block"></span>
              <span className="text-slate-600 font-medium">Extreme</span>
            </div>
            <div className="flex items-center gap-1.5 col-span-2 pt-0.5 border-t border-slate-100">
              <span className="h-2.5 w-2.5 rounded-full bg-slate-400 inline-block"></span>
              <span className="text-slate-500 font-medium">Stale / Unavailable</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
