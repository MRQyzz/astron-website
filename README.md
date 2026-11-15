# ASTRON
### Astronomical Observation Network

ASTRON is a web-based astronomical exploration and data-inspection platform built around SPHEREx observation workflows. It brings together astronomical object discovery, sky visualization, observation search, and local FITS inspection in one interface.

> **Project status:** MVP / active development. SIMBAD catalog search and local FITS analysis are implemented. SPHEREx observation discovery and product retrieval depend on the availability of the external IRSA SIA service.

## What ASTRON does

- Explore the sky through an interactive Aladin Lite view.
- Search astronomical objects by sky coordinates through SIMBAD.
- Resolve object names and identifiers through SIMBAD.
- Search SPHEREx observation metadata through IRSA SIA2.
- Upload a local FITS file for inspection.
- Inspect FITS HDU structure and metadata.
- Convert image pixel coordinates to celestial coordinates using Astropy WCS.
- Estimate spectral information from the SPHEREx `WCS-WAVE` extension using bilinear interpolation.

## Current feature status

| Feature | Implementation | Status |
|---|---|---|
| Interactive sky visualization | Aladin Lite | Implemented |
| Catalog cone search | SIMBAD TAP / ADQL | Implemented |
| Object-name search | SIMBAD TAP / ADQL | Implemented |
| SPHEREx observation search | IRSA SIA2 | Implemented; availability depends on IRSA |
| FITS product download | IRSA product URL | Implemented; availability depends on IRSA |
| Local FITS upload | FastAPI + Astropy validation | Implemented |
| FITS structure inspection | Astropy | Implemented |
| Spatial pixel-to-sky conversion | Astropy WCS | Implemented |
| Spectral lookup | SPHEREx `WCS-WAVE` + bilinear interpolation | Implemented |

ASTRON does not treat an unavailable upstream service as an empty search result. External service errors are returned to the client so that service outages can be distinguished from valid searches with no matching observations.

## Technology stack

### Frontend
- React
- Vite
- Tailwind CSS
- React Router
- Lucide React
- Aladin Lite

### Backend
- Python
- FastAPI
- Pydantic
- HTTPX
- Astropy
- NumPy
- python-multipart
- pytest

## Architecture

ASTRON uses a modular monolith with two independently run applications:

- **Frontend:** React + Vite single-page application.
- **Backend:** FastAPI application exposing HTTP endpoints.

The frontend communicates with the backend through a configurable API base URL. The backend separates API routes, application services, external data providers, request schemas, and core configuration.

See [System Architecture Overview](docs/architecture/system-overview.md).

## Repository structure

```text
ASTRON/
├── astron-frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── assets/
├── astron-backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── providers/
│   │   ├── schemas/
│   │   └── services/
│   ├── notebooks/
│   ├── tests/
│   ├── temp/
│   └── requirements.txt
├── docs/
│   └── architecture/
└── README.md
```

## Getting started

### Requirements

- Python 3.10 or newer
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/MRQyzz/astron-website.git
cd astron-website
```

### 2. Configure and run the backend

Create and activate a virtual environment from the backend directory:

```bash
cd astron-backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file from the example:

```bash
copy .env.example .env
```

On macOS / Linux, use `cp .env.example .env` instead. The example contains the default SIMBAD TAP and IRSA SIA endpoints; adjust them only when needed.

Start the API:

```bash
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000` by default. Interactive API documentation is available at `http://127.0.0.1:8000/docs`, and the health endpoint is `http://127.0.0.1:8000/health`.

### 3. Configure and run the frontend

Open a second terminal from the repository root:

```bash
cd astron-frontend
npm install
```

Create the frontend environment file:

```bash
copy .env.example .env
```

On macOS / Linux, use `cp .env.example .env`.

The default `VITE_API_BASE_URL` is `http://127.0.0.1:8000`. Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite (the project commonly uses port 5174).

## Backend API overview

The API is served from the FastAPI backend. The main route groups are:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API service information |
| GET | `/health` | Backend health check |
| GET | `/catalog/` | Catalog service status |
| POST | `/catalog/search` | SIMBAD coordinate/cone search |
| GET | `/catalog/search-by-name` | SIMBAD object-name search |
| GET | `/observations/` | Observation service status |
| POST | `/observations/search` | IRSA SIA2 observation search |
| POST | `/observations/download` | Download a selected FITS product |
| POST | `/observations/upload` | Upload a local FITS file |
| POST | `/observations/inspect` | Inspect FITS HDUs and metadata |
| POST | `/observations/spectral-info` | Query spectral information at a pixel |
| POST | `/observations/pixel-info` | Query spatial and spectral information at a pixel |

For request schemas and interactive testing, use the generated API documentation at `/docs`.

## Configuration

### Backend environment variables

| Variable | Default | Description |
|---|---|---|
| `SIMBAD_TAP_SYNC_URL` | `https://simbad.idia.ac.za/simbad/sim-tap/sync` | SIMBAD TAP synchronous endpoint |
| `IRSA_SIA_URL` | `https://irsa.ipac.caltech.edu/SIA` | IRSA SIA2 endpoint |
| `CORS_ORIGINS` | Empty | Comma-separated additional allowed frontend origins |
| `FITS_DOWNLOAD_DIR` | `astron-backend/temp` | Local directory for FITS products |

### Frontend environment variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Backend API base URL |

Do not commit real credentials, private tokens, or local `.env` files. Use the supplied `.env.example` files as templates.

## Tests

Backend tests are located in `astron-backend/tests/`. From the backend directory, with the virtual environment activated, run:

```bash
pytest
```

The repository also contains manual scientific exploration and diagnostic scripts. Files with a `_manual` suffix are exploratory checks and are not necessarily part of the automated pytest suite.

## External services and limitations

ASTRON relies on external astronomy services for remote data:

- **SIMBAD:** astronomical object catalog and identifier resolution.
- **IRSA:** SPHEREx observation discovery and product access.
- **Aladin Lite:** interactive sky visualization.

These services are outside ASTRON's control and may be temporarily unavailable or rate-limited. In particular, an upstream IRSA proxy error (HTTP 502) prevents remote coordinate-based observation searches and product retrieval while that service is failing. Local FITS upload, inspection, and analysis do not require a successful IRSA search when a suitable FITS file is already available.

VizieR is described as a possible future catalog fallback in the architecture notes; it is not currently an implemented fallback in the application.

## Data handling

- Uploaded and downloaded FITS products are stored under the backend temporary data directory by default.
- The temporary FITS directory is excluded from version control except for its `.gitkeep` placeholder.
- FITS uploads are size-limited and validated before being stored.
- Keep scientific source attribution and observation identifiers attached to results when presenting them.

## License

No license file is currently included in this repository. Add a license before redistributing the project if you intend to grant explicit reuse permissions.
