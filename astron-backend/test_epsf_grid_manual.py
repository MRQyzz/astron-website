
from pathlib import Path

import numpy as np
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    table = hdul["EPSF"].data

    records = []

    for row in table:
        epsf = np.asarray(row["EPSF"], dtype=np.float64)
        valid = np.isfinite(epsf)

        values = epsf[valid]

        peak_index = np.unravel_index(
            np.nanargmax(epsf),
            epsf.shape
        )

        records.append({
            "binx": int(row["BINX"]),
            "biny": int(row["BINY"]),
            "nstar": int(row["NSTAR"]),
            "sum": float(values.sum()),
            "peak": float(values.max()),
            "minimum": float(values.min()),
            "negative_count": int(np.sum(values < 0)),
            "peak_x": int(peak_index[1]),
            "peak_y": int(peak_index[0]),
        })

# Konversi menjadi array untuk analisis
sums = np.array([r["sum"] for r in records])
peaks = np.array([r["peak"] for r in records])
nstar = np.array([r["nstar"] for r in records])

print("=== EPSF GRID ANALYSIS ===")
print(f"Total models       : {len(records)}")
print(f"Sum min            : {sums.min()}")
print(f"Sum max            : {sums.max()}")
print(f"Sum mean           : {sums.mean()}")
print(f"Peak min           : {peaks.min()}")
print(f"Peak max           : {peaks.max()}")
print(f"Peak mean          : {peaks.mean()}")
print(f"NSTAR min          : {nstar.min()}")
print(f"NSTAR max          : {nstar.max()}")
print(f"NSTAR mean         : {nstar.mean()}")

print("\n=== PEAK POSITION CHECK ===")
print(
    "Models with centered peak:",
    sum(
        r["peak_x"] == 16 and r["peak_y"] == 16
        for r in records
    )
)

print("\n=== FIRST 10 MODELS ===")

for record in records[:10]:
    print(record)
