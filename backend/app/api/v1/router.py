from fastapi import APIRouter

from app.api.v1.endpoints import machines, report, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
