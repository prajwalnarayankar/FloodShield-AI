import React from "react";
import { FaShieldAlt, FaSync, FaWater, FaCloudRain, FaCompass, FaBell, FaInfoCircle, FaHeartbeat } from "react-icons/fa";

export default function Navbar({ activeTab, onTabChange, onRefresh, refreshing, demoMode = false }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <FaShieldAlt /> },
    { id: "rivers", label: "River Monitoring", icon: <FaWater /> },
    { id: "rainfall", label: "Rainfall", icon: <FaCloudRain /> },
    { id: "upstream", label: "Upstream Conditions", icon: <FaCompass /> },
    { id: "alerts", label: "Alerts", icon: <FaBell /> },
    { id: "health", label: "Data Health", icon: <FaHeartbeat /> },
    { id: "about", label: "About", icon: <FaInfoCircle /> },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur shadow-xs">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
            <FaShieldAlt className="text-xl" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight text-slate-900 sm:text-xl">
                FloodShield<span className="text-blue-600">-AI</span>
              </h1>
              {demoMode && (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold tracking-wide text-amber-800 uppercase">
                  Demo Mode
                </span>
              )}
            </div>
            <p className="text-xs font-medium text-slate-500">
              Yadgir District Flood Risk Monitoring & Decision Support System
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 rounded-xl bg-slate-100 p-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                activeTab === item.id
                  ? "bg-white text-blue-700 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60 transition shadow-2xs"
            title="Refresh hydrological telemetry from CWC/NWIC/IMD"
          >
            <FaSync className={refreshing ? "animate-spin text-blue-600" : "text-slate-500"} />
            <span className="hidden sm:inline">{refreshing ? "Syncing..." : "Sync Data"}</span>
          </button>
        </div>
      </div>

      {/* Mobile navigation bar */}
      <div className="flex md:hidden overflow-x-auto border-t border-slate-100 px-2 py-1 scrollbar-none">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold ${
              activeTab === item.id
                ? "bg-blue-50 text-blue-700"
                : "text-slate-600"
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </header>
  );
}
