"""Async utilities for sync/async interop."""

import asyncio
from typing import Any, Awaitable, Callable, Coroutine, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine in a sync context.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # If loop is already running, we need to use a different approach
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)


def sync_to_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """
    Convert a sync function to an async function.

    Args:
        func: The sync function to convert

    Returns:
        An async function that wraps the sync function
    """
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return async_wrapper
