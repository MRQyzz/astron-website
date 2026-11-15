
from pathlib import Path

import numpy as np
from astropy.io import fits


FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)


def calculate_moments(profile):
    """
    Menghitung centroid dan second central moments
    dari satu model ePSF.
    """

    profile = np.asarray(profile, dtype=np.float64)

    y, x = np.indices(profile.shape)

    total = np.sum(profile)

    if not np.isfinite(total) or abs(total) < 1e-12:
        return None

    # Centroid berbobot intensitas
    x_center = np.sum(profile * x) / total
    y_center = np.sum(profile * y) / total

    dx = x - x_center
    dy = y - y_center

    # Second central moments
    mxx = np.sum(profile * dx**2) / total
    myy = np.sum(profile * dy**2) / total
    mxy = np.sum(profile * dx * dy) / total

    # Eigenvalues matriks momen
    covariance = np.array([
        [mxx, mxy],
        [mxy, myy],
    ])

    eigenvalues = np.linalg.eigvalsh(covariance)

    sigma_x = np.sqrt(mxx) if mxx >= 0 else np.nan
    sigma_y = np.sqrt(myy) if myy >= 0 else np.nan

    return {
        "x_center": x_center,
        "y_center": y_center,
        "mxx": mxx,
        "myy": myy,
        "mxy": mxy,
        "sigma_x": sigma_x,
        "sigma_y": sigma_y,
        "eigen_min": eigenvalues[0],
        "eigen_max": eigenvalues[1],
    }


def summarize(values):
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]

    if len(values) == 0:
        return None

    return {
        "min": np.min(values),
        "mean": np.mean(values),
        "median": np.median(values),
        "max": np.max(values),
        "std": np.std(values),
    }


def print_summary(label, results):
    print(f"\n=== {label} ===")

    fields = [
        "x_center",
        "y_center",
        "sigma_x",
        "sigma_y",
        "mxx",
        "myy",
        "mxy",
        "eigen_min",
        "eigen_max",
    ]

    for field in fields:
        stats = summarize([item[field] for item in results])

        if stats is None:
            print(f"{field}: no valid data")
            continue

        print(
            f"{field:12s} | "
            f"min={stats['min']:.6f} | "
            f"mean={stats['mean']:.6f} | "
            f"median={stats['median']:.6f} | "
            f"max={stats['max']:.6f} | "
            f"std={stats['std']:.6f}"
        )


with fits.open(FITS_PATH, memmap=True) as hdul:

    epsf_table = hdul["EPSF"].data

    raw_results = []
    clipped_results = []
    negative_counts = []

    for row in epsf_table:

        profile = np.asarray(
            row["EPSF"],
            dtype=np.float64
        )

        bin_x = int(row["BINX"])
        bin_y = int(row["BINY"])

        negative_counts.append(
            np.count_nonzero(profile < 0)
        )

        # Pendekatan 1: profil asli
        raw = calculate_moments(profile)

        if raw is not None:
            raw_results.append(raw)

        # Pendekatan 2: nilai negatif dijadikan nol
        clipped = np.maximum(profile, 0)

        clipped_total = np.sum(clipped)

        if clipped_total > 0:
            clipped = clipped / clipped_total

            result = calculate_moments(clipped)

            if result is not None:
                clipped_results.append(result)

    print("TOTAL MODELS:", len(epsf_table))
    print("RAW RESULTS:", len(raw_results))
    print("CLIPPED RESULTS:", len(clipped_results))

    print_summary("RAW EPSF", raw_results)
    print_summary("CLIPPED EPSF", clipped_results)

    print("\n=== NEGATIVE VALUE DISTRIBUTION ===")
    print("Total negative elements:", sum(negative_counts))
    print("Mean per model:", np.mean(negative_counts))
    print("Maximum per model:", np.max(negative_counts))

    # Bandingkan beberapa model terpilih
    selected_bins = [
        (0, 0),
        (10, 10),
        (20, 20),
        (14, 1),
    ]

    print("\n=== SELECTED BIN COMPARISON ===")

    for target_x, target_y in selected_bins:

        row_index = next(
            (
                i for i, row in enumerate(epsf_table)
                if int(row["BINX"]) == target_x
                and int(row["BINY"]) == target_y
            ),
            None,
        )

        if row_index is None:
            continue

        row = epsf_table[row_index]
        profile = np.asarray(row["EPSF"], dtype=np.float64)

        raw = calculate_moments(profile)

        clipped = np.maximum(profile, 0)
        clipped /= np.sum(clipped)

        clipped_result = calculate_moments(clipped)

        print(
            f"\nBIN ({target_x}, {target_y})"
        )
        print("NSTAR:", row["NSTAR"])
        print("CWAVE:", row["CWAVE"])
        print("CBAND:", row["CBAND"])
        print("Negative elements:", np.count_nonzero(profile < 0))

        print("RAW:")
        print(raw)

        print("CLIPPED:")
        print(clipped_result)
