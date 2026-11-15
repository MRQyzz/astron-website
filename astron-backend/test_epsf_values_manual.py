
from pathlib import Path
import numpy as np
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    epsf_table = hdul["EPSF"].data

    # Ambil model ePSF dari bin pertama
    epsf = np.asarray(epsf_table[0]["EPSF"], dtype=np.float64)

    # Mask untuk nilai yang valid
    valid = np.isfinite(epsf)
    values = epsf[valid]

    print("=== EPSF NUMERICAL ANALYSIS ===")
    print(f"Shape       : {epsf.shape}")
    print(f"Valid       : {valid.sum()}")
    print(f"Invalid     : {(~valid).sum()}")

    print("\n=== STATISTICS ===")
    print(f"Minimum     : {values.min()}")
    print(f"Maximum     : {values.max()}")
    print(f"Mean        : {values.mean()}")
    print(f"Median      : {np.median(values)}")
    print(f"Sum         : {values.sum()}")

    # Posisi nilai maksimum
    max_position = np.unravel_index(
        np.nanargmax(epsf),
        epsf.shape
    )

    print("\n=== PEAK POSITION ===")
    print(f"Position    : {max_position}")
    print(f"Peak value  : {epsf[max_position]}")

    # Parameter bin yang bersangkutan
    row = epsf_table[0]

    print("\n=== BIN METADATA ===")
    print(f"BINX        : {row['BINX']}")
    print(f"BINY        : {row['BINY']}")
    print(f"XCENTER     : {row['XCENTER']}")
    print(f"YCENTER     : {row['YCENTER']}")
    print(f"NSTAR       : {row['NSTAR']}")
    print(f"CWAVE       : {row['CWAVE']}")
    print(f"CBAND       : {row['CBAND']}")
