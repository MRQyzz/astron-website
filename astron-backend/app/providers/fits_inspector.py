from pathlib import Path
from astropy.io import fits

def inspect_fits_structure(file_path: str | Path) -> dict:
    """
    Inspect the structural metadata of a FITS file.

    Returns information about each HDU without
    loading or exposing the full scientific data.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError("FITS file does not exists")

    if not file_path.is_file():
        raise ValueError("FITS path must be point to a file")

    if file_path.suffix.lower() != ".fits":
        raise ValueError("File must have a .fits extension")

    hdus_metadata = []

    try:
        with fits.open(file_path, mode="readonly", memmap=True) as hdul:
            for index, hdu in enumerate(hdul):
                data = hdu.data

                dimensions = (
                    list(data.shape)
                    if data is not None and hasattr(data, "shape")
                    else None
                )

                metadata = {
                    "index": index,
                    "name": hdu.name,
                    "type": type(hdu).__name__,
                    "dimensions": dimensions,
                }

                if hasattr(data, "nrows"):
                    metadata["row_count"] = data.nrows

                if hasattr(data, "names"):
                    metadata["column_count"] = len(data.names)
                    metadata["columns"] = list(data.names)

                hdus_metadata.append(metadata)

    except Exception as exc:
        raise ValueError(
            "Failed to inspect FITS file"
        ) from exc

    return {
        "filename": file_path.name,
        "size_bytes": file_path.stat().st_size,
        "hdu_count": len(hdus_metadata),
        "hdus": hdus_metadata,
    }