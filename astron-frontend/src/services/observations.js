
import { apiRequest } from "./api";

export function searchObservations({ ra, dec, radius }) {
  return apiRequest("/observations/search", {
    method: "POST",
    body: JSON.stringify({
      ra: Number(ra),
      dec: Number(dec),
      radius: Number(radius),
    }),
  });
}
