# Use notebooks.ipynb in ./notebooks/notebooks.ipynb for better data exploration experience
from pathlib import Path

import pandas as pd
from astropy.io import fits

# Locate FITS file
fits_path = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

# Pandas display configuration
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 140)
pd.set_option("display.max_colwidth", 50)


def inspect_fits(path):
    with fits.open(path) as hdul:

        # ==========================================
        # 1. HDU OVERVIEW
        # ==========================================

        overview = []

        for index, hdu in enumerate(hdul):
            data = hdu.data

            overview.append({
                "Index": index,
                "HDU Name": hdu.name,
                "Type": type(hdu).__name__,
                "Shape": getattr(data, "shape", None),
                "Data Type": getattr(data, "dtype", None),
                "Header Cards": len(hdu.header),
            })

        overview_df = pd.DataFrame(overview)

        print("\n" + "=" * 90)
        print("FITS HDU OVERVIEW")
        print("=" * 90)

        print(overview_df.to_string(index=False))

        # ==========================================
        # 2. HEADER DETAILS
        # ==========================================

        for index, hdu in enumerate(hdul):

            header_data = []

            for card in hdu.header.cards:
                header_data.append({
                    "Keyword": card.keyword,
                    "Value": str(card.value),
                    "Comment": card.comment,
                })

            header_df = pd.DataFrame(header_data)

            print("\n" + "=" * 90)
            print(f"HDU {index}: {hdu.name} - HEADER DETAILS")
            print("=" * 90)

            print(header_df.to_string(index=False))

            # Save each HDU header as CSV
            output_path = Path("temp") / f"header_{index}_{hdu.name}.csv"
            header_df.to_csv(output_path, index=False)

        # ==========================================
        # 3. BINARY TABLE STRUCTURE
        # ==========================================

        for index, hdu in enumerate(hdul):

            if isinstance(hdu, fits.BinTableHDU):
                print("\n" + "=" * 90)
                print(f"HDU {index}: {hdu.name} - TABLE STRUCTURE")
                print("=" * 90)

                columns = []

                for column in hdu.columns:
                    columns.append({
                        "Name": column.name,
                        "Format": column.format,
                        "Unit": column.unit,
                        "Dimension": column.dim,
                    })

                columns_df = pd.DataFrame(columns)
                print(columns_df.to_string(index=False))


if __name__ == "__main__":
    inspect_fits(fits_path)
