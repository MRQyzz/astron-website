from pathlib import Path
from astropy.io import fits
from astropy.wcs import WCS
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt

fits_file = next(Path("temp").glob("2025W37_1A_0290_1*.fits"))

with fits.open(fits_file, memmap=True) as hdul:
    header = hdul["IMAGE"].header
    wcs = WCS(header)

    print("=== HEADER REFERENCE ===")
    print("CRPIX:", header["CRPIX1"], header["CRPIX2"])
    print("CRVAL:", header["CRVAL1"], header["CRVAL2"])

    print("\n=== ASTROPY WCS ===")
    print("CRPIX:", wcs.wcs.crpix)
    print("CRVAL:", wcs.wcs.crval)
    print("CTYPE:", wcs.wcs.ctype)
    print("CDELT:", wcs.wcs.cdelt)
    print("PC Matrix:")
    print(wcs.wcs.pc)

    print("\n=== TRANSFORMATION TEST ===")

    x = header["CRPIX1"]
    y = header["CRPIX2"]

    for origin in [0, 1]:
        result = wcs.all_pix2world([[x, y]], origin)[0]

        print(f"\nOrigin = {origin}")
        print("RA:", result[0])
        print("Dec:", result[1])

    print("\n=== DISTORTION KEYWORDS ===")

    for key in header:
        if (
            key.startswith(("A_", "B_", "AP_", "BP_"))
            or key.startswith(("CPDIS", "DP", "D2IM"))
        ):
            print(key, "=", header[key])

    print("\n=== CORE WCS VS FULL WCS ===")

    pixel = [[1020.5, 1020.5]]

    core_result = wcs.wcs_pix2world(pixel, 1)
    full_result = wcs.all_pix2world(pixel, 1)

    print("Core WCS:")
    print("RA:", core_result[0][0])
    print("Dec:", core_result[0][1])

    print("\nFull WCS:")
    print("RA:", full_result[0][0])
    print("Dec:", full_result[0][1])

    print("\n=== SIP COEFFICIENTS ===")
    print("A_0_0:", wcs.sip.a[0, 0])
    print("B_0_0:", wcs.sip.b[0, 0])

    print("\n=== SIP DISTORTION AT REFERENCE PIXEL ===")

    sip = wcs.sip

    u = 0.0
    v = 0.0

    dx = sip.a[0, 0]
    dy = sip.b[0, 0]

    print("A(u, v):", dx)
    print("B(u, v):", dy)

    print("\n=== SIP INVERSE POLYNOMIAL ===")

    dx_inverse = sip.ap[0, 0]
    dy_inverse = sip.bp[0, 0]

    print("AP(u, v):", dx_inverse)
    print("BP(u, v):", dy_inverse)

    print("\n=== WCS WITHOUT SIP ===")

    wcs_without_sip = deepcopy(wcs)
    wcs_without_sip.sip = None

    pixel = [[1020.5, 1020.5]]

    result_without_sip = wcs_without_sip.all_pix2world(
        pixel, 1
    )[0]

    print("RA:", result_without_sip[0])
    print("Dec:", result_without_sip[1])

    print("\n=== WCS WITH SIP ===")

    result_with_sip = wcs.all_pix2world(
        pixel, 1
    )[0]

    print("RA:", result_with_sip[0])
    print("Dec:", result_with_sip[1])

    print("\n=== SIP LOW-ORDER COEFFICIENT CHECK ===")

    sip = wcs.sip

    coefficients = {
        "A_0_0": sip.a[0, 0],
        "A_1_0": sip.a[1, 0],
        "A_0_1": sip.a[0, 1],
        "B_0_0": sip.b[0, 0],
        "B_1_0": sip.b[1, 0],
        "B_0_1": sip.b[0, 1],
    }

    for name, value in coefficients.items():
        print(f"{name:8}: {value:.12f}")

    ra, dec = wcs.wcs.crval

    # World coordinate -> pixel coordinate
    pixel = wcs.all_world2pix([[ra, dec]], 1)[0]

    print("=== WORLD TO PIXEL ===")
    print(f"RA: {ra}")
    print(f"Dec: {dec}")
    print(f"X pixel: {pixel[0]}")
    print(f"Y pixel: {pixel[1]}")

    print("\n=== REFERENCE PIXEL ===")
    print(f"CRPIX1: {wcs.wcs.crpix[0]}")
    print(f"CRPIX2: {wcs.wcs.crpix[1]}")

    wcs_core = deepcopy(wcs)
    wcs_core.sip = None

    test_pixels = [
        [1020.5, 1020.5],  # Reference pixel
        [500.0, 500.0],    # Near lower-left region
        [1500.0, 500.0],   # Near lower-right region
        [500.0, 1500.0],   # Near upper-left region
        [1500.0, 1500.0],  # Near upper-right region
    ]

    print("\n=== CORE VS FULL WCS COMPARISON ===")

    for pixel in test_pixels:
        core_world = wcs_core.all_pix2world([pixel], 1)[0]
        full_world = wcs.all_pix2world([pixel], 1)[0]

        print(f"\nPixel: {pixel}")
        print(f"Core WCS: {core_world}")
        print(f"Full WCS: {full_world}")
        print(
            "Difference (arcsec):",
            [
                (full_world[0] - core_world[0]) * 3600,
                (full_world[1] - core_world[1]) * 3600,
            ],
        )

    # --------------------------------------------------
    # 1. Generate pixel coordinate grid
    # --------------------------------------------------

    grid_size = 13

    x_values = np.linspace(1, 2040, grid_size)
    y_values = np.linspace(1, 2040, grid_size)

    xx, yy = np.meshgrid(x_values, y_values)

    pixel_grid = np.column_stack([
        xx.ravel(),
        yy.ravel()
    ])

    # --------------------------------------------------
    # 2. Pixel -> World using Full WCS
    # --------------------------------------------------

    full_world = wcs.all_pix2world(pixel_grid, 1)

    # --------------------------------------------------
    # 3. World -> Pixel using Core WCS
    # --------------------------------------------------

    core_pixel_from_full = wcs_core.all_world2pix(
        full_world,
        1
    )

    # --------------------------------------------------
    # 4. Calculate displacement field
    # --------------------------------------------------

    dx = core_pixel_from_full[:, 0] - pixel_grid[:, 0]
    dy = core_pixel_from_full[:, 1] - pixel_grid[:, 1]

    displacement = np.sqrt(dx**2 + dy**2)

    dx = dx.reshape(grid_size, grid_size)
    dy = dy.reshape(grid_size, grid_size)
    displacement = displacement.reshape(grid_size, grid_size)

    # --------------------------------------------------
    # 5. Print displacement statistics
    # --------------------------------------------------

    print("\n=== SIP DISPLACEMENT STATISTICS ===")

    print(f"Minimum : {np.min(displacement):.6f} pixels")
    print(f"Maximum : {np.max(displacement):.6f} pixels")
    print(f"Mean    : {np.mean(displacement):.6f} pixels")
    print(f"Median  : {np.median(displacement):.6f} pixels")

    # --------------------------------------------------
    # 6. Plot displacement magnitude
    # --------------------------------------------------

    plt.figure(figsize=(9, 7))

    magnitude_plot = plt.scatter(
        xx,
        yy,
        c=displacement,
        cmap="viridis",
        s=100
    )

    plt.colorbar(
        magnitude_plot,
        label="Displacement (pixels)"
    )

    plt.title("SIP Displacement Magnitude")
    plt.xlabel("X Pixel")
    plt.ylabel("Y Pixel")
    plt.xlim(1, 2040)
    plt.ylim(1, 2040)
    plt.gca().set_aspect("equal")
    plt.grid(alpha=0.2)

    plt.show()

    # --------------------------------------------------
    # 7. Plot displacement vector field
    # --------------------------------------------------

    magnification = 30

    plt.figure(figsize=(9, 7))

    plt.quiver(
        xx,
        yy,
        dx * magnification,
        dy * magnification,
        displacement,
        cmap="viridis",
        angles="xy",
        scale_units="xy",
        scale=1
    )

    plt.colorbar(label="Displacement (pixels)")

    plt.title(
        f"SIP Displacement Vector Field "
        f"(Magnification: {magnification}x)"
    )

    plt.xlabel("X Pixel")
    plt.ylabel("Y Pixel")
    plt.xlim(1, 2040)
    plt.ylim(1, 2040)
    plt.gca().set_aspect("equal")
    plt.grid(alpha=0.2)

    plt.show()

    # --------------------------------------------------
    # Radial vs Tangential Displacement Analysis
    # --------------------------------------------------

    # Center of the image
    center_x = 1020.5
    center_y = 1020.5

    # Relative position from image center
    rx = xx - center_x
    ry = yy - center_y

    # Normalize radial direction
    radius = np.sqrt(rx**2 + ry**2)

    safe_radius = np.where(radius == 0, np.nan, radius)

    radial_unit_x = rx / safe_radius
    radial_unit_y = ry / safe_radius

    # Radial displacement component
    radial_component = (
        dx * radial_unit_x +
        dy * radial_unit_y
    )

    # Tangential displacement component
    tangential_component = (
        -dx * radial_unit_y +
        dy * radial_unit_x
    )

    # Calculate statistics
    print("\n=== RADIAL / TANGENTIAL ANALYSIS ===")

    print(
        "Mean radial displacement:",
        np.nanmean(radial_component),
        "pixels"
    )

    print(
        "Mean absolute radial displacement:",
        np.nanmean(np.abs(radial_component)),
        "pixels"
    )

    print(
        "Mean absolute tangential displacement:",
        np.nanmean(np.abs(tangential_component)),
        "pixels"
    )

    print(
        "Mean tangential displacement:",
        np.nanmean(tangential_component),
        "pixels"
    )

