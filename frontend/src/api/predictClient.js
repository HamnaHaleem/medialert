const API_BASE = "http://127.0.0.1:8000";
const TOKEN_KEY = "medialert_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function isLoggedIn() {
  return Boolean(getToken());
}

// Response Handling

class SessionExpiredError extends Error {
  constructor(message) {
    super(message);
    this.name = "SessionExpiredError";
  }
}

async function handleResponse(response) {
  if (response.status === 401) {
    clearToken();
    const body = await response.json().catch(() => ({ detail: "Session expired." }));
    throw new SessionExpiredError(body.detail || "Session expired. Please log in again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    const message = typeof body.detail === "string"
      ? body.detail
      : JSON.stringify(body.detail);
    throw new Error(message);
  }
  return response.json();
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Authentication

export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(response);
}

export async function loginUser(email, password) {
  
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await handleResponse(response);
  setToken(data.access_token);
  return data;
}

export function logoutUser() {
  clearToken();
}

// Application endpoints

export async function fetchFormOptions() {
  const response = await fetch(`${API_BASE}/form-options`);
  return handleResponse(response);
}

export async function submitAssessment(payload) {
  const response = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function fetchHistory(patientReference) {
  const response = await fetch(`${API_BASE}/history/${encodeURIComponent(patientReference)}`, {
    headers: authHeaders(),
  });
  return handleResponse(response);
}

export async function downloadPdf(assessmentId) {

  const response = await fetch(`${API_BASE}/assessments/${assessmentId}/pdf`, {
    headers: authHeaders(),
  });
  if (response.status === 401) {
    clearToken();
    throw new SessionExpiredError("Session expired. Please log in again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail || "Could not download PDF.");
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `medialert-assessment-${assessmentId}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export async function fetchProfile() {
  const response = await fetch(`${API_BASE}/me`, {
    headers: authHeaders(),
  });
  return handleResponse(response);
}

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`, {
    headers: authHeaders(),
  });
  return handleResponse(response);
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse(response);
}

export { SessionExpiredError };