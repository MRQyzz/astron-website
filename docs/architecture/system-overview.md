
# ASTRON — System Architecture Overview

## 1. Architecture Pattern

ASTRON uses a Modular Monolith architecture.

The application consists of two independent components:

- Frontend: React + Vite
- Backend: Python + FastAPI

The frontend communicates with the backend through HTTP API requests.

No database or distributed infrastructure is required for the MVP.

## 2. Frontend Architecture

### Pages
- LandingPage.jsx
- ExplorerPage.jsx

### Main Components
- Navbar
- SkySearch
- SkyMap
- ObjectList
- ObjectDetail
- ObservationList
- ObservationDetail

### Main Responsibilities
- Accept astronomical search input.
- Display an interactive sky map using Aladin Lite.
- Manage search coordinates and radius.
- Display catalog objects and SPHEREx observations.
- Present selected object and observation details.
- Communicate with the backend through API services.

## 3. Backend Architecture

### API Layer
- Catalog routes
- Observation routes

### Services Layer
- Catalog Service
- Observation Service
- Retrieval Service

### Provider Layer
- SIMBAD
- VizieR
- IRSA

### Processing Layer
- FITS Reader
- Validator
- Quality Handler
- Preprocessing
- WCS Handler

### Core Layer
- Configuration
- Fallback Handler
- Exceptions

## 4. Data Retrieval Workflow

### Catalog Retrieval
1. Receive search coordinates.
2. Validate the request.
3. Query SIMBAD.
4. Use VizieR as a compatible fallback when necessary.
5. Validate and return catalog results.

### SPHEREx Observation Retrieval
1. Receive search coordinates and radius.
2. Query IRSA SIA2.
3. Retrieve observation metadata and footprints.
4. Request available FITS products or cutouts.
5. Temporarily store FITS data.
6. Read FITS information using Astropy.
7. Validate and return observation results.

Catalog and observation retrieval operate independently.

Failure in one branch must not prevent the other branch from completing.

## 5. Data Sources

| Purpose | Provider |
|---|---|
| Astronomical catalogs | SIMBAD |
| Catalog fallback | VizieR |
| SPHEREx observations | IRSA |
| Sky visualization | Aladin Lite / HiPS |

## 6. Error Handling and Fallback

- Handle HTTP timeouts.
- Retry network errors and server errors (5xx).
- Respect Retry-After for HTTP 429.
- Do not retry HTTP 400.
- Handle HTTP 404 contextually.
- Validate returned data and metadata.
- Preserve source provenance.
- Report unavailable services without substituting unrelated data.

## 7. Data Integrity

- Preserve the original source of every result.
- Do not label non-SPHEREx data as SPHEREx.
- Validate coordinates and observation coverage.
- Avoid duplicate records.
- Do not interpret an empty result as a service failure.

## 8. MVP Scope

The MVP focuses on:

1. Interactive sky exploration.
2. Astronomical catalog retrieval.
3. SPHEREx observation discovery.
4. FITS inspection.
5. Integrated visualization.

Advanced scientific preprocessing and transformations will be
determined separately after the initial data retrieval workflow
has been established.
