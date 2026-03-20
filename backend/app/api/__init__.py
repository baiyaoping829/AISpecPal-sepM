from fastapi import APIRouter
from .routes import auth, specifications, versions, relations, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(specifications.router, prefix="/specifications", tags=["specifications"])
api_router.include_router(versions.router, prefix="/versions", tags=["versions"])
api_router.include_router(relations.router, prefix="/relations", tags=["relations"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
