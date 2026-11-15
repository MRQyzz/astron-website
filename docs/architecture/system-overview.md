# ASTRON — System Architecture Overview

## 1. Architecture Pattern

ASTRON uses a modular monolith architecture with two independently run applications:

- **Frontend:** React + Vite.
- **Backend:** Python + FastAPI.

The frontend communicates with the backend through HTTP API requests. The current MVP does not require a database or distributed infrastructure.

## 2. Frontend Architecture

### Main pages
- `LandingPage.jsx`
- `ExplorerPage.jsx`

### Main components
- Layout/navigation components.
- Observation result components.
- Sky map component powered by Aladin Lite.

### Responsibilities
- Accept object-name and sky-coordinate search input.
- Display an interactive sky visualization.
- Present catalog objects and observation results.
- Support FITS upload and analysis workflows.
- Communicate with the backend through API service modules.

## 3. Backend Architecture

The backend separates responsibilities into these layers:

| Layer | Responsibility |
|---|---|
| API routes | HTTP endpoints, request handling, and response/error mapping |
| Services | Coordinate catalog and observation workflows |
| Providers | Communicate with SIMBAD and IRSA; inspect FITS and calculate WCS information |
| Schemas | Validate API request payloads |
| Core | Configuration and reusable HTTP retry behavior |

## 4. Implemented Data Workflows

### Catalog search
1. Receive and validate sky coordinates or an object name.
2. Submit an ADQL query to SIMBAD TAP.
3. Return catalog records to the frontend.
4. Surface upstream errors as API errors rather than silently treating them as empty results.

### SPHEREx observation search
1. Receive sky coordinates and a search radius.
2. Build an IRSA SIA2 request for the configured SPHEREx collection.
3. Retrieve and parse the returned VOTable.
4. Return observation metadata to the frontend.

This workflow depends on IRSA availability. An upstream proxy or service failure can prevent remote observation discovery.

### FITS product workflow
1. A user uploads a local FITS file or downloads a selected product from IRSA.
2. The backend validates and stores the FITS file in its temporary data directory.
3. Astropy inspects HDU structure and metadata.
4. Astropy WCS maps image pixel coordinates to celestial coordinates.
5. The SPHEREx `WCS-WAVE` table is interpolated to estimate spectral information at a selected pixel.

## 5. External Data and Visualization Services

| Purpose | Provider | Current role |
|---|---|---|
| Astronomical catalog search | SIMBAD TAP | Implemented |
| SPHEREx observation discovery | IRSA SIA2 | Implemented; availability-dependent |
| FITS product access | IRSA | Implemented; availability-dependent |
| Interactive sky visualization | Aladin Lite | Frontend visualization |

VizieR is a possible future catalog fallback, not an active fallback implementation in the current code.

## 6. Error Handling

- HTTP timeouts and network errors are handled at the API boundary.
- The shared HTTP client retries selected transient network and upstream server failures.
- HTTP 429 responses are handled separately as rate limiting.
- Upstream HTTP error details are preserved in a limited diagnostic excerpt for IRSA search failures.
- A failed external service is not represented as a successful search with zero results.
- Local FITS inspection and analysis can continue when a valid local FITS file is available, even if IRSA observation search is unavailable.

## 7. Data Integrity and Local Storage

- FITS uploads are checked for file extension, size, and FITS validity before being stored.
- FITS files are stored under the backend temporary data directory by default.
- The temporary data directory is excluded from version control.
- Observation identifiers and provider provenance are returned with relevant service results.

## 8. MVP Scope

The implemented MVP focuses on:

1. Interactive sky visualization.
2. SIMBAD catalog search by coordinates and object name.
3. IRSA SIA2 SPHEREx observation search.
4. FITS upload and product retrieval.
5. FITS structure inspection.
6. Spatial WCS and spectral WCS-WAVE pixel analysis.

Advanced preprocessing, additional catalog providers, and automated fallback strategies remain future work unless implemented in a later revision.
