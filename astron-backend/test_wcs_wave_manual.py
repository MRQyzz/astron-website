
from pathlib import Path

import numpy as np
from astropy.io import fits


FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)


with fits.open(FITS_PATH, memmap=True) as hdul:

    hdu = hdul["WCS-WAVE"]
    table = hdu.data
    header = hdu.header

    print("=== WCS-WAVE STRUCTURE ===")
    print("Rows:", len(table))
    print("Columns:", len(table.columns))

    print("\n=== COLUMN METADATA ===")

    for column in table.columns:
        print("\nName:", column.name)
        print("Format:", column.format)
        print("Unit:", column.unit)
        print("Dimension:", column.dim)

    print("\n=== HEADER ===")

    for key in header:
        if key.startswith(
            ("TTYPE", "TFORM", "TUNIT", "TDIM")
        ):
            print(f"{key}: {header[key]}")

    print("\n=== FIRST ROW VALUES ===")

    row = table[0]

    for column in table.columns.names:

        value = row[column]

        print(f"\n{column}")

        if isinstance(value, np.ndarray):
            print("Shape:", value.shape)
            print("Data type:", value.dtype)
            print("Values:", value)

            if np.issubdtype(value.dtype, np.number):
                print("Min:", np.nanmin(value))
                print("Max:", np.nanmax(value))
        else:
            print("Value:", value)
