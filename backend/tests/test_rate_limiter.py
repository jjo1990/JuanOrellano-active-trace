import asyncio

import pytest

from app.core.rate_limiter import InMemoryRateLimiter


class TestRateLimiter:
    async def test_allows_up_to_max_attempts(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)
        for _ in range(5):
            assert await limiter.check("test:alice@test.com") is True

    async def test_blocks_sixth_attempt(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)
        for _ in range(5):
            await limiter.check("test:alice@test.com")
        assert await limiter.check("test:alice@test.com") is False

    async def test_window_resets_after_time(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=1)
        for _ in range(5):
            await limiter.check("test:alice@test.com")
        assert await limiter.check("test:alice@test.com") is False
        await asyncio.sleep(1.1)
        assert await limiter.check("test:alice@test.com") is True

    async def test_different_keys_do_not_interfere(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)
        for _ in range(5):
            await limiter.check("test:alice@test.com")
        assert await limiter.check("test:bob@test.com") is True

    async def test_reset_clears_counter(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)
        for _ in range(5):
            await limiter.check("test:alice@test.com")
        assert await limiter.check("test:alice@test.com") is False
        await limiter.reset("test:alice@test.com")
        assert await limiter.check("test:alice@test.com") is True

    async def test_concurrent_safety(self):
        limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=60)

        async def attempt():
            return await limiter.check("test:alice@test.com")

        results = await asyncio.gather(*[attempt() for _ in range(10)])
        allowed = sum(1 for r in results if r)
        blocked = sum(1 for r in results if not r)
        assert allowed == 5
        assert blocked == 5
