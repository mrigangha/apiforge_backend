from sys import prefix

from fastapi import APIRouter

from src.api.v1.endpoints import admin_controller, auth_controller

router = APIRouter(prefix="/api/v1")

router.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
router.include_router(admin_controller.router, prefix="/admin", tags=["admin"])
