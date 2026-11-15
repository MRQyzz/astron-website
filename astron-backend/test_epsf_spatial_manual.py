
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    table = hdul["EPSF"].data

    peak_map = np.full((21, 21), np.nan)
    negative_map = np.full((21, 21), np.nan)

    for row in table:
        x = int(row["BINX"])
        y = int(row["BINY"])

        epsf = np.asarray(
            row["EPSF"],
            dtype=np.float64
        )

        peak_map[y, x] = np.nanmax(epsf)
        negative_map[y, x] = np.sum(epsf < 0)

# Visualisasi amplitudo puncak
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

im1 = axes[0].imshow(
    peak_map,
    origin="lower",
    interpolation="nearest"
)
axes[0].set_title("EPSF Peak Amplitude")
axes[0].set_xlabel("BINX")
axes[0].set_ylabel("BINY")
fig.colorbar(im1, ax=axes[0], label="Peak value")

# Visualisasi jumlah nilai negatif
im2 = axes[1].imshow(
    negative_map,
    origin="lower",
    interpolation="nearest"
)
axes[1].set_title("Negative Values per EPSF")
axes[1].set_xlabel("BINX")
axes[1].set_ylabel("BINY")
fig.colorbar(im2, ax=axes[1], label="Negative pixel count")

plt.tight_layout()
# plt.show()

print("=== PEAK MAP STATISTICS ===")
print(f"Minimum : {np.nanmin(peak_map):.8f}")
print(f"Maximum : {np.nanmax(peak_map):.8f}")
print(f"Mean    : {np.nanmean(peak_map):.8f}")
print(f"Std     : {np.nanstd(peak_map):.8f}")

print("\n=== NEGATIVE MAP STATISTICS ===")
print(f"Minimum : {np.nanmin(negative_map):.0f}")
print(f"Maximum : {np.nanmax(negative_map):.0f}")
print(f"Mean    : {np.nanmean(negative_map):.4f}")
print(f"Total   : {np.nansum(negative_map):.0f}")

print("\n=== PEAK MAP BY ROW ===")
for y in range(21):
    print(
        f"BINY {y:2d}: "
        + " ".join(f"{v:.5f}" for v in peak_map[y])
    )

print("\n=== NEGATIVE MAP BY ROW ===")
for y in range(21):
    print(
        f"BINY {y:2d}: "
        + " ".join(f"{int(v):3d}" for v in negative_map[y])
    )


print("=== NEGATIVE MAP VERIFICATION ===")

print(
    "Global maximum:",
    int(np.nanmax(negative_map))
)

print(
    "Global minimum:",
    int(np.nanmin(negative_map))
)

print("\n=== HIGHEST NEGATIVE COUNTS ===")

flat_indices = np.argsort(
    negative_map.ravel()
)[-10:][::-1]

for index in flat_indices:
    y, x = np.unravel_index(
        index,
        negative_map.shape
    )

    print(
        f"BINX={x:2d}, BINY={y:2d}, "
        f"negative_count={int(negative_map[y, x])}"
    )

print("\n=== NEGATIVE COUNT BY ROW ===")

for y in range(21):
    values = [
        int(v) for v in negative_map[y]
    ]

    print(
        f"BINY {y:2d}: "
        + ", ".join(map(str, values))
    )

