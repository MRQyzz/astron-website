
from pathlib import Path
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    epsf = hdul["EPSF"].data
    header = hdul["EPSF"].header

    print("=== EPSF STRUCTURE ===")
    print(f"Rows    : {len(epsf)}")
    print(f"Columns : {len(epsf.columns)}")

    print("\n=== EPSF COLUMNS ===")

    for column in epsf.columns:
        print(f"\nName   : {column.name}")
        print(f"Format : {column.format}")
        print(f"Unit   : {column.unit}")
        print(f"Dim    : {column.dim}")

    print("\n=== EPSF HEADER ===")

    for key in header:
        if key.startswith(("TTYPE", "TFORM", "TUNIT", "TDIM")):
            print(f"{key}: {header[key]}")

    print("\n=== FIRST 3 ROWS ===")

    for row in epsf[:3]:
        for column in epsf.columns.names:
            value = row[column]

            if hasattr(value, "__len__") and not isinstance(value, str):
                print(f"{column}: array shape={value.shape}")
            else:
                print(f"{column}: {value}")

        print("-" * 40)
