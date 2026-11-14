import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import httpx

MAX_ATTEMPTS = 3
BASE_DELAY = 1.0 # seconds
MAX_DELAY = 8.0 # seconds

def get_retry_after(response: httpx.Response) -> float | None:
    """
    Read and parse the Retry-After header.

    Supports both:
    - Delay in seconds
    - HTTP date
    """

    value = response.headers.get("Retry-After")

    if value is None:
        return None

    try:
        delay = float(value)
        return max(0.0, delay)
    except ValueError:
        pass

    try:
        retry_date = parsedate_to_datetime(value)

        if retry_date.tzinfo is None:
            retry_date = retry_date.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        return max(0.0, (retry_date - now).total_seconds())
    
    except (TypeError, ValueError, OverflowError):
        return None

async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    max_attempts: int = MAX_ATTEMPTS,
    base_delay: float = BASE_DELAY,
    max_delay: float = MAX_DELAY,
    **kwargs,
) -> httpx.Response:
    """
    Send an HTTP request with bounded retry handling.

    Retries:
    - Timeout errors
    - Network errors
    - HTTP 429
    - HTTP 5xx
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    if base_delay < 0 or max_delay < 0:
        raise ValueError("base_delay and max_delay cannot be negative")

    for attempt in range(max_attempts):
        try:
            response = await client.request(
                method,
                url,
                **kwargs,
            )

            if response.status_code == 429:
                if attempt == max_attempts - 1:
                    response.raise_for_status()

                retry_after = get_retry_after(response)
                delay = retry_after if retry_after is not None else base_delay * (2 ** attempt)
                await asyncio.sleep(min(delay, max_delay))
                continue

            if 500 <= response.status_code <= 599:
                if attempt == max_attempts - 1:
                    response.raise_for_status()

                delay = min(base_delay * (2 ** attempt), max_delay)
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            return response

        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == max_attempts - 1:
                raise

            delay = min(base_delay * (2 ** attempt), max_delay)
            await asyncio.sleep(delay)

    raise RuntimeError("HTTP request failed after all retry attempts")