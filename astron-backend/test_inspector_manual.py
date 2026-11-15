
from pathlib import Path

from app.providers.fits_inspector import inspect_fits_structure


fits_dir = Path("temp")

fits_file = next(
    fits_dir.glob("2025W37_1A_0290_1*.fits")
)

result = inspect_fits_structure(fits_file)

print(f"Filename: {result['filename']}")
print(f"Size: {result['size_bytes']} bytes")
print(f"Total HDUs: {result['hdu_count']}")

for hdu in result["hdus"]:
    print(hdu)
