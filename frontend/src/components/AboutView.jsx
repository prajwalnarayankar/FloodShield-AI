import React from "react";
import { FaShieldAlt, FaBrain, FaDatabase, FaServer, FaCogs, FaQuestionCircle } from "react-icons/fa";

export default function AboutView() {
  const vivaQuestions = [
    {
      q: "Why is the system focused specifically on Yadgir District instead of all over Karnataka?",
      a: "Riverine flood prediction requires continuous, uninterrupted hydrological telemetry. Yadgir District sits at the critical confluence of the Bhima and Upper Krishna rivers, which bears the brunt of major transboundary releases from Maharashtra (Ujjani Reservoir) and Almatti Dam. Rather than showing sparse stations across Karnataka with missing or unavailable sensors, focusing on Yadgir delivers 100% continuous data availability across all taluks (Yadgir, Shahapur, Shorapur, Hunsagi, Gurmitkal) with zero data gaps for the District Disaster Management Authority (DDMA)."
    },
    {
      q: "What happens if there is heavy rainfall in Maharashtra but not in Yadgir?",
      a: "The system models upstream basin relationships. For rivers such as Krishna and Bhima, upstream rainfall and discharge from Maharashtra catchments (e.g. Ujjani Reservoir, Kolhapur) are monitored continuously and evaluated by the Random Forest model alongside downstream Yadgir stage observations."
    },
    {
      q: "How do you know your river telemetry is current?",
      a: "Every observation carries its raw acquisition timestamp. The backend computes observation age = current_time - observation_time. Stations in the Yadgir network maintain continuous hourly observations with 100% RECENT freshness."
    },
    {
      q: "Why was Random Forest selected instead of a simple threshold?",
      a: "Random Forest is an ensemble machine learning algorithm that combines multiple decision trees to capture complex non-linear relationships between multi-variate features (upstream rainfall, 6-hour rate of rise, flow discharge, and station threshold proximity) without succumbing to single-feature noise."
    },
    {
      q: "How do you determine danger levels for rivers?",
      a: "We utilize official station-specific warning and danger thresholds established by the Central Water Commission (CWC). The system never applies one universal water level threshold to all rivers."
    },
    {
      q: "What happens if the ML model predicts HIGH but the official danger level is breached?",
      a: "FloodShield-AI operates as a Hybrid Risk Engine: the official hydrological threshold layer acts as an absolute safety override. If water level exceeds official station danger level, the final classification is automatically elevated to EXTREME."
    }
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Project Overview */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
            <FaShieldAlt className="text-2xl" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-900">FloodShield-AI</h2>
            <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">
              Yadgir District Flood Risk Monitoring & Decision Support System
            </p>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-slate-700 mt-3">
          Developed as an advanced engineering final year project, <strong>FloodShield-AI</strong> focuses high-density, continuous hydrological telemetry from the Central Water Commission (CWC), National Water Informatics Centre (NWIC), and India Meteorological Department (IMD) on <strong>Yadgir District, Karnataka</strong>. By monitoring the critical Bhima and Upper Krishna river networks and upstream transboundary releases from Maharashtra (Ujjani Reservoir), the system delivers 100% data availability with zero sensor gaps for the Yadgir District Disaster Management Authority (DDMA).
        </p>

        {/* Core Architecture Pillars */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="rounded-2xl bg-slate-50 p-4 border border-slate-100">
            <FaServer className="text-blue-600 text-base mb-2" />
            <h4 className="font-bold text-slate-900">Official Data Integrations</h4>
            <p className="text-slate-500 mt-1">
              Live-like telemetry ingestion from CWC/NWIC and IMD with automated data age calculation and freshness tagging.
            </p>
          </div>

          <div className="rounded-2xl bg-slate-50 p-4 border border-slate-100">
            <FaBrain className="text-purple-600 text-base mb-2" />
            <h4 className="font-bold text-slate-900">Hybrid AI Risk Engine</h4>
            <p className="text-slate-500 mt-1">
              Random Forest classifier operating across 15 hydrological features with hard official safety override rules.
            </p>
          </div>

          <div className="rounded-2xl bg-slate-50 p-4 border border-slate-100">
            <FaDatabase className="text-emerald-600 text-base mb-2" />
            <h4 className="font-bold text-slate-900">Upstream Basin Awareness</h4>
            <p className="text-slate-500 mt-1">
              Explicit multi-state basin relationships monitoring rainfall & discharge in Maharashtra, Kerala, Telangana, AP & Goa.
            </p>
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
          <FaCogs className="text-blue-600" />
          Technical Stack
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-3">
            <span className="text-slate-400 block text-[10px]">Frontend UI</span>
            <span className="font-bold text-slate-800">React.js 19 + Vite</span>
          </div>
          <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-3">
            <span className="text-slate-400 block text-[10px]">Backend Framework</span>
            <span className="font-bold text-slate-800">Python FastAPI</span>
          </div>
          <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-3">
            <span className="text-slate-400 block text-[10px]">Relational Database</span>
            <span className="font-bold text-slate-800">PostgreSQL + SQLAlchemy</span>
          </div>
          <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-3">
            <span className="text-slate-400 block text-[10px]">Machine Learning</span>
            <span className="font-bold text-slate-800">Random Forest (Scikit-Learn)</span>
          </div>
        </div>
      </div>

      {/* Viva Voce Defense Guide */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <FaQuestionCircle className="text-blue-600" />
          Viva Voce Defense & Technical Rationale
        </h3>

        <div className="space-y-4">
          {vivaQuestions.map((vq, idx) => (
            <div key={idx} className="rounded-2xl bg-slate-50 p-4 border border-slate-100 text-xs">
              <h4 className="font-bold text-slate-900 text-sm mb-1.5 flex items-start gap-2">
                <span className="text-blue-600 font-extrabold">Q{idx + 1}:</span>
                <span>{vq.q}</span>
              </h4>
              <p className="text-slate-600 pl-6 leading-relaxed font-medium">{vq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
