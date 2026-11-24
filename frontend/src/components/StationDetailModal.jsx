import React from "react";
import { FaTimes, FaShieldAlt, FaWater, FaExclamationTriangle } from "react-icons/fa";

export default function StationDetailModal({ stationDetail, onClose }) {
  if (!stationDetail) return null;

  const { station, latest_observation, prediction, timeseries } = stationDetail;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl border border-slate-200">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-4">
          <div>
            <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
              CWC Station Hydro-Telemetry
            </span>
            <h3 className="text-xl font-black text-slate-900">
              {station?.station_name}
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              {station?.river} River · {station?.basin} Basin ·{" "}
              {station?.district}, {station?.state}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
          >
            <FaTimes />
          </button>
        </div>

        {/* Risk & Safety Override Banner */}
        <div
          className={`mt-4 rounded-2xl p-4 ${
            prediction?.risk === "EXTREME"
              ? "bg-red-50 border border-red-200 text-red-950"
              : prediction?.risk === "HIGH"
              ? "bg-orange-50 border border-orange-200 text-orange-950"
              : prediction?.risk === "MEDIUM"
              ? "bg-amber-50 border border-amber-200 text-amber-950"
              : "bg-emerald-50 border border-emerald-200 text-emerald-950"
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider opacity-75">
                Flood Risk Assessment
              </span>
              <div className="text-2xl font-black">{prediction?.risk || "LOW"} RISK</div>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold opacity-75">Confidence</span>
              <div className="text-xl font-bold">
                {Math.round((prediction?.confidence ?? 0.8) * 100)}%
              </div>
            </div>
          </div>

          {prediction?.override_applied && (
            <div className="mt-2 rounded-lg bg-red-100/80 p-2 text-xs font-bold text-red-900">
              ⚠ Safety Override Triggered: {prediction?.override_reason}
            </div>
          )}

          <div className="mt-2 border-t border-black/5 pt-2 text-xs">
            <span className="font-bold">Explainable AI Analysis: </span>
            <span>{prediction?.explanation || "Telemetry within stable operating limits."}</span>
          </div>
        </div>

        {/* Hydrological Metrics */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-500 block text-[11px]">Water Level</span>
            <span className="text-lg font-bold text-slate-900">
              {latest_observation?.water_level != null
                ? `${Number(latest_observation.water_level).toFixed(2)} m`
                : "N/A"}
            </span>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-500 block text-[11px]">River Discharge</span>
            <span className="text-lg font-bold text-slate-900">
              {latest_observation?.discharge != null
                ? `${Number(latest_observation.discharge).toFixed(1)} m³/s`
                : "—"}
            </span>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-500 block text-[11px]">Warning Level</span>
            <span className="text-lg font-bold text-slate-900">
              {station?.warning_level != null
                ? `${station.warning_level} m`
                : "Unlisted"}
            </span>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-500 block text-[11px]">Danger Level</span>
            <span className="text-lg font-bold text-slate-900">
              {station?.danger_level != null
                ? `${station.danger_level} m`
                : "Unlisted"}
            </span>
          </div>
        </div>

        {/* Freshness & Metadata */}
        <div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs space-y-1.5">
          <div className="flex justify-between">
            <span className="text-slate-500">Observation Timestamp:</span>
            <span className="font-semibold text-slate-800">
              {latest_observation?.observation_time || "N/A"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Data Freshness:</span>
            <span className="font-semibold text-slate-800">
              {latest_observation?.freshness || "RECENT"} ({latest_observation?.data_age || "Current"})
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Data Source:</span>
            <span className="font-semibold text-slate-800">
              {station?.source || "Central Water Commission"}
            </span>
          </div>
        </div>

        {/* Observations List / Recent Trend */}
        {timeseries?.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Recent Telemetry Readings ({timeseries.length} observations)
            </h4>
            <div className="max-h-40 overflow-y-auto rounded-xl border border-slate-200">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-[10px] uppercase text-slate-600 font-bold">
                  <tr>
                    <th className="px-3 py-2">Timestamp</th>
                    <th className="px-3 py-2">Water Level (m)</th>
                    <th className="px-3 py-2">Discharge (m³/s)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {timeseries.map((t, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="px-3 py-1.5 text-slate-600">{t.time}</td>
                      <td className="px-3 py-1.5 font-bold text-slate-900">{t.water_level ?? "—"}</td>
                      <td className="px-3 py-1.5 text-slate-700">{t.discharge ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="mt-5 border-t border-slate-100 pt-3 text-right">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-slate-200 px-4 py-2 text-xs font-semibold text-slate-800 hover:bg-slate-300 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
