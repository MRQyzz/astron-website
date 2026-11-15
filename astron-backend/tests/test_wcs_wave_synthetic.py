
import numpy as np
import pytest

from app.providers.wcs_wave import interpolate_wcs_wave


@pytest.fixture
def synthetic_wcs_wave():
    """
    Create a synthetic WCS-WAVE grid.

    Both spectral quantities follow a bilinear function:
    f(x, y) = a + bx + cy + dxy
    """

    x_grid = np.array([1.0, 3.0])
    y_grid = np.array([1.0, 3.0])

    values = np.zeros((2, 2, 2), dtype=float)

    for iy, y in enumerate(y_grid):
        for ix, x in enumerate(x_grid):

            # Central wavelength in micrometers.
            wavelength = (
                1.0
                + 0.01 * x
                + 0.02 * y
                + 0.001 * x * y
            )

            # Bandwidth in micrometers.
            bandwidth = (
                0.02
                + 0.001 * x
                + 0.002 * y
                + 0.0001 * x * y
            )

            values[iy, ix] = [wavelength, bandwidth]

    return x_grid, y_grid, values


def test_interpolation_at_known_midpoint(synthetic_wcs_wave):
    x_grid, y_grid, values = synthetic_wcs_wave

    result = interpolate_wcs_wave(
        x=2.0,
        y=2.0,
        x_grid=x_grid,
        y_grid=y_grid,
        values=values,
    )

    assert result["central_wavelength_um"] == pytest.approx(1.064)
    assert result["bandwidth_um"] == pytest.approx(0.0264)


def test_interpolation_at_control_point(synthetic_wcs_wave):
    x_grid, y_grid, values = synthetic_wcs_wave

    result = interpolate_wcs_wave(
        x=3.0,
        y=3.0,
        x_grid=x_grid,
        y_grid=y_grid,
        values=values,
    )

    assert result["central_wavelength_um"] == pytest.approx(1.099)
    assert result["bandwidth_um"] == pytest.approx(0.0299)


def test_interpolation_at_boundary(synthetic_wcs_wave):
    x_grid, y_grid, values = synthetic_wcs_wave

    result = interpolate_wcs_wave(
        x=1.0,
        y=1.0,
        x_grid=x_grid,
        y_grid=y_grid,
        values=values,
    )

    assert result["central_wavelength_um"] == pytest.approx(1.031)
    assert result["bandwidth_um"] == pytest.approx(0.0231)


def test_interpolation_rejects_out_of_bounds(synthetic_wcs_wave):
    x_grid, y_grid, values = synthetic_wcs_wave

    with pytest.raises(ValueError):
        interpolate_wcs_wave(
            x=4.0,
            y=2.0,
            x_grid=x_grid,
            y_grid=y_grid,
            values=values,
        )


def test_interpolation_rejects_nan(synthetic_wcs_wave):
    x_grid, y_grid, values = synthetic_wcs_wave

    with pytest.raises(ValueError):
        interpolate_wcs_wave(
            x=float("nan"),
            y=2.0,
            x_grid=x_grid,
            y_grid=y_grid,
            values=values,
        )
