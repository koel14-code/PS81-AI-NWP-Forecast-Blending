/**
 * SkyBlend AI API Client.
 * Direct REST API client communicating with FastAPI backend at http://127.0.0.1:8000 / http://localhost:8000.
 */

let BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');

async function fetchApi(endpoint) {
  let url = `${BASE_URL}${endpoint}`;
  try {
    let res;
    try {
      res = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
    } catch (netErr) {
      // Automatic fallback for Windows IPv6/IPv4: retry localhost:8000 -> 127.0.0.1:8000
      if (url.includes('localhost:8000')) {
        const altUrl = url.replace('localhost:8000', '127.0.0.1:8000');
        console.warn(`[SkyBlend API] ${url} failed. Retrying with ${altUrl}...`);
        try {
          res = await fetch(altUrl, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
          });
          url = altUrl;
          BASE_URL = BASE_URL.replace('localhost:8000', '127.0.0.1:8000');
        } catch {
          throw netErr;
        }
      } else {
        throw netErr;
      }
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const msg = errData.detail || `Server returned status HTTP ${res.status}`;
      console.error(`[SkyBlend API Error] GET ${url} -> Status ${res.status}:`, msg);
      throw new Error(msg);
    }

    const json = await res.json();
    if (json.success === false) {
      const msg = json.error || 'API returned failure status.';
      console.error(`[SkyBlend API Error] GET ${url} -> payload failure:`, msg);
      throw new Error(msg);
    }

    return json.data;
  } catch (err) {
    console.error(`[SkyBlend API Connection Error] Failed request to GET ${url}:`, err.message || err);
    throw new Error(`Unable to connect to SkyBlend backend at ${url}. ${err.message || ''}`);
  }
}

export const api = {
  getHealth: () => fetchApi('/api/health'),
  getOverview: (variable = 'precipitation') =>
    fetchApi(`/api/overview?variable=${encodeURIComponent(variable)}`),
  getForecast: (location = 'kolkata', leadDay = 1, variable = 'precipitation') =>
    fetchApi(`/api/forecast?location=${encodeURIComponent(location)}&lead_day=${leadDay}&variable=${encodeURIComponent(variable)}`),
  getWeights: (location = 'kolkata', leadDay = 1, variable = 'precipitation') =>
    fetchApi(`/api/weights?location=${encodeURIComponent(location)}&lead_day=${leadDay}&variable=${encodeURIComponent(variable)}`),
  getSpatialWeights: (leadDay = 1, variable = 'precipitation') =>
    fetchApi(`/api/spatial-weights?lead_day=${leadDay}&variable=${encodeURIComponent(variable)}`),
  getVerification: (variable = 'precipitation') =>
    fetchApi(`/api/verification?variable=${encodeURIComponent(variable)}`),
  getExtremeSignal: (location = 'kolkata', leadDay = 1, variable = 'precipitation') =>
    fetchApi(`/api/extreme-signal?location=${encodeURIComponent(location)}&lead_day=${leadDay}&variable=${encodeURIComponent(variable)}`),
  getMethodology: (variable = 'precipitation') =>
    fetchApi(`/api/methodology?variable=${encodeURIComponent(variable)}`),
  getBaseUrl: () => BASE_URL,
};
