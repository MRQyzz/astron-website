
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

    return {
        "sigma_x": np.sqrt(mxx) if mxx >= 0 else np.nan,
    }


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = np.isfinite(x) & np.isfinite(y)
    x, y = x[valid], y[valid]

    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan

    return np.corrcoef(x, y)[0, 1]


def remove_spatial_trend(values, bin_x, bin_y):
    """
    Menghilangkan tren linear yang dijelaskan oleh
    BINX dan BINY, lalu mengembalikan residual.
    """

    values = np.asarray(values, dtype=float)

    design = np.column_stack([
        np.ones(len(values)),
        bin_x,
        bin_y,
    ])

    coefficients, *_ = np.linalg.lstsq(
        design,
        values,
        rcond=None,
    )

    predicted = design @ coefficients
    residual = values - predicted

    return residual, coefficients


with fits.open(FITS_PATH, memmap=True) as hdul:

    table = hdul["EPSF"].data

    bin_x = []
    bin_y = []
    cwave = []
    sigma_x = []

    for row in table:

        moments = calculate_moments(row["EPSF"])

        if moments is None:
            continue

        bin_x.append(int(row["BINX"]))
        bin_y.append(int(row["BINY"]))
        cwave.append(float(row["CWAVE"]))
        sigma_x.append(moments["sigma_x"])


bin_x = np.asarray(bin_x, dtype=float)
bin_y = np.asarray(bin_y, dtype=float)
cwave = np.asarray(cwave, dtype=float)
sigma_x = np.asarray(sigma_x, dtype=float)


print("=== ORIGINAL CORRELATION ===")
print("CWAVE vs sigma_x:", pearson(cwave, sigma_x))


# Hilangkan tren spasial dari kedua variabel
cwave_residual, cwave_coeff = remove_spatial_trend(
    cwave, bin_x, bin_y
)

sigma_residual, sigma_coeff = remove_spatial_trend(
    sigma_x, bin_x, bin_y
)


print("\n=== SPATIAL TREND COEFFICIENTS ===")
print("CWAVE:", cwave_coeff)
print("sigma_x:", sigma_coeff)


print("\n=== SPATIALLY DETRENDED CORRELATION ===")
print(
    "CWAVE residual vs sigma_x residual:",
    pearson(cwave_residual, sigma_residual),
)


# Korelasi CWAVE dan sigma_x pada setiap baris BINY
print("\n=== WITHIN-ROW CORRELATION ===")

row_correlations = []

for row_index in range(21):

    mask = bin_y == row_index

    r = pearson(
        cwave[mask],
        sigma_x[mask],
    )

    row_correlations.append(r)

    print(
        f"BINY={row_index:2d} | "
        f"r={r: .5f}"
    )


valid_correlations = np.asarray(row_correlations)
valid_correlations = valid_correlations[
    np.isfinite(valid_correlations)
]

print("\n=== WITHIN-ROW SUMMARY ===")
print("Valid rows:", len(valid_correlations))
print("Mean r:", np.mean(valid_correlations))
print("Median r:", np.median(valid_correlations))
print("Min r:", np.min(valid_correlations))
print("Max r:", np.max(valid_correlations))
