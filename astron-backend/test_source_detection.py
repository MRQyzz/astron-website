
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.stats import sigma_clipped_stats, SigmaClip

from photutils.background import Background2D, MedianBackground

# Locate FITS file
FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

# Load IMAGE extension
with fits.open(FITS_PATH) as hdul:
    image_data = hdul["IMAGE"].data.astype(np.float32).copy()

# Calculate background statistics
mean, median, std = sigma_clipped_stats(
    image_data,
    sigma=3.0,
    maxiters=5
)

print("=== BACKGROUND STATISTICS ===")
print(f"Mean   : {mean}")
print(f"Median : {median}")
print(f"Std    : {std}")

# Visualize background-subtracted image
background_subtracted = image_data - median

plt.figure(figsize=(9, 7))

vmin, vmax = np.nanpercentile(
    background_subtracted,
    [1, 99]
)

plt.imshow(
    background_subtracted,
    origin="lower",
    cmap="gray",
    vmin=vmin,
    vmax=vmax
)

plt.colorbar(label="Background-subtracted value")
plt.title("SPHEREx IMAGE - Background Subtracted")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()

sigma_clip = SigmaClip(sigma=3.0, maxiters=5)

bkg = Background2D(
    image_data,
    box_size=(64, 64),
    filter_size=(3, 3),
    sigma_clip=sigma_clip,
    bkg_estimator=MedianBackground(),
)

# Retrieve background map
background_map = bkg.background

# Subtract local background
background_subtracted = image_data - background_map

print("=== LOCAL BACKGROUND STATISTICS ===")
print(f"Background median : {np.median(background_map)}")
print(f"Background mean   : {np.mean(background_map)}")
print(f"Background std    : {np.std(background_map)}")

# Visualize local background map
plt.figure(figsize=(9, 7))
plt.imshow(background_map, origin="lower", cmap="viridis")
plt.colorbar(label="Background (MJy/sr)")
plt.title("SPHEREx - Local Background Map")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()

# Visualize background-subtracted image
plt.figure(figsize=(9, 7))

vmin, vmax = np.nanpercentile(
    background_subtracted,
    [1, 99]
)

plt.imshow(
    background_subtracted,
    origin="lower",
    cmap="gray",
    vmin=vmin,
    vmax=vmax,
)

plt.colorbar(label="Background-subtracted value")
plt.title("SPHEREx IMAGE - Local Background Subtracted")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()

# 1. Check non-finite pixels
invalid_mask = ~np.isfinite(image_data)

total_pixels = image_data.size
invalid_pixels = np.count_nonzero(invalid_mask)
valid_pixels = total_pixels - invalid_pixels

print("=== INVALID PIXEL ANALYSIS ===")
print(f"Total pixels   : {total_pixels}")
print(f"Invalid pixels : {invalid_pixels}")
print(f"Valid pixels   : {valid_pixels}")
print(f"Invalid ratio  : {invalid_pixels / total_pixels * 100:.4f}%")

# Visualize invalid pixel distribution
plt.figure(figsize=(9, 7))
plt.imshow(invalid_mask, origin="lower", cmap="gray")
plt.colorbar(label="Invalid pixel mask")
plt.title("SPHEREx - Invalid Pixel Distribution")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()


# 2. Visualize local background RMS
plt.figure(figsize=(9, 7))
plt.imshow(
    bkg.background_rms,
    origin="lower",
    cmap="viridis"
)
plt.colorbar(label="Background RMS (MJy/sr)")
plt.title("SPHEREx - Local Background RMS")
plt.xlabel("X Pixel")
plt.ylabel("Y Pixel")
plt.show()