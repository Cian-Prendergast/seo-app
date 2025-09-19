from functools import wraps
import time
import logging
from state import ContentOptimizationState

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(state: ContentOptimizationState) -> ContentOptimizationState:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(state)
                except Exception as e:
                    last_exception = e
                    logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                    state = {
                        **state,
                        "retry_count": state.get("retry_count", 0) + 1
                    }
            error_msg = f"All {max_retries} attempts failed. Last error: {str(last_exception)}"
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": f"{func.__name__}_failed"
            }
        return wrapper
    return decorator
