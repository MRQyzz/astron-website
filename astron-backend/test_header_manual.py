from pathlib import Path
from astropy.io import fits
import pandas as pd

fits_file = next(Path("temp").glob("2025W37_1A_0290_1*.fits"))

with fits.open(fits_file, memmap=True) as hdul:
    rows = []

    for hdu_name in ["PRIMARY", "IMAGE"]:
        header = hdul[hdu_name].header

        for key in header:
            if key in ["COMMENT", "HISTORY"]:
                continue

            rows.append({
                "HDU": hdu_name,
                "Keyword": key,
                "Value": str(header[key]),
                "Comment": header.comments[key],
            })

# print(pd.DataFrame(rows))

important_keywords = [
    "BUNIT", "OBJECT", "DATE-OBS", "TELESCOP",
    "INSTRUME", "FILTER", "BAND", "WAVELEN",
    "CRVAL1", "CRVAL2", "CTYPE1", "CTYPE2",
    "NAXIS", "NAXIS1", "NAXIS2", "CRPIX1",
    "CRPIX2", "CRVAL1",  "CRVAL2", "CDELT1",
    "CDELT2", "CD1_1", "CD1_2", "CD2_1",
    "CD2_2", "PC1_1", "PC1_2", "PC2_1",
    "PC2_2", "FINAST", "ASTRONETSOLVED",
    "MATCH_NSTARS", "CRVAL1", "CRVAL2",
    "CRPIX1", "CRPIX2", "CTYPE1", "CTYPE2",
]

filtered_metadata = [
    row for row in rows
    if row["Keyword"] in important_keywords
]

for item in filtered_metadata:
    print(
        f'{item["HDU"]:8} | '
        f'{item["Keyword"]:12} | '
        f'{item["Value"]:20} | '
        f'{item["Comment"]}'
    )