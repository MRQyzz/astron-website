import { apiRequest } from "./api";

export function searchObservations({ ra, dec, radius }) {
  return apiRequest("/observations/search", {
    method: "POST",
    body: JSON.stringify({ ra, dec, radius }),
  });
}

export function uploadFits({ obsId, file }) {
  const body = new FormData();
  body.append("obs_id", obsId);
  body.append("file", file);
  return apiRequest("/observations/upload", {
    method: "POST",
    body,
    headers: {},
  });
}

export function inspectFits(obsId) {
  return apiRequest("/observations/inspect", {
    method: "POST",
    body: JSON.stringify({ obs_id: obsId }),
  });
}

export function getPixelInfo({ obsId, x, y }) {
  return apiRequest("/observations/pixel-info", {
    method: "POST",
    body: JSON.stringify({ obs_id: obsId, x, y }),
  });
}

export function getSpectralInfo({ obsId, x, y }) {
  return apiRequest("/observations/spectral-info", {
    method: "POST",
    body: JSON.stringify({ obs_id: obsId, x, y }),
  });
}

export function downloadObservation({ obsId, accessUrl }) {
  return apiRequest("/observations/download", {
    method: "POST",
    body: JSON.stringify({ obs_id: obsId, access_url: accessUrl }),
  });
}
