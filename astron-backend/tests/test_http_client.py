
import asyncio

import httpx
import pytest

from app.core.http_client import request_with_retry


@pytest.fixture
def run_async():
    def runner(coroutine):
        return asyncio.run(coroutine)

    return runner


def test_retry_after_server_error(monkeypatch, run_async):
    attempts = 0
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(503)

        return httpx.Response(200, json={"status": "ok"})

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            response = await request_with_retry(
                client,
                "GET",
                "https://example.com",
            )

            return response

    response = run_async(scenario())

    assert response.status_code == 200
    assert attempts == 2
    assert delays == [1.0]


def test_retry_after_rate_limit(monkeypatch, run_async):
    attempts = 0
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "3"},
            )

        return httpx.Response(200)

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await request_with_retry(
                client,
                "GET",
                "https://example.com",
            )

    response = run_async(scenario())

    assert response.status_code == 200
    assert attempts == 2
    assert delays == [3.0]


def test_retry_after_network_error(monkeypatch, run_async):
    attempts = 0
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise httpx.ConnectError("Connection failed")

        return httpx.Response(200)

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await request_with_retry(
                client,
                "GET",
                "https://example.com",
            )

    response = run_async(scenario())

    assert response.status_code == 200
    assert attempts == 2
    assert delays == [1.0]


def test_do_not_retry_bad_request(monkeypatch, run_async):
    attempts = 0
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    def handler(request):
        nonlocal attempts
        attempts += 1

        return httpx.Response(400)

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await request_with_retry(
                client,
                "GET",
                "https://example.com",
            )

    with pytest.raises(httpx.HTTPStatusError):
        run_async(scenario())

    assert attempts == 1
    assert delays == []
