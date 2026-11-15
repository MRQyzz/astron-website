
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    variance = hdul["VARIANCE"].data.astype(
        np.float32
    ).copy()
    image = hdul["IMAGE"].data
    flags = hdul["FLAGS"].data
    flag_header = hdul["FLAGS"].header


print("=== VARIANCE STATISTICS ===")

finite_mask = np.isfinite(variance)
valid_variance = variance[finite_mask]

print(f"Shape          : {variance.shape}")
print(f"Data type      : {variance.dtype}")
print(f"Minimum        : {np.min(valid_variance)}")
print(f"Maximum        : {np.max(valid_variance)}")
print(f"Mean           : {np.mean(valid_variance)}")
print(f"Median         : {np.median(valid_variance)}")
print(f"Standard dev   : {np.std(valid_variance)}")
print(f"Invalid pixels : {np.count_nonzero(~finite_mask)}")
print(f"Negative pixels: {np.count_nonzero(valid_variance < 0)}")
print(f"Zero pixels    : {np.count_nonzero(valid_variance == 0)}")

# Visualize variance
plt.figure(figsize=(9, 7))

vmin, vmax = np.nanpercentile(
    variance,
    [1, 99]
)

plt.imshow(
    variance,
    origin="lower",
    cmap="viridis",
    vmin=vmin,
    vmax=vmax
)

plt.colorbar(label="Variance")
plt.title("SPHEREx - Variance Map")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()

# Visualize variance distribution
plt.figure(figsize=(9, 5))

plt.hist(
    valid_variance,
    bins=100,
    histtype="step"
)

plt.xlabel("Variance")
plt.ylabel("Pixel Count")
plt.title("SPHEREx - Variance Distribution")
plt.yscale("log")
plt.show()


# Robust distribution analysis
print("\n=== VARIANCE PERCENTILES ===")

percentiles = [0, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

for p in percentiles:
    value = np.percentile(valid_variance, p)
    print(f"P{p:<6}: {value:.10f}")


# Locate the 20 highest variance pixels
print("\n=== TOP 20 VARIANCE PIXELS ===")

flat_indices = np.argpartition(
    valid_variance, -20
)[-20:]

top_indices = flat_indices[
    np.argsort(valid_variance[flat_indices])[::-1]
]

valid_coordinates = np.argwhere(finite_mask)

for index in top_indices:
    y, x = valid_coordinates[index]

    print(
        f"X={x:4}, Y={y:4} | "
        f"Variance={variance[y, x]:.6f}"
    )


# Inspect variance header
print("\n=== VARIANCE HEADER ===")

with fits.open(FITS_PATH, memmap=True) as hdul:
    variance_header = hdul["VARIANCE"].header

for key in ["BUNIT", "EXTNAME", "BTYPE", "COMMENT"]:
    if key in variance_header:
        print(f"{key}: {variance_header[key]}")


# Histogram without extreme values
upper_limit = np.percentile(valid_variance, 99.9)

plt.figure(figsize=(9, 5))
plt.hist(
    valid_variance[valid_variance <= upper_limit],
    bins=100,
    histtype="step"
)

plt.xlabel("Variance")
plt.ylabel("Pixel Count")
plt.title("SPHEREx - Variance Distribution (Below P99.9)")
plt.yscale("log")
plt.show()

# Define flags from FITS header
flag_definitions = {}

# for key in hdul["FLAGS"].header:
#     if key.startswith("MSKN"):
#         bit = int(key[4:])
#         flag_definitions[bit] = hdul["FLAGS"].header[key]

# # Find the 20 highest variance pixels
# flat_variance = variance.ravel()
# top_indices = np.argpartition(
#     flat_variance, -20
# )[-20:]

# top_indices = top_indices[
#     np.argsort(flat_variance[top_indices])[::-1]
# ]

# print("\n=== VARIANCE / IMAGE / FLAGS CROSS-CHECK ===")

# for index in top_indices:
#     y, x = np.unravel_index(index, variance.shape)

#     flag_value = int(flags[y, x])

#     active_flags = [
#         name
#         for bit, name in flag_definitions.items()
#         if flag_value & (1 << bit)
#     ]

#     print(f"\nPixel: X={x}, Y={y}")
#     print(f"Variance : {variance[y, x]:.6f}")
#     print(f"Image    : {image[y, x]:.6f}")
#     print(f"Flag value: {flag_value}")
#     print(f"Active flags: {active_flags}")

for key in flag_header:
    if key.startswith("MSKN"):
        bit = int(key[4:])
        flag_definitions[bit] = flag_header[key]


# Select pixels with valid IMAGE and VARIANCE values
valid_mask = (
    np.isfinite(variance)
    & np.isfinite(image)
)

valid_variance = variance[valid_mask]
valid_coordinates = np.argwhere(valid_mask)


# Find the 20 highest valid variance pixels
top_positions = np.argpartition(
    valid_variance, -20
)[-20:]

top_positions = top_positions[
    np.argsort(valid_variance[top_positions])[::-1]
]


# Cross-check IMAGE, VARIANCE, and FLAGS
print("\n=== CORRECTED VARIANCE / IMAGE / FLAGS CROSS-CHECK ===")

for position in top_positions:
    y, x = valid_coordinates[position]

    flag_value = int(flags[y, x])

    active_flags = [
        name
        for bit, name in flag_definitions.items()
        if flag_value & (1 << bit)
    ]

    print(f"\nPixel: X={x}, Y={y}")
    print(f"Variance : {variance[y, x]:.6f}")
    print(f"Image    : {image[y, x]:.6f}")
    print(f"Flag value: {flag_value}")
    print(f"Active flags: {active_flags}")


print("\n=== VARIANCE AND FLAG CORRELATION ===")

# Use only finite variance values
finite_mask = np.isfinite(variance)
nonfunc_mask = (flags & (1 << 6)) != 0
bloom_mask = (flags & (1 << 26)) != 0
overflow_mask = (flags & (1 << 1)) != 0

# Compare NONFUNC and usable pixels
nonfunc_valid = finite_mask & nonfunc_mask
func_valid = finite_mask & ~nonfunc_mask

print("\n--- NONFUNC ---")
print(f"Valid pixels: {np.count_nonzero(nonfunc_valid)}")
print(f"Median variance: {np.median(variance[nonfunc_valid]):.8f}")

print("\n--- WITHOUT NONFUNC ---")
print(f"Valid pixels: {np.count_nonzero(func_valid)}")
print(f"Median variance: {np.median(variance[func_valid]):.8f}")

# Define high variance using the previously observed P99.9
threshold = np.nanpercentile(variance, 99.9)
high_variance = finite_mask & (variance > threshold)

print("\n--- HIGH VARIANCE ---")
print(f"Threshold (P99.9): {threshold:.8f}")
print(f"High variance pixels: {np.count_nonzero(high_variance)}")

for name, mask in [
    ("NONFUNC", nonfunc_mask),
    ("BLOOM", bloom_mask),
    ("OVERFLOW", overflow_mask),
]:
    overlap = high_variance & mask
    count = np.count_nonzero(overlap)

    percentage = (
        count / np.count_nonzero(high_variance) * 100
        if np.count_nonzero(high_variance) > 0
        else 0
    )

    print(
        f"{name:10} | "
        f"{count:8} pixels | "
        f"{percentage:.2f}% of high variance pixels"
    )
