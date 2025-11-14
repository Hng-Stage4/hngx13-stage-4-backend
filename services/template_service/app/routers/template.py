from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.config.database import get_db
from app.services.template_service import TemplateService
from app.schemas.template_schema import (
    TemplateCreate, TemplateUpdate, Template, TemplateResponse, TemplateRenderRequest
)
from app.utils.logger import logger

router = APIRouter()

@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    try:
        service = TemplateService(db)
        result = service.create_template(template)
        return TemplateResponse(
            success=True,
            data=result,
            message="Template created successfully"
        )
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        if "ix_templates_logical_id" in str(e):
            raise HTTPException(
                status_code=400, 
                detail=f"A template with logical_id '{template.logical_id}' already exists"
            )
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = TemplateService(db)
        result = service.get_template(template_id)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Handle both SQLAlchemy models and dicts from cache
        if isinstance(result, dict):
            template_data = result
        else:
            # Convert SQLAlchemy model to dict for Pydantic
            template_data = {
                "id": result.id,
                "logical_id": result.logical_id,
                "name": result.name,
                "subject": result.subject,
                "body": result.body,
                "language": result.language,
                "created_at": result.created_at,
                "updated_at": result.updated_at
            }
        
        return TemplateResponse(
            success=True,
            data=template_data,
            message="Template retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    try:
        service = TemplateService(db)
        result = service.update_template(template_id, template_update)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return TemplateResponse(
            success=True,
            data=result,
            message="Template updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{logical_id}/render")
async def render_template(
    logical_id: str,
    render_request: TemplateRenderRequest,
    db: Session = Depends(get_db)
):
    try:
        service = TemplateService(db)
        result = service.render_template(
            logical_id,
            render_request.variables,
            render_request.language
        )
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return {
            "success": True,
            "data": result,
            "message": "Template rendered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to render template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))