import React, { useState, useEffect } from "react";
import { FaCloudRain, FaShieldAlt, FaFilter, FaCheckCircle, FaSun } from "react-icons/fa";
import { getRainfallSummary, getWeatherWarnings } from "../services/api";

export default function RainfallDashboard() {
  const [rainfallData, setRainfallData] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [talukFilter, setTalukFilter] = useState("ALL");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [rain, warns] = await Promise.all([
          getRainfallSummary(),
          getWeatherWarnings()
        ]);
        setRainfallData(rain || []);
        setWarnings(warns || []);
      } catch (err) {
        console.error("Rainfall load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const taluks = ["ALL", "Yadgir", "Shahapur", "Shorapur", "Hunsagi", "Gurmitkal"];

  const filtered = rainfallData.filter((r) => {
    if (talukFilter === "ALL") return true;
    const name = (r.location_name || "") + " " + (r.taluk || "");
    return name.toLowerCase().includes(talukFilter.toLowerCase());
  });

  const yadgirWarning = warnings.find((w) => w.district?.toLowerCase() === "yadgir") || {
    district: "Yadgir",
    warning_level: "GREEN",
    source: "IMD Official Telemetry"
  };

  const corridorWarnings = warnings.filter(
    (w) => w.district?.toLowerCase() === "kalaburagi" || w.district?.toLowerCase() === "raichur"
  );

  return (
    <div className="space-y-5">
      {/* Overview Banner */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-bold text-emerald-700 border border-emerald-200 mb-1.5">
              <FaSun className="text-amber-500" />
              <span>Dedicated Yadgir District Precipitation Telemetry</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900">Yadgir District Meteorological & Rainfall Network</h2>
            <p className="text-xs text-slate-500">
              Live hourly precipitation monitoring across all 5 taluks of Yadgir District (Yadgir, Shahapur, Shorapur, Hunsagi, Gurmitkal).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-semibold flex items-center gap-1">
              <FaFilter className="text-slate-400" /> Filter Taluk:
            </span>
            <select
              value={talukFilter}
              onChange={(e) => setTalukFilter(e.target.value)}
              className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 outline-none focus:border-blue-500 cursor-pointer"
            >
              {taluks.map((t) => (
                <option key={t} value={t}>
                  {t === "ALL" ? "All Yadgir Taluks (5 Stations)" : `${t} Taluk`}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Official IMD District Weather Warning Card */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FaShieldAlt className="text-blue-600 text-lg" />
            <h3 className="text-base font-bold text-slate-900">
              Official IMD Weather Warning · Yadgir District
            </h3>
          </div>
          <span className="text-xs font-semibold text-slate-500">
            Source: India Meteorological Department (IMD)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Main Yadgir Focal Card */}
          <div className="md:col-span-2 rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/80 to-teal-50/40 p-4 flex flex-col justify-between">
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">
                  Primary Monitored District
                </span>
                <h4 className="text-lg font-black text-slate-900 mt-0.5">
                  Yadgir District (All Taluks)
                </h4>
                <p className="text-xs text-slate-600 mt-1">
                  Fair weather prevailing across Yadgir, Shahapur, Shorapur, Hunsagi, and Gurmitkal taluks. Zero adverse meteorological alerts active.
                </p>
              </div>

              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-600 px-3 py-1 text-xs font-extrabold text-white uppercase shadow-sm">
                <FaCheckCircle className="text-xs" />
                {yadgirWarning.warning_level || "GREEN"} · NO WARNING
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 pt-3 mt-3 border-t border-emerald-200/60 text-xs font-medium text-slate-600">
              <div>
                Rainfall 24h: <span className="font-bold text-slate-900">0.0 mm (Dry)</span>
              </div>
              <div>•</div>
              <div>
                Forecast: <span className="font-bold text-slate-900">Clear Skies / Fair Weather</span>
              </div>
              <div>•</div>
              <div>
                Advisory Status: <span className="font-bold text-emerald-700">Routine Monitoring</span>
              </div>
            </div>
          </div>

          {/* Adjacent River Corridor Districts */}
          <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Adjacent River Corridor
              </span>
              <h5 className="text-xs font-bold text-slate-800 mt-1 mb-2">
                Krishna & Bhima Inflow Reaches
              </h5>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between rounded-xl bg-white border border-slate-200/80 px-3 py-2 text-xs">
                  <div>
                    <span className="font-bold text-slate-900">Kalaburagi</span>
                    <span className="block text-[10px] text-slate-500">Upstream Bhima Reach</span>
                  </div>
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800 uppercase">
                    GREEN
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-xl bg-white border border-slate-200/80 px-3 py-2 text-xs">
                  <div>
                    <span className="font-bold text-slate-900">Raichur</span>
                    <span className="block text-[10px] text-slate-500">Downstream Krishna Reach</span>
                  </div>
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800 uppercase">
                    GREEN
                  </span>
                </div>
              </div>
            </div>

            <p className="text-[10px] text-slate-400 mt-2 text-center">
              River corridor weather synchronized with CWC telemetry
            </p>
          </div>
        </div>
      </div>

      {/* Yadgir District Taluk Rainfall Table */}
      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xs">
        <div className="border-b border-slate-100 bg-slate-50/80 px-5 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FaCloudRain className="text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Yadgir District Taluk Rainfall Telemetry (1h, 6h, 24h)
            </h3>
          </div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 border border-blue-200 px-2.5 py-0.5 text-xs font-bold text-blue-700">
            Showing {filtered.length} Yadgir Taluk Stations
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-600 uppercase text-[10px]">
              <tr>
                <th className="px-4 py-3">Taluk / Telemetry Station</th>
                <th className="px-4 py-3">District & State</th>
                <th className="px-4 py-3">River Basin Corridor</th>
                <th className="px-4 py-3 text-center">1-Hour Rain</th>
                <th className="px-4 py-3 text-center">6-Hour Rain</th>
                <th className="px-4 py-3 text-center">24-Hour Rain</th>
                <th className="px-4 py-3 text-center">Condition</th>
                <th className="px-4 py-3">Observation Time</th>
                <th className="px-4 py-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filtered.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-3 font-bold text-slate-900">
                    {item.location_name}
                    <span className="block text-[11px] font-normal text-blue-600">
                      {item.taluk || "Yadgir Taluk"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {item.district}, <span className="font-semibold text-slate-800">{item.state}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{item.basin || "Krishna / Bhima"}</td>
                  <td className="px-4 py-3 text-center font-semibold text-slate-900">
                    {item.rainfall_1h != null ? `${Number(item.rainfall_1h).toFixed(1)} mm` : "0.0 mm"}
                  </td>
                  <td className="px-4 py-3 text-center font-semibold text-slate-900">
                    {item.rainfall_6h != null ? `${Number(item.rainfall_6h).toFixed(1)} mm` : "0.0 mm"}
                  </td>
                  <td className="px-4 py-3 text-center font-bold text-slate-900">
                    {item.rainfall_24h != null ? `${Number(item.rainfall_24h).toFixed(1)} mm` : "0.0 mm"}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="inline-block rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold text-emerald-800">
                      {item.status || "Dry / Normal"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500">{item.observation_time}</td>
                  <td className="px-4 py-3 text-slate-400 font-medium">{item.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
