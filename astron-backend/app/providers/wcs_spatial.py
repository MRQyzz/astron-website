
from pathlib import Path

from astropy.io import fits
from astropy.wcs import WCS


def get_spatial_info(
    file_path: str | Path,
    x: float,
    y: float,
) -> dict:
    """
    Convert FITS pixel coordinates into celestial coordinates
    using the complete Astropy WCS transformation.
    """

    file_path = Path(file_path)

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError("FITS file does not exist.")

    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Pixel coordinates must be numeric.")

    try:
        with fits.open(
            file_path,
            mode="readonly",
            memmap=True,
        ) as hdul:

            if "IMAGE" not in hdul:
                raise ValueError("FITS file does not contain IMAGE.")

            header = hdul["IMAGE"].header
            image_data = hdul["IMAGE"].data

            if image_data is None or image_data.ndim != 2:
                raise ValueError("IMAGE extension is not a 2D image.")

            height, width = image_data.shape

            if not (1 <= x <= width and 1 <= y <= height):
                raise ValueError("Pixel coordinates are outside the IMAGE.")

            wcs = WCS(header)

            if not wcs.has_celestial:
                raise ValueError("IMAGE does not contain celestial WCS.")

            world = wcs.all_pix2world(
                [[float(x), float(y)]],
                1,
            )[0]

            ra, dec = world[:2]

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Failed to calculate spatial coordinates.") from exc

    return {
        "pixel": {
            "x": float(x),
            "y": float(y),
        },
        "sky_coordinates": {
            "ra_deg": float(ra),
            "dec_deg": float(dec),
        },
        "source": "IMAGE",
        "method": "astropy_wcs_all_pix2world",
    }
