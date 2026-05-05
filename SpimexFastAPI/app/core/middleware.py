import logging
import time

from fastapi import Request
from app.core.metrics import REQUEST_COUNT, REQUEST_TIME

logger = logging.getLogger("api")


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        path = request.url.path
        REQUEST_COUNT[path] += 1
        REQUEST_TIME.append(process_time)

        logger.info(
            f"{request.method} {path} "
            f"status={response.status_code} "
            f"time={process_time:.4f}s"
        )

        return response
