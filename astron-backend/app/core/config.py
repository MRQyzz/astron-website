import os
from pathlib import Path

SIMBAD_TAP_SYNC_URL = os.getenv(
    "SIMBAD_TAP_SYNC_URL",
    "https://simbad.idia.ac.za/simbad/sim-tap/sync",
)

SIMBAD_TIMEOUT = 30.0

IRSA_SIA_URL = os.getenv(
    "IRSA_SIA_URL",
    "https://irsa.ipac.caltech.edu/SIA",
)

IRSA_TIMEOUT = 90.0

# FITS download config
BACKEND_DIR = Path(__file__).resolve().parents[2]

FITS_DOWNLOAD_DIR = Path(
    os.getenv(
        "FITS_DOWNLOAD_DIR",
        str(BACKEND_DIR / "temp"),
    )
)

FITS_TIMEOUT = 300.0
FITS_MAX_SIZE = 512 * 1024 * 1024  # 512 MB
FITS_MAX_ATTEMPTS = 3
