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
      // Automatic fallback for Windows IPv6/IPv4 localhost vs 127.0.0.1 mismatch
      if (url.includes('localhost:8000')) {
        const altUrl = url.replace('localhost:8000', '127.0.0.1:8000');
        console.warn(`[SkyBlend API] ${url} failed. Retrying with ${altUrl}...`);
        res = await fetch(altUrl, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
        });
        url = altUrl;
        BASE_URL = BASE_URL.replace('localhost:8000', '127.0.0.1:8000');
      } else if (url.includes('127.0.0.1:8000')) {
        const altUrl = url.replace('127.0.0.1:8000', 'localhost:8000');
        console.warn(`[SkyBlend API] ${url} failed. Retrying with ${altUrl}...`);
        res = await fetch(altUrl, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
        });
        url = altUrl;
        BASE_URL = BASE_URL.replace('127.0.0.1:8000', 'localhost:8000');
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
  getOverview: () => fetchApi('/api/overview'),
  getForecast: (location = 'kolkata', leadDay = 1) =>
    fetchApi(`/api/forecast?location=${encodeURIComponent(location)}&lead_day=${leadDay}`),
  getWeights: (location = 'kolkata', leadDay = 1) =>
    fetchApi(`/api/weights?location=${encodeURIComponent(location)}&lead_day=${leadDay}`),
  getSpatialWeights: (leadDay = 1) =>
    fetchApi(`/api/spatial-weights?lead_day=${leadDay}`),
  getVerification: () => fetchApi('/api/verification'),
  getExtremeSignal: (location = 'kolkata', leadDay = 1) =>
    fetchApi(`/api/extreme-signal?location=${encodeURIComponent(location)}&lead_day=${leadDay}`),
  getMethodology: () => fetchApi('/api/methodology'),
};
