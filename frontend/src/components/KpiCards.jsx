import React from "react";
import { FaBroadcastTower, FaCheckCircle, FaExclamationCircle, FaExclamationTriangle, FaBell, FaClock } from "react-icons/fa";

export default function KpiCards({ summary, onFilterRisk }) {
  if (!summary) return null;

  const cards = [
    {
      id: "total",
      label: "Total Stations",
      value: summary.total_stations ?? 0,
      sub: "CWC / NWIC Network",
      icon: <FaBroadcastTower className="text-blue-600" />,
      bg: "bg-blue-50/70 border-blue-100",
      textColor: "text-blue-950",
      filter: null
    },
    {
      id: "recent",
      label: "Active Stations",
      value: summary.recent_stations ?? 0,
      sub: "100% Live Telemetry",
      icon: <FaCheckCircle className="text-emerald-600" />,
      bg: "bg-emerald-50/70 border-emerald-100",
      textColor: "text-emerald-950",
      filter: "recent"
    },
    {
      id: "stale",
      label: "Unavailable",
      value: (summary.stale_stations ?? 0) + (summary.unavailable_stations ?? 0),
      sub: ((summary.stale_stations ?? 0) + (summary.unavailable_stations ?? 0) === 0) ? "Zero Data Gaps" : "Awaiting Sync",
      icon: <FaClock className="text-slate-500" />,
      bg: ((summary.stale_stations ?? 0) + (summary.unavailable_stations ?? 0) === 0) ? "bg-emerald-50/40 border-emerald-200" : "bg-slate-50 border-slate-200",
      textColor: ((summary.stale_stations ?? 0) + (summary.unavailable_stations ?? 0) === 0) ? "text-emerald-900" : "text-slate-800",
      filter: "stale"
    },
    {
      id: "low",
      label: "Low Risk",
      value: summary.low_risk ?? 0,
      sub: "Normal Flow",
      icon: <FaCheckCircle className="text-emerald-500" />,
      bg: "bg-emerald-50/50 border-emerald-100",
      textColor: "text-emerald-900",
      filter: "LOW"
    },
    {
      id: "medium",
      label: "Medium Risk",
      value: summary.medium_risk ?? 0,
      sub: "Watch Level",
      icon: <FaExclamationTriangle className="text-amber-500" />,
      bg: "bg-amber-50/70 border-amber-100",
      textColor: "text-amber-950",
      filter: "MEDIUM"
    },
    {
      id: "high",
      label: "High Risk",
      value: summary.high_risk ?? 0,
      sub: "Near Warning",
      icon: <FaExclamationCircle className="text-orange-500" />,
      bg: "bg-orange-50/70 border-orange-100",
      textColor: "text-orange-950",
      filter: "HIGH"
    },
    {
      id: "extreme",
      label: "Extreme Risk",
      value: summary.extreme_risk ?? 0,
      sub: "Above Danger Level",
      icon: <FaExclamationCircle className="text-red-600 animate-pulse" />,
      bg: "bg-red-50/80 border-red-200",
      textColor: "text-red-950",
      filter: "EXTREME"
    },
    {
      id: "alerts",
      label: "Active Alerts",
      value: summary.active_alerts ?? 0,
      sub: "Hydrological Notices",
      icon: <FaBell className="text-purple-600" />,
      bg: "bg-purple-50/70 border-purple-100",
      textColor: "text-purple-950",
      filter: null
    }
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
      {cards.map((card) => (
        <div
          key={card.id}
          onClick={() => card.filter && onFilterRisk && onFilterRisk(card.filter)}
          className={`group flex flex-col justify-between rounded-2xl border p-3 transition-all hover:shadow-sm ${card.bg} ${
            card.filter ? "cursor-pointer hover:scale-[1.02]" : ""
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-600 truncate">{card.label}</span>
            <span className="text-base">{card.icon}</span>
          </div>
          <div className="mt-2">
            <span className={`text-2xl font-extrabold tracking-tight ${card.textColor}`}>
              {card.value}
            </span>
            <p className="mt-0.5 text-[11px] font-medium text-slate-500 truncate">{card.sub}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
