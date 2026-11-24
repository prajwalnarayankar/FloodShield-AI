import React, { useState, useEffect } from "react";
import {
  FaBell,
  FaExclamationTriangle,
  FaCheckCircle,
  FaPlay,
  FaSlidersH,
  FaPaperPlane,
  FaEnvelope,
  FaSms,
  FaDesktop,
  FaCheck,
  FaInfoCircle,
  FaMobileAlt,
  FaBroadcastTower,
  FaCheckDouble,
  FaUndo,
  FaTrashAlt
} from "react-icons/fa";
import {
  getAlerts,
  evaluateCustomScenario,
  triggerTestAlert,
  resolveAlert,
  resetDemoAlerts,
  clearAlerts
} from "../services/api";

export default function AlertsView() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [testResult, setTestResult] = useState(null);

  // Recipient Target States for Dual SMS + Email Alerts
  const [recipientPhone, setRecipientPhone] = useState("+917204956308");
  const [recipientEmail, setRecipientEmail] = useState("prajwal1@gmail.com");
  const [showTargetConfig, setShowTargetConfig] = useState(false);
  const [emailTab, setEmailTab] = useState("preview");

  // Viva Interactive Scenario Simulation State
  const [simWaterLevel, setSimWaterLevel] = useState(355.0);
  const [simWarningLevel, setSimWarningLevel] = useState(359.0);
  const [simDangerLevel, setSimDangerLevel] = useState(361.0);
  const [simRainfall24h, setSimRainfall24h] = useState(25.0);
  const [simUpstreamRainfall, setSimUpstreamRainfall] = useState(30.0);
  const [simRateOfRise, setSimRateOfRise] = useState(0.4);
  const [simDischarge, setSimDischarge] = useState(120.0);
  const [simResult, setSimResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await getAlerts();
      setAlerts(data || []);
    } catch (err) {
      console.error("Alerts error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleTriggerTest = async (riskLevel = "EXTREME", stationId = "CWC_KR_YADGIR") => {
    setTriggering(true);
    setTestResult(null);
    try {
      const res = await triggerTestAlert({
        station_id: stationId,
        risk_level: riskLevel,
        recipient_phone: recipientPhone,
        recipient_email: recipientEmail
      });
      setTestResult(res);
      await loadAlerts();
    } catch (err) {
      console.error("Failed to trigger test alert:", err);
    } finally {
      setTriggering(false);
    }
  };

  const [resetting, setResetting] = useState(false);

  const handleResolveAlert = async (alertId) => {
    try {
      await resolveAlert(alertId);
      await loadAlerts();
    } catch (err) {
      console.error("Failed to resolve alert:", err);
    }
  };

  const handleResetDemo = async () => {
    setResetting(true);
    try {
      await resetDemoAlerts();
      await loadAlerts();
    } catch (err) {
      console.error("Failed to reset demo alerts:", err);
    } finally {
      setResetting(false);
    }
  };

  const handleClearAlerts = async () => {
    if (!window.confirm("Clear all alerts from feed?")) return;
    try {
      await clearAlerts();
      await loadAlerts();
    } catch (err) {
      console.error("Failed to clear alerts:", err);
    }
  };

  const handleRunSimulation = async () => {
    setEvaluating(true);
    try {
      const res = await evaluateCustomScenario({
        water_level: Number(simWaterLevel),
        warning_level: Number(simWarningLevel),
        danger_level: Number(simDangerLevel),
        rainfall_24h: Number(simRainfall24h),
        upstream_rainfall: Number(simUpstreamRainfall),
        water_level_change_6h: Number(simRateOfRise),
        discharge: Number(simDischarge)
      });
      setSimResult(res);
    } catch (err) {
      console.error("Simulation error:", err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. HOW ALERTS WORK GUIDE BANNER */}
      <div className="rounded-3xl border border-blue-200 bg-blue-50/70 p-5 shadow-xs">
        <div className="flex items-start gap-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shrink-0 shadow-md">
            <FaInfoCircle className="text-xl" />
          </div>
          <div className="space-y-2">
            <h2 className="text-base font-bold text-slate-900">
              How Alerts Are Triggered, Dispatched, and Checked
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-700 pt-1">
              <div className="rounded-2xl bg-white p-3 border border-blue-100 shadow-2xs">
                <div className="flex items-center gap-2 font-bold text-blue-900 mb-1">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-blue-800 text-[11px]">1</span>
                  Trigger Conditions
                </div>
                <p className="text-slate-600 leading-relaxed text-[11px]">
                  Triggered during 30-minute sync when river level crosses official <strong>CWC Danger Threshold</strong> or when the <strong>Random Forest Engine</strong> predicts HIGH/EXTREME risk based on rainfall and rate of rise.
                </p>
              </div>

              <div className="rounded-2xl bg-white p-3 border border-blue-100 shadow-2xs">
                <div className="flex items-center gap-2 font-bold text-blue-900 mb-1">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-blue-800 text-[11px]">2</span>
                  Multi-Channel Dispatch
                </div>
                <p className="text-slate-600 leading-relaxed text-[11px]">
                  Alerts are committed to PostgreSQL, formatted for <strong>SMS broadcast</strong>, generated as a formal <strong>DDMA email bulletin</strong>, and immediately broadcast to the Web Dashboard.
                </p>
              </div>

              <div className="rounded-2xl bg-white p-3 border border-blue-100 shadow-2xs">
                <div className="flex items-center gap-2 font-bold text-blue-900 mb-1">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-blue-800 text-[11px]">3</span>
                  How to Verify Right Now
                </div>
                <p className="text-slate-600 leading-relaxed text-[11px]">
                  Click the <strong>"Trigger Test Alert"</strong> button below, inspect the live feed, query <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">/api/alerts</code>, or use the What-If Simulator below.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. ACTIVE ALERTS FEED WITH INSTANT TEST TRIGGER */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-4 gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-red-100 text-red-600">
              <FaBell className="text-base" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Hydrological Early Warnings & Alerts</h2>
              <p className="text-xs text-slate-500">Live notifications for Yadgir District River Network & Dispatched Channels</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => handleTriggerTest("EXTREME", "CWC_KR_YADGIR")}
              disabled={triggering}
              className="flex items-center gap-1.5 rounded-xl bg-red-600 px-3.5 py-2 text-xs font-bold text-white shadow-sm hover:bg-red-700 disabled:opacity-50 transition"
              title="Dispatches live test alerts to both Twilio SMS and SMTP Email"
            >
              <FaPaperPlane className={triggering ? "animate-pulse" : ""} />
              <span>{triggering ? "Dispatching..." : "Simulate & Send Test Alert"}</span>
            </button>

            <button
              type="button"
              onClick={() => setShowTargetConfig(!showTargetConfig)}
              className={`flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold transition ${
                showTargetConfig
                  ? "bg-purple-100 border-purple-300 text-purple-900"
                  : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
              }`}
              title="Configure target phone number (SMS) and email address (Email Bulletin)"
            >
              <FaEnvelope className="text-purple-600" />
              <FaSms className="text-blue-600" />
              <span>Alert Targets</span>
            </button>

            <button
              type="button"
              onClick={handleResetDemo}
              disabled={resetting}
              className="flex items-center gap-1.5 rounded-xl bg-blue-50 border border-blue-200 px-3 py-2 text-xs font-bold text-blue-700 hover:bg-blue-100 disabled:opacity-50 transition"
              title="Resets feed to clean official Yadgir District demo alerts"
            >
              <FaUndo className={resetting ? "animate-spin" : ""} />
              <span>{resetting ? "Resetting..." : "Reset Demo Alerts"}</span>
            </button>

            <button
              type="button"
              onClick={handleClearAlerts}
              className="flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-500 hover:bg-slate-100 hover:text-red-600 transition"
              title="Clear all alerts from database"
            >
              <FaTrashAlt className="text-xs" />
              <span className="hidden sm:inline">Clear</span>
            </button>

            <div className="flex items-center gap-1.5 pl-1">
              <span className="rounded-full bg-red-50 border border-red-200 px-2 py-0.5 text-[11px] font-bold text-red-700">
                {alerts.filter(a => a.status === "ACTIVE").length} Active
              </span>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                {alerts.filter(a => a.status === "RESOLVED").length} Resolved
              </span>
              <span className="rounded-full bg-slate-200/80 px-2 py-0.5 text-[11px] font-bold text-slate-700">
                {alerts.length} Total
              </span>
            </div>
          </div>
        </div>

        {/* Dual Alert Recipient Configuration Drawer */}
        {showTargetConfig && (
          <div className="mt-3.5 p-4 rounded-2xl bg-gradient-to-r from-blue-50/70 via-purple-50/50 to-slate-50 border border-slate-200 text-xs shadow-xs">
            <div className="font-bold text-slate-800 mb-2 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <FaSlidersH className="text-blue-600" />
                <span>Multi-Channel Emergency Alert Targets (SMS & Email)</span>
              </span>
              <span className="text-[11px] font-normal text-slate-500">Live alerts will be sent to both destinations upon trigger</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                  <FaSms className="text-blue-600" /> Target Mobile Phone (Twilio Cellular SMS):
                </label>
                <input
                  type="text"
                  value={recipientPhone}
                  onChange={(e) => setRecipientPhone(e.target.value)}
                  placeholder="+917204956308"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-mono font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">Format: +91XXXXXXXXXX (Connected to Twilio Messaging Gateway)</span>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                  <FaEnvelope className="text-purple-600" /> Target Recipient Email (SMTP Emergency Bulletin):
                </label>
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="prajwal1@gmail.com"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-mono font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">Delivers high-priority HTML flood warning bulletin to inbox</span>
              </div>
            </div>
          </div>
        )}

        {/* Test Alert Dispatch Feedback Modal / Card */}
        {testResult && (
          <div className="mt-4 rounded-3xl border border-emerald-300 bg-gradient-to-br from-emerald-50 via-teal-50/40 to-slate-50 p-5 text-xs shadow-sm">
            <div className="flex items-center justify-between font-bold text-emerald-950 pb-3 border-b border-emerald-200/80">
              <span className="flex items-center gap-2 text-sm">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white shadow-xs">
                  <FaCheck className="text-xs" />
                </span>
                <span>Emergency Broadcast Dispatched to Both SMS & Email Channels!</span>
              </span>
              <button
                type="button"
                onClick={() => setTestResult(null)}
                className="rounded-lg px-2 py-1 text-slate-500 hover:bg-emerald-100 hover:text-slate-800 transition"
              >
                ✕ Close
              </button>
            </div>

            {/* Dual Channel Live Status Banner */}
            <div className="my-3 grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* SMS Channel Card */}
              <div className={`rounded-2xl p-3 border ${
                testResult.dispatched_channels?.sms_delivery?.status === "DELIVERED"
                  ? "bg-blue-50/90 border-blue-200 text-blue-950"
                  : "bg-slate-50 border-slate-200 text-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-bold flex items-center gap-1.5 text-xs">
                    <FaSms className="text-blue-600 text-sm" />
                    <span>SMS Channel (Twilio Gateway)</span>
                  </span>
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    testResult.dispatched_channels?.sms_delivery?.status === "DELIVERED"
                      ? "bg-blue-600 text-white"
                      : "bg-amber-100 text-amber-800"
                  }`}>
                    {testResult.dispatched_channels?.sms_delivery?.status === "DELIVERED" ? "DISPATCHED" : (testResult.dispatched_channels?.sms_delivery?.status || "CONFIGURED")}
                  </span>
                </div>
                <div className="mt-1 text-[11px] text-slate-600 flex items-center justify-between">
                  <span>Target: <span className="font-mono font-bold text-slate-800">{testResult.dispatched_channels?.sms_delivery?.phone || recipientPhone}</span></span>
                  {testResult.dispatched_channels?.sms_delivery?.sid && (
                    <span className="text-[10px] font-mono text-slate-500 truncate max-w-[140px]">SID: {testResult.dispatched_channels.sms_delivery.sid}</span>
                  )}
                </div>
              </div>

              {/* Email Channel Card */}
              <div className={`rounded-2xl p-3 border ${
                testResult.dispatched_channels?.email_delivery?.status === "DELIVERED"
                  ? "bg-purple-50/90 border-purple-200 text-purple-950"
                  : testResult.dispatched_channels?.email_delivery?.status === "CONFIG_REQUIRED"
                  ? "bg-amber-50/90 border-amber-200 text-amber-950"
                  : "bg-slate-50 border-slate-200 text-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-bold flex items-center gap-1.5 text-xs">
                    <FaEnvelope className="text-purple-600 text-sm" />
                    <span>Email Channel (SMTP Dispatch)</span>
                  </span>
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    testResult.dispatched_channels?.email_delivery?.status === "DELIVERED"
                      ? "bg-emerald-600 text-white"
                      : testResult.dispatched_channels?.email_delivery?.status === "CONFIG_REQUIRED"
                      ? "bg-amber-500 text-white"
                      : "bg-slate-200 text-slate-700"
                  }`}>
                    {testResult.dispatched_channels?.email_delivery?.status === "DELIVERED"
                      ? "DELIVERED"
                      : testResult.dispatched_channels?.email_delivery?.status === "CONFIG_REQUIRED"
                      ? "CONFIG REQUIRED"
                      : (testResult.dispatched_channels?.email_delivery?.status || "READY")}
                  </span>
                </div>
                <div className="mt-1 text-[11px] text-slate-600 flex items-center justify-between">
                  <span>Recipient: <span className="font-mono font-bold text-slate-800">{testResult.dispatched_channels?.email_delivery?.recipient || recipientEmail}</span></span>
                  {testResult.dispatched_channels?.email_delivery?.status === "CONFIG_REQUIRED" && (
                    <span className="text-[10px] text-amber-700 font-medium">Add SMTP_USER in .env</span>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-3 grid grid-cols-1 lg:grid-cols-12 gap-4">
              {/* Left Column: Live Citizen Smartphone Receiver Simulation (5 cols) */}
              <div className="lg:col-span-5 flex flex-col">
                <div className="text-[11px] font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
                  <FaMobileAlt className="text-blue-600" />
                  <span>Citizen Smartphone Live Receiver (What People See on Phone):</span>
                </div>

                {/* Smartphone Device Mockup Frame */}
                <div className="rounded-2xl border-4 border-slate-800 bg-slate-900 p-2.5 text-slate-100 shadow-lg">
                  {/* Phone Status Bar */}
                  <div className="flex items-center justify-between px-2 pb-2 text-[10px] text-slate-400 border-b border-slate-800">
                    <span className="font-bold text-white">10:42 AM</span>
                    <div className="h-2 w-12 rounded-full bg-slate-700"></div>
                    <span className="flex items-center gap-1">5G 📶 98%</span>
                  </div>

                  {/* Incoming SMS Notification Card */}
                  <div className="mt-2.5 space-y-2">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="flex items-center gap-1 font-semibold text-emerald-400">
                        <FaSms />
                        <span>MESSAGES • VM-KSDMA</span>
                      </span>
                      <span>Just Now</span>
                    </div>

                    {/* Emergency Alert Bubble */}
                    <div className="rounded-xl bg-red-950/90 border border-red-500/70 p-3 shadow-md">
                      <div className="flex items-center gap-1.5 text-red-300 font-bold text-[11px] mb-1">
                        <FaExclamationTriangle className="text-red-400 animate-pulse text-xs" />
                        <span>EMERGENCY FLOOD BROADCAST</span>
                      </div>
                      <p className="font-mono text-[10.5px] leading-relaxed text-red-100 whitespace-pre-wrap">
                        {testResult.dispatched_channels?.sms_payload || "[ALERT: EXTREME] River Krishna at Kudachi reached 538.85m (Danger Level: 538.0m). Immediate precautionary measures recommended for downstream areas."}
                      </p>
                      <div className="mt-2 pt-2 border-t border-red-900/60 flex items-center justify-between text-[9px] text-red-300">
                        <span>Issued: DDMA Yadgir / FloodShield-AI</span>
                        <span className="text-emerald-400 font-bold flex items-center gap-1">
                          <FaCheckDouble className="text-xs" /> Delivered
                        </span>
                      </div>
                    </div>

                    <div className="text-center text-[9px] text-slate-500 pt-1">
                      Priority 1 Government Emergency Alert • Audio override enabled
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Gateway Payload & Official DDMA Email Bulletin (7 cols) */}
              <div className="lg:col-span-7 flex flex-col justify-between gap-3">
                {/* Gateway Payload */}
                <div className="rounded-2xl bg-white p-3.5 border border-emerald-100 shadow-2xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 mb-1.5 text-[11px]">
                    <span className="flex items-center gap-1.5">
                      <FaSms className="text-blue-600" />
                      <span>Telecommunications Gateway SMS Payload:</span>
                    </span>
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[9px] font-bold text-emerald-800">
                      TRAI & NDMA CAP v1.2 Format
                    </span>
                  </div>
                  <pre className="whitespace-pre-wrap font-mono text-[10px] text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                    {testResult.dispatched_channels?.sms_payload}
                  </pre>
                </div>

                {/* Email Channel Bulletin */}
                <div className="rounded-2xl bg-white p-3.5 border border-purple-100 shadow-2xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 mb-2 text-[11px]">
                    <span className="flex items-center gap-1.5">
                      <FaEnvelope className="text-purple-600" />
                      <span>Official DDMA & Citizen Email Alert:</span>
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => setEmailTab("preview")}
                        className={`rounded-lg px-2 py-0.5 text-[10px] font-bold transition ${
                          emailTab === "preview" ? "bg-purple-600 text-white" : "bg-purple-50 text-purple-700 hover:bg-purple-100"
                        }`}
                      >
                        HTML Email
                      </button>
                      <button
                        type="button"
                        onClick={() => setEmailTab("raw")}
                        className={`rounded-lg px-2 py-0.5 text-[10px] font-bold transition ${
                          emailTab === "raw" ? "bg-purple-600 text-white" : "bg-purple-50 text-purple-700 hover:bg-purple-100"
                        }`}
                      >
                        Plain Text
                      </button>
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5 mb-2 text-[10px] space-y-0.5 font-mono">
                    <div><span className="text-slate-400 font-semibold">From:</span> FloodShield-AI Emergency System &lt;alerts@floodshield.gov.in&gt;</div>
                    <div><span className="text-slate-400 font-semibold">To:</span> <span className="text-purple-900 font-bold">{testResult.dispatched_channels?.email_delivery?.recipient || recipientEmail}</span></div>
                    <div><span className="text-slate-400 font-semibold">Subject:</span> <span className="text-slate-800 font-semibold">{testResult.dispatched_channels?.email_payload?.subject}</span></div>
                  </div>

                  {emailTab === "preview" ? (
                    <div className="rounded-xl border border-red-200 bg-red-50/50 p-3 space-y-2 text-slate-800">
                      <div className="flex items-center justify-between border-b border-red-200 pb-2">
                        <span className="font-bold text-red-700 text-xs flex items-center gap-1.5">
                          <FaExclamationTriangle className="text-red-500" />
                          <span>EMERGENCY HYDROLOGICAL BULLETIN</span>
                        </span>
                        <span className="rounded-full bg-red-600 text-white text-[9px] font-black px-2 py-0.5 uppercase">
                          {testResult.alert?.risk_level || "EXTREME"}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-700 leading-relaxed font-medium">
                        {testResult.alert?.message}
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-[10px] bg-white p-2 rounded-lg border border-slate-200">
                        <div><span className="text-slate-500">Station:</span> <strong className="text-slate-900">{testResult.alert?.station_name}</strong></div>
                        <div><span className="text-slate-500">Channel:</span> <strong className="text-purple-700">SMS + EMAIL + WEB</strong></div>
                        <div><span className="text-slate-500">Issued:</span> <strong className="text-slate-900">{new Date().toLocaleTimeString()}</strong></div>
                        <div><span className="text-slate-500">Security:</span> <strong className="text-emerald-700">NDMA / CWC Verified</strong></div>
                      </div>
                    </div>
                  ) : (
                    <pre className="whitespace-pre-wrap font-mono text-[9.5px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-200 max-h-36 overflow-y-auto">
                      {testResult.dispatched_channels?.email_payload?.body}
                    </pre>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Alerts List */}
        {alerts.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">
            <FaCheckCircle className="mx-auto mb-2 text-2xl text-emerald-500" />
            No active high-risk flood alerts currently recorded. Click "Simulate & Send Test Alert" above to verify the pipeline.
          </div>
        ) : (
          <div className="mt-4 divide-y divide-slate-100">
            {alerts.map((a) => (
              <div key={a.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-md px-2 py-0.5 text-[10px] font-black uppercase ${
                        a.risk_level === "EXTREME"
                          ? "bg-red-600 text-white"
                          : a.risk_level === "HIGH"
                          ? "bg-amber-600 text-white"
                          : a.risk_level === "WARNING"
                          ? "bg-orange-500 text-white"
                          : "bg-blue-600 text-white"
                      }`}
                    >
                      {a.risk_level} ALERT
                    </span>
                    <span className="text-sm font-bold text-slate-900">
                      Station: {a.station_name} ({a.river} River)
                    </span>
                    {a.status === "ACTIVE" ? (
                      <span className="flex items-center gap-1 rounded-full bg-red-50 border border-red-200 px-2 py-0.5 text-[10px] font-bold text-red-700">
                        <span className="h-1.5 w-1.5 rounded-full bg-red-600 animate-pulse"></span>
                        ACTIVE
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 rounded-full bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                        <FaCheck className="text-[9px]" />
                        RESOLVED
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-700 font-medium">{a.message}</p>
                  <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                    <span>Basin: <strong className="text-slate-600">{a.basin}</strong></span>
                    <span>District: <strong className="text-slate-600">{a.district}</strong></span>
                    <span>Dispatched: <strong className="text-slate-600">{a.sent_at}</strong></span>
                    <span>Channels: <strong className="text-slate-600">{a.channel}</strong></span>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-center">
                  {a.status === "ACTIVE" && (
                    <button
                      type="button"
                      onClick={() => handleResolveAlert(a.id)}
                      className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-600 hover:bg-slate-50 hover:text-emerald-700 transition"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. VIVA DEMONSTRATION: SCENARIO WHAT-IF SIMULATOR */}
      <div className="rounded-3xl border border-blue-200 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 p-6 shadow-xs">
        <div className="flex items-center justify-between border-b border-blue-100 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white">
              <FaSlidersH />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Interactive Flood Scenario & Safety Override Simulator
              </h2>
              <p className="text-xs text-slate-500">
                Viva Voce interactive demonstration tool: Test real-time model evaluation and CWC danger overrides
              </p>
            </div>
          </div>
        </div>

        {/* Sliders Grid */}
        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs">
          {/* Water Level */}
          <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <div className="flex justify-between font-bold">
              <span className="text-slate-700">Observed Water Level (m)</span>
              <span className="text-blue-600 text-sm font-extrabold">{simWaterLevel} m</span>
            </div>
            <input
              type="range"
              min="345"
              max="365"
              step="0.2"
              value={simWaterLevel}
              onChange={(e) => setSimWaterLevel(Number(e.target.value))}
              className="mt-2 w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>Warning: {simWarningLevel}m</span>
              <span>Danger: {simDangerLevel}m</span>
            </div>
          </div>

          {/* 6h Rate of Rise */}
          <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <div className="flex justify-between font-bold">
              <span className="text-slate-700">6-Hour Rate of Rise</span>
              <span className="text-blue-600 text-sm font-extrabold">{simRateOfRise} m/6h</span>
            </div>
            <input
              type="range"
              min="-1.5"
              max="3.0"
              step="0.1"
              value={simRateOfRise}
              onChange={(e) => setSimRateOfRise(Number(e.target.value))}
              className="mt-2 w-full accent-blue-600 cursor-pointer"
            />
            <span className="text-[10px] text-slate-400 block mt-1">
              Rapid surge rates increase risk probability
            </span>
          </div>

          {/* Discharge */}
          <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <div className="flex justify-between font-bold">
              <span className="text-slate-700">River Discharge (Flow Rate)</span>
              <span className="text-blue-600 text-sm font-extrabold">{simDischarge} m³/s</span>
            </div>
            <input
              type="range"
              min="10"
              max="1500"
              step="10"
              value={simDischarge}
              onChange={(e) => setSimDischarge(Number(e.target.value))}
              className="mt-2 w-full accent-blue-600 cursor-pointer"
            />
            <span className="text-[10px] text-slate-400 block mt-1">
              Hydrological flow volume downstream
            </span>
          </div>

          {/* Local 24h Rainfall */}
          <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <div className="flex justify-between font-bold">
              <span className="text-slate-700">Local 24h Rainfall</span>
              <span className="text-blue-600 text-sm font-extrabold">{simRainfall24h} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="250"
              step="5"
              value={simRainfall24h}
              onChange={(e) => setSimRainfall24h(Number(e.target.value))}
              className="mt-2 w-full accent-blue-600 cursor-pointer"
            />
            <span className="text-[10px] text-slate-400 block mt-1">
              IMD observation in Karnataka district
            </span>
          </div>

          {/* Upstream Catchment Rainfall */}
          <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <div className="flex justify-between font-bold">
              <span className="text-slate-700">Upstream Inflow Rain (Mah/Ker)</span>
              <span className="text-blue-600 text-sm font-extrabold">{simUpstreamRainfall} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="350"
              step="5"
              value={simUpstreamRainfall}
              onChange={(e) => setSimUpstreamRainfall(Number(e.target.value))}
              className="mt-2 w-full accent-blue-600 cursor-pointer"
            />
            <span className="text-[10px] text-slate-400 block mt-1">
              Cross-border rainfall (e.g. Koyna / Wayanad)
            </span>
          </div>

          {/* Run Button */}
          <div className="flex flex-col justify-center rounded-2xl border border-white bg-white/80 p-4 shadow-2xs">
            <button
              type="button"
              onClick={handleRunSimulation}
              disabled={evaluating}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs font-bold text-white shadow-md hover:bg-blue-700 disabled:opacity-50 transition"
            >
              <FaPlay className="text-[10px]" />
              <span>{evaluating ? "Evaluating..." : "Evaluate Flood Scenario"}</span>
            </button>
          </div>
        </div>

        {/* Simulation Output Card */}
        {simResult && (
          <div className="mt-5 rounded-2xl border border-white bg-white p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-3 gap-2">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Model Assessment Result
                </span>
                <div className="flex items-center gap-3">
                  <span
                    className={`rounded-lg px-3 py-1 text-base font-black uppercase ${
                      simResult.risk === "EXTREME"
                        ? "bg-red-600 text-white"
                        : simResult.risk === "HIGH"
                        ? "bg-orange-500 text-white"
                        : simResult.risk === "MEDIUM"
                        ? "bg-amber-500 text-white"
                        : "bg-emerald-600 text-white"
                    }`}
                  >
                    {simResult.risk} RISK
                  </span>
                  <span className="text-xs font-semibold text-slate-600">
                    Model Confidence: {Math.round((simResult.confidence ?? 0.8) * 100)}%
                  </span>
                </div>
              </div>

              {simResult.override_applied && (
                <div className="rounded-xl bg-red-50 border border-red-200 px-3 py-1.5 text-xs font-bold text-red-800">
                  ⚠ Hard Safety Override Triggered!
                </div>
              )}
            </div>

            {simResult.override_applied && (
              <p className="mt-3 rounded-xl bg-red-100/60 p-2.5 text-xs font-semibold text-red-900">
                {simResult.override_reason}
              </p>
            )}

            <div className="mt-3 text-xs text-slate-700">
              <strong className="text-slate-900">Explainable AI Drivers:</strong>
              <ul className="mt-1 list-disc pl-5 space-y-0.5 text-slate-600">
                {simResult.reasons?.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
