from fastapi import APIRouter
from app.api.v1 import auth, assets, projects, documents, calculations, drawings, chat, rag, audit, health, agents

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["calculations"])
api_router.include_router(drawings.router, prefix="/drawings", tags=["drawings"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
