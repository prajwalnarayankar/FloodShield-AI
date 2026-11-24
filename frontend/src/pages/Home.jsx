import React, { useState, useEffect, useCallback } from "react";
import Navbar from "../components/Navbar";
import KpiCards from "../components/KpiCards";
import FloodMap from "../components/FloodMap";
import RiverMonitoring from "../components/RiverMonitoring";
import RainfallDashboard from "../components/RainfallDashboard";
import UpstreamConditions from "../components/UpstreamConditions";
import AlertsView from "../components/AlertsView";
import DataHealthView from "../components/DataHealthView";
import AboutView from "../components/AboutView";
import StationDetailModal from "../components/StationDetailModal";
import {
  getDashboardSummary,
  getAllStations,
  getStationDetail,
  refreshData
} from "../services/api";
import { FaShieldAlt, FaWater, FaExclamationTriangle, FaCheckCircle, FaInfoCircle, FaSync } from "react-icons/fa";

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [summary, setSummary] = useState(null);
  const [stations, setStations] = useState([]);
  const [selectedStationDetail, setSelectedStationDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [syncStatus, setSyncStatus] = useState("");
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [sumData, stData] = await Promise.all([
        getDashboardSummary(),
        getAllStations()
      ]);
      setSummary(sumData);
      setStations(stData || []);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
      setError("Unable to connect to FloodShield backend API. Ensure FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    setSyncStatus("Fetching live telemetry from CWC & IMD...");
    try {
      const res = await refreshData();
      setSyncStatus(`Sync Complete: ${res.water_levels?.fetched ?? 0} WL, ${res.discharge?.fetched ?? 0} Discharge, ${res.rainfall?.fetched ?? 0} Rainfall.`);
      await loadData();
      setTimeout(() => setSyncStatus(""), 6000);
    } catch (err) {
      setSyncStatus("Sync failed: Check network or CWC telemetry endpoints.");
      setTimeout(() => setSyncStatus(""), 6000);
    } finally {
      setRefreshing(false);
    }
  };

  const handleSelectStation = async (stationId) => {
    try {
      const detail = await getStationDetail(stationId);
      setSelectedStationDetail(detail);
    } catch (err) {
      console.error("Failed to fetch station detail:", err);
    }
  };

  const handleFilterRisk = (risk) => {
    setActiveTab("rivers");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
      <div>
        {/* Navigation Bar */}
        <Navbar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onRefresh={handleRefresh}
          refreshing={refreshing}
        />

        {/* Global Sync Banner / Feedback */}
        {syncStatus && (
          <div className="bg-blue-600 px-4 py-2 text-center text-xs font-semibold text-white shadow-inner flex items-center justify-center gap-2">
            <FaSync className={refreshing ? "animate-spin" : ""} />
            <span>{syncStatus}</span>
          </div>
        )}

        {error && (
          <div className="mx-auto max-w-7xl px-4 pt-4 sm:px-6">
            <div className="rounded-2xl bg-red-50 border border-red-200 p-4 text-xs font-semibold text-red-800 flex items-center gap-2">
              <FaExclamationTriangle className="text-red-500 text-sm shrink-0" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 space-y-6">
          {/* TAB 1: DASHBOARD */}
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              {/* Header Hero Banner */}
              <div className="rounded-3xl bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 p-6 text-white shadow-lg relative overflow-hidden">
                <div className="relative z-10 max-w-3xl space-y-2">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/20 border border-emerald-400/30 px-3 py-1 text-xs font-semibold backdrop-blur-md text-emerald-200">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span>100% Continuous Telemetry Active · Yadgir District Network</span>
                  </div>
                  <h1 className="text-2xl font-black tracking-tight sm:text-3xl">
                    Yadgir District Flood Risk Decision Support System
                  </h1>
                  <p className="text-xs text-blue-100 sm:text-sm">
                    Continuous hydro-meteorological telemetry across Bhima and Upper Krishna river networks in Yadgir District, capturing transboundary upstream releases from Maharashtra (Ujjani Reservoir) and Almatti Dam with automated DDMA decision support.
                  </p>
                  <div className="flex flex-wrap gap-4 pt-2 text-xs font-semibold text-blue-200">
                    <div>
                      <span className="text-white font-bold">{summary?.total_stations ?? stations.length}</span> CWC Stations
                    </div>
                    <div>•</div>
                    <div>
                      <span className="text-white font-bold">{summary?.recent_stations ?? 0}</span> Fresh Stations
                    </div>
                    <div>•</div>
                    <div>
                      <span className="text-white font-bold">{summary?.active_alerts ?? 0}</span> Active Risk Notices
                    </div>
                    <div>•</div>
                    <div>
                      Last Pipeline Evaluation: <span className="text-white font-bold">{summary?.last_sync || "Recent"}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* KPI Summary Cards */}
              <KpiCards summary={summary} onFilterRisk={handleFilterRisk} />

              {/* Interactive Karnataka Map */}
              <FloodMap
                stations={stations}
                onSelectStation={handleSelectStation}
              />

              {/* Critical Attention Stations / Active Highlights */}
              <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      High-Priority Hydrological Stations
                    </h3>
                    <p className="text-xs text-slate-500">
                      Stations approaching or exceeding warning thresholds or with elevated upstream inflows
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveTab("rivers")}
                    className="text-xs font-bold text-blue-600 hover:text-blue-800"
                  >
                    View All {stations.length} Stations →
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b border-slate-100 bg-slate-50/70 font-bold uppercase text-[10px] text-slate-600">
                      <tr>
                        <th className="px-4 py-2.5">Station</th>
                        <th className="px-4 py-2.5">River / Basin</th>
                        <th className="px-4 py-2.5">Water Level</th>
                        <th className="px-4 py-2.5">Danger Level</th>
                        <th className="px-4 py-2.5">Risk Level</th>
                        <th className="px-4 py-2.5">Freshness</th>
                        <th className="px-4 py-2.5 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {stations.slice(0, 6).map((station) => (
                        <tr key={station.station_id} className="hover:bg-slate-50/80 transition">
                          <td className="px-4 py-2.5 font-bold text-slate-900">
                            {station.station_name}
                            <span className="block text-[11px] font-normal text-slate-500">
                              {station.district}, {station.state}
                            </span>
                          </td>
                          <td className="px-4 py-2.5">
                            <span className="font-semibold">{station.river}</span>
                            <span className="block text-[11px] text-slate-500">{station.basin}</span>
                          </td>
                          <td className="px-4 py-2.5 font-bold">
                            {station.water_level != null ? `${Number(station.water_level).toFixed(2)} m` : "—"}
                          </td>
                          <td className="px-4 py-2.5 text-slate-600">
                            {station.danger_level != null ? `${station.danger_level} m` : "Unlisted"}
                          </td>
                          <td className="px-4 py-2.5">
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
                          </td>
                          <td className="px-4 py-2.5">
                            <span
                              className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                                station.freshness === "RECENT"
                                  ? "bg-emerald-50 text-emerald-700"
                                  : "bg-slate-100 text-slate-600"
                              }`}
                            >
                              {station.freshness}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 text-center">
                            <button
                              type="button"
                              onClick={() => handleSelectStation(station.station_id)}
                              className="rounded-lg bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 transition"
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
            </div>
          )}

          {/* TAB 2: RIVER MONITORING */}
          {activeTab === "rivers" && (
            <RiverMonitoring
              stations={stations}
              onSelectStation={handleSelectStation}
              selectedStationDetail={selectedStationDetail}
              onCloseDetail={() => setSelectedStationDetail(null)}
            />
          )}

          {/* TAB 3: RAINFALL */}
          {activeTab === "rainfall" && <RainfallDashboard />}

          {/* TAB 4: UPSTREAM CONDITIONS */}
          {activeTab === "upstream" && <UpstreamConditions />}

          {/* TAB 5: ALERTS & SCENARIO SIMULATOR */}
          {activeTab === "alerts" && <AlertsView />}

          {/* TAB 6: DATA HEALTH */}
          {activeTab === "health" && <DataHealthView />}

          {/* TAB 7: ABOUT & VIVA DEFENSE */}
          {activeTab === "about" && <AboutView />}
        </main>
      </div>

      {/* Shared Station Detail Modal (works for map clicks on Dashboard too) */}
      {activeTab !== "rivers" && selectedStationDetail && (
        <StationDetailModal
          stationDetail={selectedStationDetail}
          onClose={() => setSelectedStationDetail(null)}
        />
      )}

      {/* Professional System Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12 text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <FaShieldAlt className="text-blue-600 text-base" />
            <span className="font-bold text-slate-800">FloodShield-AI</span>
            <span>— Yadgir District Hydrological Decision Support System</span>
          </div>
          <div className="text-center sm:text-right space-y-0.5">
            <p>
              Data Sources: Central Water Commission (CWC) · National Water Informatics Centre (NWIC) · IMD
            </p>
            <p className="text-[11px] text-slate-400">
              Hybrid Random Forest Safety Engine · Strictly displays verified telemetry without synthetic fabrication
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}