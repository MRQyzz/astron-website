import os

SIMBAD_TAP_SYNC_URL = os.getenv(
    "SIMBAD_TAP_SYNC_URL",
    "https://simbad.idia.ac.za/simbad/sim-tap/sync",
)

SIMBAD_TIMEOUT = 30.0
