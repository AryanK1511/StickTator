from fastapi import APIRouter

from app.websocket.v1.endpoints import connection, frontend, machine  # noqa

websocket_router = APIRouter()
# websocket_router.include_router(
#     connection.router, prefix="/connection", tags=["connection"]
# )
websocket_router.include_router(machine.router, prefix="/machine", tags=["machine"])
websocket_router.include_router(frontend.router, prefix="/frontend", tags=["frontend"])
