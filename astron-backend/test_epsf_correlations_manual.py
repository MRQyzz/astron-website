
from pathlib import Path

import numpy as np
from astropy.io import fits


FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)


def calculate_moments(profile):
    profile = np.asarray(profile, dtype=np.float64)
    y, x = np.indices(profile.shape)

    total = np.sum(profile)

    if not np.isfinite(total) or abs(total) < 1e-12:
        return None

    x_center = np.sum(profile * x) / total
    y_center = np.sum(profile * y) / total

    dx = x - x_center
    dy = y - y_center

    mxx = np.sum(profile * dx**2) / total
    myy = np.sum(profile * dy**2) / total
    mxy = np.sum(profile * dx * dy) / total

    return {
        "x_center": x_center,
        "y_center": y_center,
        "sigma_x": np.sqrt(mxx) if mxx >= 0 else np.nan,
        "sigma_y": np.sqrt(myy) if myy >= 0 else np.nan,
        "mxy": mxy,
    }


def correlation(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = np.isfinite(x) & np.isfinite(y)

    if np.count_nonzero(valid) < 3:
        return np.nan

    x = x[valid]
    y = y[valid]

    if np.std(x) == 0 or np.std(y) == 0:
        return np.nan

    return np.corrcoef(x, y)[0, 1]


with fits.open(FITS_PATH, memmap=True) as hdul:

    table = hdul["EPSF"].data

    records = []

    for row in table:
        moments = calculate_moments(row["EPSF"])

        if moments is None:
            continue

        records.append({
            "bin_x": int(row["BINX"]),
            "bin_y": int(row["BINY"]),
            "cwave": float(row["CWAVE"]),
            "cband": float(row["CBAND"]),
            "nstar": int(row["NSTAR"]),
            **moments,
        })


print("VALID MODELS:", len(records))

fields = [
    "bin_x",
    "bin_y",
    "cwave",
    "cband",
    "nstar",
]

targets = [
    "sigma_x",
    "sigma_y",
    "x_center",
    "y_center",
    "mxy",
]

print("\n=== PEARSON CORRELATIONS ===")

for target in targets:
    print(f"\nTARGET: {target}")

    for field in fields:
        x = [r[field] for r in records]
        y = [r[target] for r in records]

        print(
            f"{field:10s}: "
            f"{correlation(x, y): .5f}"
        )


print("\n=== SPATIAL ROW SUMMARY ===")

for bin_y in range(21):
    group = [
        r for r in records
        if r["bin_y"] == bin_y
    ]

    if not group:
        continue

    print(
        f"BINY={bin_y:2d} | "
        f"CWAVE={np.mean([r['cwave'] for r in group]):.5f} | "
        f"SIGMA_X={np.mean([r['sigma_x'] for r in group]):.5f} | "
        f"SIGMA_Y={np.mean([r['sigma_y'] for r in group]):.5f} | "
        f"X_CENTER={np.mean([r['x_center'] for r in group]):.5f} | "
        f"Y_CENTER={np.mean([r['y_center'] for r in group]):.5f}"
    )


print("\n=== SPATIAL COLUMN SUMMARY ===")

for bin_x in range(21):
    group = [
        r for r in records
        if r["bin_x"] == bin_x
    ]

    if not group:
        continue

    print(
        f"BINX={bin_x:2d} | "
        f"CWAVE={np.mean([r['cwave'] for r in group]):.5f} | "
        f"SIGMA_X={np.mean([r['sigma_x'] for r in group]):.5f} | "
        f"SIGMA_Y={np.mean([r['sigma_y'] for r in group]):.5f} | "
        f"X_CENTER={np.mean([r['x_center'] for r in group]):.5f} | "
        f"Y_CENTER={np.mean([r['y_center'] for r in group]):.5f}"
    )
