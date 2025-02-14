from flask import current_app
from functools import wraps
import time

def monitor_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start
            current_app.logger.info(
                f"DB Operation: {f.__name__} completed in {duration:.2f}s"
            )
            return result
        except Exception as e:
            current_app.logger.error(
                f"DB Operation: {f.__name__} failed: {str(e)}"
            )
            raise
    return decorated_function 