import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

// --- DASHBOARD SUMMARY ---
export async function getDashboardSummary() {
  const response = await api.get("/dashboard/summary");
  return response.data;
}

// --- STATIONS ---
export async function getAllStations(filters = {}) {
  const response = await api.get("/stations", { params: filters });
  return response.data;
}

export async function getStationDetail(stationId) {
  const response = await api.get(`/stations/${stationId}`);
  return response.data;
}

// --- RIVERS ---
export async function getAllRivers() {
  const response = await api.get("/rivers");
  return response.data;
}

export async function getRiverDetail(riverName) {
  const response = await api.get(`/rivers/${encodeURIComponent(riverName)}`);
  return response.data;
}

// --- OBSERVATIONS ---
export async function getLatestObservations() {
  const response = await api.get("/observations/latest");
  return response.data;
}

// --- RAINFALL & IMD WARNINGS ---
export async function getRainfallSummary(params = {}) {
  const response = await api.get("/rainfall", { params });
  return response.data;
}

export async function getWeatherWarnings() {
  const response = await api.get("/rainfall/warnings");
  return response.data;
}

// --- UPSTREAM BASIN CONDITIONS ---
export async function getUpstreamConditions() {
  const response = await api.get("/upstream");
  return response.data;
}

// --- PREDICTIONS ---
export async function getAllPredictions() {
  const response = await api.get("/predictions");
  return response.data;
}

export async function evaluateCustomScenario(scenarioData) {
  const response = await api.post("/predictions/evaluate", scenarioData);
  return response.data;
}

// --- ALERTS ---
export async function getAlerts() {
  const response = await api.get("/alerts");
  return response.data;
}

export async function triggerTestAlert(payload = {}) {
  const response = await api.post("/alerts/test-trigger", payload);
  return response.data;
}

export async function resolveAlert(alertId) {
  const response = await api.post(`/alerts/resolve/${alertId}`);
  return response.data;
}

export async function resetDemoAlerts() {
  const response = await api.post("/alerts/reset-demo");
  return response.data;
}

export async function clearAlerts() {
  const response = await api.post("/alerts/clear");
  return response.data;
}

// --- DATA HEALTH & REFRESH ---
export async function getDataHealth() {
  const response = await api.get("/data-health");
  return response.data;
}

export async function refreshData() {
  const response = await api.post("/data/refresh");
  return response.data;
}

export default api;