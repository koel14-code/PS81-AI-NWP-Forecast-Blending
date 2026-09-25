/**
 * SkyBlend AI API Client.
 *
 * In Vite development mode, requests use relative URLs ('/api/*') so they route
 * through the Vite dev-server reverse proxy directly to FastAPI at http://127.0.0.1:8000.
 *
 * This allows teammates on LAN (e.g. http://192.168.1.3:5173) as well as local users
 * (http://localhost:5173) to communicate seamlessly without direct cross-origin calls to port 8000.
 *
 * An explicit override can still be supplied via VITE_API_BASE_URL if needed.
 */

function resolveBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim();

  // Explicit override if configured in environment
  if (configured) {
    return configured.replace(/\/+$/, '');
  }

  // In Vite development mode, use relative URL ('') so browser requests
  // route through Vite's dev-server proxy (http://<host>:5173/api/* -> http://127.0.0.1:8000/api/*).
  if (import.meta.env.DEV) {
    return '';
  }

  // Production fallback:
  // Default to relative URL ('') for same-origin or reverse-proxy deployments (Nginx, Caddy, FastAPI static mount).
  return '';
}

let BASE_URL = resolveBaseUrl();

function getDisplayUrl(endpoint = '') {
  if (BASE_URL) {
    return `${BASE_URL}${endpoint}`;
  }
  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.origin}${endpoint}`;
  }
  return endpoint;
}

async function fetchApi(endpoint) {
  const url = `${BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      const message =
        errorData.detail ||
        `Server returned status HTTP ${res.status}`;

      console.error(
        `[SkyBlend API Error] GET ${getDisplayUrl(endpoint)} -> ${res.status}:`,
        message
      );

      throw new Error(message);
    }

    const json = await res.json();

    if (json.success === false) {
      const message =
        json.error || 'API returned failure status.';

      console.error(
        `[SkyBlend API Error] GET ${getDisplayUrl(endpoint)} -> payload failure:`,
        message
      );

      throw new Error(message);
    }

    return json.data;
  } catch (error) {
    console.error(
      `[SkyBlend API Connection Error] GET ${getDisplayUrl(endpoint)}:`,
      error.message || error
    );

    throw new Error(
      `Unable to connect to SkyBlend backend at ${getDisplayUrl(endpoint)}. ${
        error.message || ''
      }`
    );
  }
}

export const api = {
  getHealth: () =>
    fetchApi('/api/health'),

  getOverview: (variable = 'precipitation') =>
    fetchApi(
      `/api/overview?variable=${encodeURIComponent(variable)}`
    ),

  getForecast: (
    location = 'kolkata',
    leadDay = 1,
    variable = 'precipitation'
  ) =>
    fetchApi(
      `/api/forecast?location=${encodeURIComponent(
        location
      )}&lead_day=${leadDay}&variable=${encodeURIComponent(
        variable
      )}`
    ),

  getWeights: (
    location = 'kolkata',
    leadDay = 1,
    variable = 'precipitation'
  ) =>
    fetchApi(
      `/api/weights?location=${encodeURIComponent(
        location
      )}&lead_day=${leadDay}&variable=${encodeURIComponent(
        variable
      )}`
    ),

  getSpatialWeights: (
    leadDay = 1,
    variable = 'precipitation'
  ) =>
    fetchApi(
      `/api/spatial-weights?lead_day=${leadDay}&variable=${encodeURIComponent(
        variable
      )}`
    ),

  getVerification: (variable = 'precipitation') =>
    fetchApi(
      `/api/verification?variable=${encodeURIComponent(
        variable
      )}`
    ),

  getExtremeSignal: (
    location = 'kolkata',
    leadDay = 1,
    variable = 'precipitation'
  ) =>
    fetchApi(
      `/api/extreme-signal?location=${encodeURIComponent(
        location
      )}&lead_day=${leadDay}&variable=${encodeURIComponent(
        variable
      )}`
    ),

  getMethodology: (variable = 'precipitation') =>
    fetchApi(
      `/api/methodology?variable=${encodeURIComponent(
        variable
      )}`
    ),

  getBaseUrl: () => BASE_URL,
  getDisplayUrl: (endpoint = '') => getDisplayUrl(endpoint),
};