
from pathlib import Path

import numpy as np
from astropy.io import fits


FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)


def load_wcs_wave(file_path):
    """Load spatial control points and spectral values."""

    with fits.open(file_path, memmap=True) as hdul:
        table = hdul["WCS-WAVE"].data

        x_grid = np.asarray(table["X"][0], dtype=float)
        y_grid = np.asarray(table["Y"][0], dtype=float)
        values = np.asarray(table["VALUES"][0], dtype=float)

    return x_grid, y_grid, values


def bilinear_interpolate(x, y, x_grid, y_grid, values):
    """
    Interpolate wavelength and bandwidth at a FITS pixel coordinate.

    Coordinates use FITS convention: first pixel is (1, 1).
    """

    x = float(x)
    y = float(y)

    if not np.isfinite(x) or not np.isfinite(y):
        raise ValueError("Pixel coordinates must be finite.")

    if not (x_grid[0] <= x <= x_grid[-1]):
        raise ValueError("X coordinate is outside the WCS-WAVE grid.")

    if not (y_grid[0] <= y <= y_grid[-1]):
        raise ValueError("Y coordinate is outside the WCS-WAVE grid.")

    # Find the grid cell containing (x, y).
    ix = np.searchsorted(x_grid, x, side="right") - 1
    iy = np.searchsorted(y_grid, y, side="right") - 1

    # Handle the upper boundary.
    ix = min(max(ix, 0), len(x_grid) - 2)
    iy = min(max(iy, 0), len(y_grid) - 2)

    x1, x2 = x_grid[ix], x_grid[ix + 1]
    y1, y2 = y_grid[iy], y_grid[iy + 1]

    # Relative position inside the grid cell.
    tx = (x - x1) / (x2 - x1)
    ty = (y - y1) / (y2 - y1)

    # Four surrounding values.
    q11 = values[iy, ix]
    q21 = values[iy, ix + 1]
    q12 = values[iy + 1, ix]
    q22 = values[iy + 1, ix + 1]

    # Bilinear interpolation.
    result = (
        q11 * (1 - tx) * (1 - ty)
        + q21 * tx * (1 - ty)
        + q12 * (1 - tx) * ty
        + q22 * tx * ty
    )

    return {
        "central_wavelength_um": float(result[0]),
        "bandwidth_um": float(result[1]),
    }


def main():
    x_grid, y_grid, values = load_wcs_wave(FITS_PATH)

    print("=== WCS-WAVE DATA ===")
    print("X grid:", x_grid)
    print("Y grid:", y_grid)
    print("VALUES shape:", values.shape)

    # Test 1: Exact control point.
    exact = bilinear_interpolate(
        x_grid[4], y_grid[4],
        x_grid, y_grid, values
    )

    expected = values[4, 4]

    print("\n=== TEST 1: CONTROL POINT ===")
    print("Interpolated:", exact)
    print("Original:", expected)
    print("Wavelength error:",
          abs(exact["central_wavelength_um"] - expected[0]))
    print("Bandwidth error:",
          abs(exact["bandwidth_um"] - expected[1]))

    # Test 2: Midpoint between four control points.
    x_mid = (x_grid[4] + x_grid[5]) / 2
    y_mid = (y_grid[4] + y_grid[5]) / 2

    midpoint = bilinear_interpolate(
        x_mid, y_mid,
        x_grid, y_grid, values
    )

    print("\n=== TEST 2: GRID MIDPOINT ===")
    print("Pixel:", (x_mid, y_mid))
    print("Result:", midpoint)

    # Test 3: Several arbitrary pixel coordinates.
    test_points = [
        (1000, 800),
        (500, 500),
        (1500, 1200),
        (2040, 2040),
        (1, 1),
    ]

    print("\n=== TEST 3: ARBITRARY PIXELS ===")

    for x, y in test_points:
        result = bilinear_interpolate(
            x, y, x_grid, y_grid, values
        )

        print(
            f"Pixel ({x}, {y}) | "
            f"Wavelength: {result['central_wavelength_um']:.6f} um | "
            f"Bandwidth: {result['bandwidth_um']:.6f} um"
        )


if __name__ == "__main__":
    main()
