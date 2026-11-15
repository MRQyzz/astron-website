
from pathlib import Path

import numpy as np
from astropy.io import fits


def load_wcs_wave(file_path: str | Path) -> tuple:
    """Load spatial grid and spectral values from a FITS file."""

    file_path = Path(file_path)

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError("FITS file does not exist.")

    with fits.open(file_path, mode="readonly", memmap=True) as hdul:
        if "WCS-WAVE" not in hdul:
            raise ValueError("FITS file does not contain WCS-WAVE.")

        table = hdul["WCS-WAVE"].data

        if table is None or len(table) == 0:
            raise ValueError("WCS-WAVE table is empty.")

        x_grid = np.asarray(table["X"][0], dtype=float)
        y_grid = np.asarray(table["Y"][0], dtype=float)
        values = np.asarray(table["VALUES"][0], dtype=float)

    if values.shape != (len(y_grid), len(x_grid), 2):
        raise ValueError("Invalid WCS-WAVE values shape.")

    if (
        not np.all(np.isfinite(x_grid))
        or not np.all(np.isfinite(y_grid))
        or not np.all(np.isfinite(values))
    ):
        raise ValueError("WCS-WAVE contains non-finite values.")

    if (
        np.any(np.diff(x_grid) <= 0)
        or np.any(np.diff(y_grid) <= 0)
    ):
        raise ValueError("WCS-WAVE grids must be strictly increasing.")

    return x_grid, y_grid, values


def interpolate_wcs_wave(
    x: float,
    y: float,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    values: np.ndarray,
) -> dict:
    """Estimate wavelength and bandwidth at a FITS pixel coordinate."""

    x = float(x)
    y = float(y)

    if not np.isfinite(x) or not np.isfinite(y):
        raise ValueError("Pixel coordinates must be finite.")

    if not (x_grid[0] <= x <= x_grid[-1]):
        raise ValueError("X coordinate is outside the WCS-WAVE grid.")

    if not (y_grid[0] <= y <= y_grid[-1]):
        raise ValueError("Y coordinate is outside the WCS-WAVE grid.")

    ix = np.searchsorted(x_grid, x, side="right") - 1
    iy = np.searchsorted(y_grid, y, side="right") - 1

    ix = min(max(ix, 0), len(x_grid) - 2)
    iy = min(max(iy, 0), len(y_grid) - 2)

    x1, x2 = x_grid[ix], x_grid[ix + 1]
    y1, y2 = y_grid[iy], y_grid[iy + 1]

    tx = (x - x1) / (x2 - x1)
    ty = (y - y1) / (y2 - y1)

    q11 = values[iy, ix]
    q21 = values[iy, ix + 1]
    q12 = values[iy + 1, ix]
    q22 = values[iy + 1, ix + 1]

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


def get_spectral_info(
    file_path: str | Path,
    x: float,
    y: float,
) -> dict:
    """Load WCS-WAVE and return spectral information for one pixel."""

    x_grid, y_grid, values = load_wcs_wave(file_path)

    spectral_info = interpolate_wcs_wave(
        x=x,
        y=y,
        x_grid=x_grid,
        y_grid=y_grid,
        values=values,
    )

    return {
        "pixel": {"x": float(x), "y": float(y)},
        "spectral_info": spectral_info,
        "source": "WCS-WAVE",
        "method": "bilinear_interpolation",
    }
