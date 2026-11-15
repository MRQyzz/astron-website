# ASTRON — Demo Runbook

This runbook is for a short, repeatable demonstration of the current MVP. It describes implemented workflows only; it does not imply that remote providers are always available.

## 1. Before the demo

### Environment
- Use a machine with Python 3.10+, Node.js, and npm.
- Ensure the backend dependencies are installed from `astron-backend/requirements.txt`.
- Ensure frontend dependencies are installed with `npm install` in `astron-frontend/`.
- Copy each `.env.example` to a local `.env` and verify `VITE_API_BASE_URL` points to the backend.
- Keep local FITS test data ready. Prefer a known-good SPHEREx FITS product containing the `WCS-WAVE` extension if spectral lookup will be demonstrated.
- Do not place private credentials, personal files, or large FITS products in the repository.

### Start services
Terminal 1, from `astron-backend/` with its virtual environment active:

```powershell
uvicorn app.main:app --reload
```

Terminal 2, from `astron-frontend/`:

```powershell
npm run dev
```

Open the local URL printed by Vite. The backend health endpoint is `http://127.0.0.1:8000/health`; API documentation is at `http://127.0.0.1:8000/docs`.

### Preflight checks
- Confirm the landing page loads.
- Confirm the explorer page and sky visualization load.
- Confirm the backend health endpoint returns a healthy response.
- Run a known-good SIMBAD name search and coordinate search.
- Upload the prepared local FITS file and confirm inspection works.
- If using a live IRSA search, test it before the presentation; do not assume the provider is available.

## 2. Suggested demonstration sequence

### A. Introduce the problem and ASTRON
Explain that ASTRON combines astronomical object discovery, sky visualization, SPHEREx observation discovery, and local FITS inspection in one workflow.

### B. Explore the sky
Show the interactive sky view and explain that the interface accepts object names or sky coordinates, while the backend handles catalog requests.

### C. Demonstrate SIMBAD object discovery
1. Search for a familiar astronomical object by name.
2. Show the returned catalog information.
3. Repeat using sky coordinates to demonstrate the coordinate-based catalog workflow.
4. Explain that SIMBAD is the external catalog provider, not a locally curated ASTRON database.

### D. Demonstrate SPHEREx observation discovery
1. Enter a sky coordinate and search radius.
2. If IRSA responds, show the observation metadata and explain that product retrieval is a separate user-selected step.
3. If IRSA returns an upstream error, state clearly that remote discovery depends on the IRSA SIA service and that the observed HTTP 502 is an upstream proxy/service failure. Do not describe this as a successful empty search.
4. Continue with the local FITS workflow below. This is the planned resilience path for the demo.

### E. Demonstrate local FITS analysis
1. Upload the prepared FITS file.
2. Inspect its HDU structure and metadata.
3. Select a valid image pixel coordinate and demonstrate spatial WCS conversion to sky coordinates.
4. If the file contains a valid `WCS-WAVE` extension, demonstrate spectral lookup at a pixel and explain that the wavelength and bandwidth are obtained through bilinear interpolation of the tabulated grid.
5. Emphasize that local inspection and analysis do not require a successful live IRSA query once the FITS file is available locally.

## 3. Fallback plan

| Situation | Demo response |
|---|---|
| SIMBAD unavailable | Explain the external dependency; use only previously prepared, clearly labelled screenshots or recorded outputs if available. Do not present cached material as a live query. |
| IRSA returns HTTP 502/5xx | Show the error state, explain the upstream dependency, and proceed to local FITS upload and analysis. |
| IRSA returns no matching observations | Explain that this is a valid empty result, distinct from an upstream failure. |
| FITS upload fails | Verify the file is a valid FITS file and within the configured upload limit; switch to a known-good prepared FITS file. |
| Spectral lookup unavailable | Verify that the selected FITS file contains a non-empty `WCS-WAVE` table with the expected `X`, `Y`, and `VALUES` columns. Continue with HDU inspection and spatial WCS if spectral metadata is absent. |
| Frontend cannot reach backend | Check that the API is running and that `VITE_API_BASE_URL` and backend CORS settings match the local frontend origin. |

## 4. Claims to make accurately

- SIMBAD name and coordinate search were verified in the current demo environment.
- IRSA SIA2 integration is implemented, but live availability is external and has previously returned HTTP 502 from its proxy.
- Local FITS upload, HDU inspection, spatial WCS, and WCS-WAVE spectral interpolation are implemented and should be demonstrated with a known-good file.
- VizieR fallback, automated preprocessing, and other future capabilities must not be presented as implemented unless they have since been added and tested.

## 5. After the demo

- Stop local development servers.
- Keep temporary FITS products out of Git.
- Record any reproducible bugs with the request, response status, and sanitized logs; never include secrets or private data.
- Re-run frontend lint/build and backend tests before creating a new release checkpoint.
