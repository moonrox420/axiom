from fastapi import APIRouter

from .assets import router as assets_router
from .auth import router as auth_router
from .clients import router as clients_router
from .documents import router as documents_router
from .exceptions import router as exceptions_router
from .invoices import router as invoices_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
api_router.include_router(assets_router, prefix="/assets", tags=["assets"])
api_router.include_router(exceptions_router, prefix="/exceptions", tags=["exceptions"])

__all__ = ["api_router"]
