import random

def exponential_backoff(retry_count: int, base_delay: int = 1, max_delay: int = 300) -> float:
    """Calculate exponential backoff delay with jitter"""
    delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)
    jitter = random.uniform(0.5, 1.5)
    return delay * jitter
