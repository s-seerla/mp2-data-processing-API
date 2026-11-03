import logging
import time
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Log one request and attach its request ID to the response."""
    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    started = time.perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
        logger.error("Unhandled exception during request", exc_info=True)
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    duration_ms = (time.perf_counter() - started) * 1000
    status_code = response.status_code
    
    msg = f"request_id={request_id} {request.method} {request.url.path} status={status_code} duration={duration_ms:.1f}"
    
    if status_code >= 500:
        logger.error(msg)
    elif status_code >= 400:
        logger.warning(msg)
    else:
        logger.info(msg)
        
    response.headers["X-Request-ID"] = request_id
    return response