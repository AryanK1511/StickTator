import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.logger import CustomLogger
from app.utils.response import error_response


async def global_exception_handler(request: Request, exc: Exception):
    stack_trace = traceback.format_exc()

    CustomLogger.create_log(
        "error", f"Error in {request.url.path}: {str(exc)}\n{stack_trace}"
    )

    response = error_response(
        error={
            "type": exc.__class__.__name__,
            "message": str(exc),
        },
    )

    return JSONResponse(status_code=500, content=response.dict())


def register_exception_handlers(app):
    app.add_exception_handler(Exception, global_exception_handler)
