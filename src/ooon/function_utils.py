import asyncio
import functools
import logging

import httpx


def async_retry(max_attempts=3, delay=1, exceptions=(Exception,), backoff=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if isinstance(e, httpx.HTTPStatusError):
                        logging.warning(
                            f"函数 {func.__name__} 出现异常: {e},{e.response.text}，{current_delay} 秒后重试({attempt}/{max_attempts})")
                    else:
                        logging.warning(
                            f"函数 {func.__name__} 出现异常: {e}，{current_delay} 秒后重试({attempt}/{max_attempts})")

                    if attempt >= max_attempts:
                        logging.error(f"函数 {func.__name__} 达到最大重试次数 {max_attempts}，抛出异常 {e}")
                        raise e
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            return None

        return wrapper

    return decorator