from pathlib import Path

import numpy as np
from astropy.io import fits

FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)

with fits.open(FITS_PATH, memmap=True) as hdul:
    flags = hdul["FLAGS"].data.copy()
    header = hdul["FLAGS"].header

# print("=== FLAGS HEADER ===")

# for key in header:
#     if key.startswith("BIT") or key.startswith("FLAG"):
#         print(f"{key}: {header[key]}")

# print("\n=== FLAGS STATISTICS ===")

# print(f"Shape       : {flags.shape}")
# print(f"Data type   : {flags.dtype}")
# print(f"Minimum     : {np.min(flags)}")
# print(f"Maximum     : {np.max(flags)}")
# print(f"Unique count: {np.unique(flags).size}")

# values, counts = np.unique(flags, return_counts=True)

# print("\n=== MOST COMMON FLAG VALUES ===")

# order = np.argsort(counts)[::-1]

# for index in order[:20]:
#     print(
#         f"Value: {values[index]:12} | "
#         f"Count: {counts[index]:10} | "
#         f"Percentage: {counts[index] / flags.size * 100:.4f}%"
#     )

print("=== SPHEREx FLAG DEFINITIONS ===")

for key in header:
    if key.startswith("MSKN"):
        bit_number = key[4:]
        name = header[key]
        description = header.get(
            f"MSKD{bit_number}",
            "Description unavailable"
        )

        bit_value = 1 << int(bit_number)

        print(
            f"Bit {bit_number:>2} | "
            f"{name:<12} | "
            f"Value: {bit_value:<12} | "
            f"{description}"
        )

# Convert to int64 for safe bitwise operations
flags_int = flags.astype(np.int64)

print("\n=== INDIVIDUAL FLAG DISTRIBUTION ===")

flag_results = []

for key in header:
    if not key.startswith("MSKN"):
        continue

    bit_number = int(key[4:])
    flag_name = header[key]
    bit_value = 1 << bit_number

    # Check whether this bit is active
    active_mask = (flags_int & bit_value) != 0

    count = np.count_nonzero(active_mask)
    percentage = count / flags.size * 100

    flag_results.append(
        (flag_name, bit_number, count, percentage)
    )

flag_results.sort(key=lambda item: item[2], reverse=True)

for name, bit, count, percentage in flag_results:
    print(
        f"{name:<12} | "
        f"Bit {bit:2} | "
        f"{count:10} pixels | "
        f"{percentage:8.4f}%"
    )


# Count how many flags are active per pixel
active_flag_count = np.zeros(flags.shape, dtype=np.uint8)

for _, bit, _, _ in flag_results:
    active_flag_count += (
        (flags_int & (1 << bit)) != 0
    )

print("\n=== FLAG COMBINATION STATISTICS ===")

for number in range(active_flag_count.max() + 1):
    count = np.count_nonzero(active_flag_count == number)

    if count > 0:
        print(
            f"{number} active flags: "
            f"{count} pixels "
            f"({count / flags.size * 100:.4f}%)"
        )