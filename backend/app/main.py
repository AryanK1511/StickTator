from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import settings
from app.utils.exception_handlers import register_exception_handlers
from app.utils.logger import CustomLogger
from app.utils.response import success_response
from app.websocket.v1.router import websocket_router


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(title=settings.PROJECT_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(websocket_router, prefix="/ws/v1")
    register_exception_handlers(app)

    return app


# ========== FAST API APPLICATION ==========
app: FastAPI = create_app()


# ========== HEALTH CHECK ROUTE ==========
@app.get("/health")
def health_check() -> JSONResponse:
    CustomLogger.create_log("info", "Health Check")
    return success_response("Server is Healthy")
