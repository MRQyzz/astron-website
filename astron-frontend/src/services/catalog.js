import { apiRequest } from "./api";

export function searchCatalog({ ra, dec, radius }) {
  return apiRequest("/catalog/search", {
    method: "POST",
    body: JSON.stringify({ ra, dec, radius }),
  });
}


export function searchCatalogByName(name) {
  const params = new URLSearchParams({ name });
  return apiRequest(`/catalog/search-by-name?${params.toString()}`);
}
