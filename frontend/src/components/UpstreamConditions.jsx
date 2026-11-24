import React, { useState, useEffect } from "react";
import { FaCompass, FaArrowUp, FaArrowDown, FaMinus, FaExclamationTriangle, FaShieldAlt, FaWater } from "react-icons/fa";
import { getUpstreamConditions } from "../services/api";

export default function UpstreamConditions() {
  const [basins, setBasins] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUpstream() {
      setLoading(true);
      try {
        const data = await getUpstreamConditions();
        setBasins(data || []);
      } catch (err) {
        console.error("Upstream load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadUpstream();
  }, []);

  return (
    <div className="space-y-5">
      {/* Header Banner */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
            <FaCompass className="text-xl" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">Upstream Inflow Intelligence for Yadgir District</h2>
            <p className="text-xs text-slate-500">
              Transboundary hydrological inflow monitoring into Yadgir District from Maharashtra (Ujjani Reservoir) & Upper Krishna
            </p>
          </div>
        </div>
      </div>

      {/* Basin Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {basins.map((b, idx) => {
          const isHigh = b.risk_contribution === "HIGH" || b.overall_condition.includes("CRITICAL");
          const isMedium = b.risk_contribution === "MEDIUM" || b.overall_condition.includes("ELEVATED");

          return (
            <div
              key={idx}
              className={`rounded-3xl border p-5 shadow-xs transition-all ${
                isHigh
                  ? "bg-red-50/40 border-red-200"
                  : isMedium
                  ? "bg-amber-50/40 border-amber-200"
                  : "bg-white border-slate-200"
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                <div>
                  <div className="text-[11px] font-bold text-blue-600 uppercase tracking-wide">
                    River Basin System
                  </div>
                  <h3 className="text-lg font-black text-slate-900">{b.basin} Basin</h3>
                  <p className="text-xs text-slate-500 font-medium">
                    Rivers: {b.key_rivers?.join(", ")}
                  </p>
                </div>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-black uppercase ${
                    isHigh
                      ? "bg-red-600 text-white"
                      : isMedium
                      ? "bg-amber-500 text-white"
                      : "bg-emerald-600 text-white"
                  }`}
                >
                  {b.risk_contribution} Risk Contribution
                </span>
              </div>

              {/* Upstream Inflow Dynamics */}
              <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <div className="rounded-xl bg-slate-50 p-3 border border-slate-100">
                  <span className="text-[11px] text-slate-500 font-medium block">Upstream States</span>
                  <span className="font-bold text-slate-800 text-sm">
                    {b.upstream_states?.join(", ")}
                  </span>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    Catchments: {b.upstream_catchments?.join(", ")}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-3 border border-slate-100">
                  <span className="text-[11px] text-slate-500 font-medium block">Hydraulic Lag / Travel Time</span>
                  <span className="font-bold text-slate-800 text-sm">
                    {b.travel_time_hours}
                  </span>
                  <p className="text-[10px] text-slate-400 mt-0.5">From upstream discharge crest</p>
                </div>
              </div>

              {/* Status Row */}
              <div className="mt-4 space-y-2 text-xs">
                <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-2xs">
                  <span className="text-slate-600 font-medium">Upstream Rainfall Intensity</span>
                  <span
                    className={`font-bold uppercase ${
                      b.upstream_rainfall_intensity === "HIGH"
                        ? "text-red-600"
                        : b.upstream_rainfall_intensity === "MODERATE"
                        ? "text-amber-600"
                        : "text-emerald-600"
                    }`}
                  >
                    {b.upstream_rainfall_intensity} ({b.max_upstream_rainfall_24h} mm max)
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-2xs">
                  <span className="text-slate-600 font-medium">Upstream River Level Trend</span>
                  <span className="font-bold flex items-center gap-1">
                    {b.upstream_river_trend === "RISING" ? (
                      <span className="text-red-600 flex items-center gap-0.5">
                        <FaArrowUp /> RISING
                      </span>
                    ) : b.upstream_river_trend === "FALLING" ? (
                      <span className="text-emerald-600 flex items-center gap-0.5">
                        <FaArrowDown /> FALLING
                      </span>
                    ) : (
                      <span className="text-slate-600 flex items-center gap-0.5">
                        <FaMinus /> STABLE
                      </span>
                    )}
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-2xs">
                  <span className="text-slate-600 font-medium">Downstream Karnataka Trend</span>
                  <span className="font-bold text-slate-800">
                    {b.downstream_river_trend} ({b.near_danger_stations} near danger)
                  </span>
                </div>
              </div>

              {/* Affected Districts */}
              <div className="mt-4 border-t border-slate-100 pt-3">
                <span className="text-[11px] font-bold text-slate-700 block mb-1">
                  Vulnerable Downstream Karnataka Districts:
                </span>
                <div className="flex flex-wrap gap-1">
                  {b.affected_karnataka_districts?.map((d, i) => (
                    <span
                      key={i}
                      className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700"
                    >
                      {d}
                    </span>
                  ))}
                </div>
              </div>

              {/* Overall Assessment */}
              <div className="mt-4 rounded-xl bg-slate-900 p-3 text-white text-xs flex items-center justify-between">
                <span>Overall Basin Condition:</span>
                <span className="font-bold text-amber-400 uppercase tracking-wide">
                  {b.overall_condition}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
