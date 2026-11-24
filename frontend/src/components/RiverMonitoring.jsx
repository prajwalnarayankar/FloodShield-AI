import React, { useState } from "react";
import { FaSearch, FaFilter, FaWater, FaExclamationTriangle, FaTimes, FaExternalLinkAlt } from "react-icons/fa";
import StationDetailModal from "./StationDetailModal";

export default function RiverMonitoring({ stations = [], onSelectStation, selectedStationDetail, onCloseDetail }) {
  const [search, setSearch] = useState("");
  const [basinFilter, setBasinFilter] = useState("ALL");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [freshnessFilter, setFreshnessFilter] = useState("ALL");

  const basins = ["ALL", ...Array.from(new Set(stations.map((s) => s.basin).filter(Boolean)))];

  const filtered = stations.filter((s) => {
    const q = search.toLowerCase();
    const matchesSearch =
      !q ||
      s.station_name?.toLowerCase().includes(q) ||
      s.river?.toLowerCase().includes(q) ||
      s.district?.toLowerCase().includes(q) ||
      s.basin?.toLowerCase().includes(q);

    const matchesBasin = basinFilter === "ALL" || s.basin === basinFilter;
    const matchesRisk = riskFilter === "ALL" || s.risk === riskFilter;
    const matchesFreshness = freshnessFilter === "ALL" || s.freshness === freshnessFilter;

    return matchesSearch && matchesBasin && matchesRisk && matchesFreshness;
  });

  return (
    <div className="space-y-4">
      {/* Header and Controls */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Yadgir District River Monitoring Network</h2>
            <p className="text-xs text-slate-500">
              Continuous CWC/NWIC telemetry stations across Yadgir district (Bhima & Krishna river system)
            </p>
          </div>

          {/* Search bar */}
          <div className="relative w-full sm:w-72">
            <FaSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs" />
            <input
              type="text"
              placeholder="Search station, river, district..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-xs text-slate-800 outline-none focus:border-blue-500 focus:bg-white transition"
            />
          </div>
        </div>

        {/* Filter Badges */}
        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-500 font-medium">
            <FaFilter className="text-[10px]" />
            <span>Filters:</span>
          </div>

          {/* Basin */}
          <select
            value={basinFilter}
            onChange={(e) => setBasinFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-700 outline-none focus:border-blue-500"
          >
            {basins.map((b) => (
              <option key={b} value={b}>
                {b === "ALL" ? "All Basins" : b}
              </option>
            ))}
          </select>

          {/* Risk */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-700 outline-none focus:border-blue-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="EXTREME">Extreme</option>
          </select>

          {/* Freshness */}
          <select
            value={freshnessFilter}
            onChange={(e) => setFreshnessFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-700 outline-none focus:border-blue-500"
          >
            <option value="ALL">All Data Statuses</option>
            <option value="RECENT">Recent Only</option>
            <option value="STALE">Stale Only</option>
            <option value="UNAVAILABLE">Unavailable</option>
          </select>

          <span className="ml-auto text-[11px] text-slate-400">
            Showing {filtered.length} of {stations.length} stations
          </span>
        </div>
      </div>

      {/* Stations Table */}
      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-50/80 font-bold text-slate-700 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3.5">Station / Location</th>
                <th className="px-4 py-3.5">River / Basin</th>
                <th className="px-4 py-3.5">Water Level</th>
                <th className="px-4 py-3.5">Discharge</th>
                <th className="px-4 py-3.5">Warning / Danger</th>
                <th className="px-4 py-3.5">Risk Level</th>
                <th className="px-4 py-3.5">Data Status</th>
                <th className="px-4 py-3.5">Observation Time</th>
                <th className="px-4 py-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800 font-medium">
              {filtered.map((station) => (
                <tr
                  key={station.station_id}
                  className="hover:bg-slate-50/80 transition-colors"
                >
                  {/* Station Name & District */}
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-900">{station.station_name}</div>
                    <div className="text-[11px] text-slate-500">
                      {station.district || "District Unlisted"} ({station.state})
                    </div>
                  </td>

                  {/* River & Basin */}
                  <td className="px-4 py-3">
                    <div className="font-semibold text-slate-900">{station.river}</div>
                    <div className="text-[11px] text-slate-500">{station.basin}</div>
                  </td>

                  {/* Water Level */}
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-900">
                      {station.water_level != null ? `${Number(station.water_level).toFixed(2)} m` : "N/A"}
                    </div>
                    <span
                      className={`inline-block rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${
                        station.threshold_status === "above danger"
                          ? "bg-red-100 text-red-700"
                          : station.threshold_status === "near danger"
                          ? "bg-orange-100 text-orange-700"
                          : station.threshold_status === "above warning"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {station.threshold_status}
                    </span>
                  </td>

                  {/* Discharge */}
                  <td className="px-4 py-3 font-semibold text-slate-700">
                    {station.discharge != null ? `${Number(station.discharge).toFixed(1)} m³/s` : "—"}
                  </td>

                  {/* Warning / Danger */}
                  <td className="px-4 py-3 text-[11px]">
                    <div>
                      <span className="text-slate-400">W: </span>
                      <span className="font-semibold text-slate-700">
                        {station.warning_level != null ? `${station.warning_level}m` : "—"}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">D: </span>
                      <span className="font-semibold text-slate-700">
                        {station.danger_level != null ? `${station.danger_level}m` : "—"}
                      </span>
                    </div>
                  </td>

                  {/* Risk Badge */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-bold uppercase ${
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
                  </td>

                  {/* Data Status */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          station.freshness === "RECENT"
                            ? "bg-emerald-500"
                            : station.freshness === "STALE"
                            ? "bg-slate-400"
                            : "bg-red-400"
                        }`}
                      />
                      <span className="font-semibold">{station.freshness}</span>
                    </div>
                    <div className="text-[10px] text-slate-400">{station.data_age}</div>
                  </td>

                  {/* Observation Time */}
                  <td className="px-4 py-3 text-[11px] text-slate-600">
                    {station.last_updated}
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3 text-center">
                    <button
                      type="button"
                      onClick={() => onSelectStation(station.station_id)}
                      className="rounded-lg bg-blue-50 px-2.5 py-1.5 font-semibold text-blue-700 hover:bg-blue-100 transition"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Station Detail Modal */}
      <StationDetailModal stationDetail={selectedStationDetail} onClose={onCloseDetail} />
    </div>
  );
}
