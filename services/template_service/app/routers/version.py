from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.version_service import VersionService
from app.schemas.version_schema import VersionResponse
from app.utils.logger import logger

router = APIRouter()

@router.get("/templates/{template_id}/versions", response_model=VersionResponse)
async def get_template_versions(
    template_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = VersionService(db)
        result = service.get_versions_by_template(template_id)
        return VersionResponse(
            success=True,
            data=result,
            message="Versions retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{version_id}", response_model=VersionResponse)
async def get_version(
    version_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = VersionService(db)
        result = service.get_version(version_id)
        if not result:
            raise HTTPException(status_code=404, detail="Version not found")
        return VersionResponse(
            success=True,
            data=result,
            message="Version retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get version: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
