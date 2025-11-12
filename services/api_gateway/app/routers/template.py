# ============================================
# api-gateway/app/routers/template.py
# ============================================
from fastapi import APIRouter, Request, Depends
from app.middleware.auth import get_current_user
import httpx

router = APIRouter()
TEMPLATE_SERVICE_URL = "http://template-service:8003"


@router.post("/templates")
async def create_template(
    request: Request, current_user: dict = Depends(get_current_user)
):
    """Proxy template creation to template service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TEMPLATE_SERVICE_URL}/api/templates",
            json=await request.json(),
            headers=dict(request.headers),
        )
        return response.json()


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str, current_user: dict = Depends(get_current_user)
):
    """Proxy template retrieval to template service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TEMPLATE_SERVICE_URL}/api/templates/{template_id}"
        )
        return response.json()


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str, request: Request, current_user: dict = Depends(get_current_user)
):
    """Proxy template update to template service"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{TEMPLATE_SERVICE_URL}/api/templates/{template_id}",
            json=await request.json(),
            headers=dict(request.headers),
        )
        return response.json()


@router.post("/templates/{logical_id}/render")
async def render_template(
    logical_id: str, request: Request, current_user: dict = Depends(get_current_user)
):
    """Proxy template rendering to template service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TEMPLATE_SERVICE_URL}/api/templates/{logical_id}/render",
            json=await request.json(),
            headers=dict(request.headers),
        )
        return response.json()


@router.get("/templates/{template_id}/versions")
async def get_template_versions(
    template_id: str, current_user: dict = Depends(get_current_user)
):
    """Proxy template versions to template service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TEMPLATE_SERVICE_URL}/api/templates/{template_id}/versions"
        )
        return response.json()
