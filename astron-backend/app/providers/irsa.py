from app.core.config import IRSA_SIA_URL, IRSA_TIMEOUT
from app.core.http_client import request_with_retry, get_retry_after
import math
import httpx
from io import BytesIO
# from astropy.table import Table
from astropy.io.votable import parse
from pathlib import Path
from urllib.parse import urlparse
from app.core.config import (
    IRSA_SIA_URL,
    IRSA_TIMEOUT,
    FITS_DOWNLOAD_DIR,
    FITS_TIMEOUT,
    FITS_MAX_SIZE,
    FITS_MAX_ATTEMPTS,
)
import asyncio
import hashlib
import os
import re

def build_sia2_params(
    ra: float,
    dec:  float,
    radius: float,
    collection: str = "spherex_dr1",
    maxrec: int = 100,
) -> dict:
    """
    Build parameters for an IRSA SIA2 spatial query.
    """

    values = {
        "ra": ra,
        "dec": dec,
        "radius": radius,
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a numeric value")

        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

    if not 0 <= ra < 360:
        raise ValueError("RA must be between 0 and 360 degrees")

    if not -90 <= dec <= 90:
        raise ValueError("Dec must be between -90 and 90 degrees")

    if not 0 < radius <= 180:
        raise ValueError("Radius must be between 0 and 180 degrees")

    if not isinstance(collection, str) or not collection.strip():
        raise ValueError("Collection must be a non-empty string")

    if isinstance(maxrec, bool) or not isinstance(maxrec, int) or maxrec < 1:
        raise ValueError("maxrec must be a positive integer")

    return {
        "COLLECTION": collection,
        "POS": f"circle {float(ra)!r} {float(dec)!r} {float(radius)!r}",
        "MAXREC": maxrec,
    }

async def search_observations(
    ra: float,
    dec: float,
    radius: float,
    collection: str = "spherex_dr1",
    maxrec: int = 100,
) -> str:
    """
    Search SPHEREx observations through IRSA SIA2.

    Returns the raw VOTable XML response.
    """

    params = build_sia2_params(
        ra=ra,
        dec=dec,
        radius=radius,
        collection=collection,
        maxrec=maxrec,
    )

    timeout = httpx.Timeout(
        connect=20.0,
        read=IRSA_TIMEOUT,
        write=30.0,
        pool=20.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await request_with_retry(
            client,
            "GET",
            IRSA_SIA_URL,
            params=params,
        )

        content_type = dict(response.headers).get("content-type", "")

        # if "xml" not in content_type.lower() and "votable" not in content_type.lower():
        #     raise RuntimeError(
        #         f"IRSA returned an unexpected content type: {content_type}"
        #     )
        # print("IRSA status:", response.status_code)
        # print("IRSA headers:", dict(response.headers))
        # print("IRSA content type:", content_type)
        # print("IRSA response preview:", response.text[:300])

        if (
            content_type
            and "xml" not in content_type.lower()
            and "votable" not in content_type.lower()
        ):
            raise RuntimeError(
                f"IRSA returned an unexpected content type: {content_type}"
            )

        print("IRSA status:", response.status_code)
        print("IRSA content type:", content_type)
        print("IRSA response size:", len(response.content))


        return response.text


def parse_sia2_response(votable_xml: str) -> list[dict]:
    """
    Parse an IRSA SIA2 VOTable XML response
    into a list of observation records.
    """

    if not isinstance(votable_xml, str) or not votable_xml.strip():
        raise ValueError("VOTable response must be a non-empty string")

    try:
        votable = parse(
            BytesIO(votable_xml.encode("utf-8"))
        )

        table_element = votable.get_first_table()

        if table_element is None:
            raise ValueError("VOTable contains no table")

        table = table_element.to_table(use_names_over_ids=True)

    except Exception as exc:
        raise ValueError(
            "Failed to parse IRSA VOTable response"
        ) from exc

    records = []

    for row in table:
        record = {}

        for column in table.colnames:
            value = row[column]

            if getattr(value, "mask", False):
                value = None
            elif hasattr(value, "item"):
                value = value.item()

            record[column] = value

        records.append(record)

    return records

async def download_fits_product(
    access_url: str,
    obs_id: str,
) -> dict:
    """
    Download one FITS product from an approved IRSA host.
    The file is streamed into a temporary .part file and
    renamed only after successful validation.
    """

    parsed_url = urlparse(access_url)

    allowed_hosts = {
        "irsa.ipac.caltech.edu",
    }

    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname not in allowed_hosts
        or parsed_url.username
        or parsed_url.password
    ):
        raise ValueError("Untrusted FITS download URL")

    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")

    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id)
    url_hash = hashlib.sha256(
        access_url.encode("utf-8")
    ).hexdigest()[:12]

    FITS_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


    filename = f"{safe_obs_id}_{url_hash}.fits"
    destination = FITS_DOWNLOAD_DIR / filename
    temporary = destination.with_suffix(".fits.part")

    # Check whether the FITS product has already been downloaded.
    if destination.exists():
        if destination.is_file() and destination.stat().st_size > 0:
            return {
                "obs_id": obs_id,
                "filename": filename,
                "path": str(destination),
                "size_bytes": destination.stat().st_size,
                "status": "already_downloaded",
            }

    timeout = httpx.Timeout(
        connect=20.0,
        read=FITS_TIMEOUT,
        write=30.0,
        pool=20.0,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            for attempt in range(FITS_MAX_ATTEMPTS):
                try:
                    async with client.stream(
                        "GET",
                        access_url,
                    ) as response:
                        final_host = response.url.host

                        if final_host not in allowed_hosts:
                            raise ValueError(
                                "FITS redirect reached an untrusted host"
                            )
                        if response.status_code == 429 or response.status_code >= 500:
                            if attempt == FITS_MAX_ATTEMPTS - 1:
                                response.raise_for_status()

                            retry_after = get_retry_after(response)
                            delay = (
                                retry_after
                                if retry_after is not None
                                else min(2 ** attempt, 8)
                            )
                            await asyncio.sleep(min(delay, 30))
                            continue

                        response.raise_for_status()
                        content_length = response.headers.get(
                            "content-length"
                        )

                        if content_length:
                            if int(content_length) > FITS_MAX_SIZE:
                                raise ValueError(
                                    "FITS product exceeds maximum size"
                                )

                        total_bytes = 0
                        header = bytearray()

                        with temporary.open("wb") as file:
                            async for chunk in response.aiter_bytes(
                                chunk_size=1024*1024
                            ):
                                if not chunk:
                                    continue

                                total_bytes += len(chunk)

                                if total_bytes > FITS_MAX_SIZE:
                                    raise ValueError(
                                        "FITS product exceeds maximum size"
                                    )

                                if len(header) < 80:
                                    remaining = 80 - len(header)
                                    header.extend(chunk[:remaining])

                                file.write(chunk)

                        if not bytes(header).startswith(b"SIMPLE  ="):
                            raise ValueError(
                                "Download file is not a valid FITS file"
                            )

                        os.replace(temporary, destination)
                        

                        return {
                            "obs_id": obs_id,
                            "filename": filename,
                            "path": str(destination),
                            "size_bytes": total_bytes,
                            "status": "downloaded",
                        }
                except (httpx.TimeoutException, httpx.NetworkError):
                    if attempt == FITS_MAX_ATTEMPTS - 1:
                        raise

                    await asyncio.sleep(min(2 ** attempt, 8))

        raise RuntimeError("FITS download failed")

    except Exception:
        temporary.unlink(missing_ok=True)
        raise