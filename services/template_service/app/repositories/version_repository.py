from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict
from app.models.version import Version
from app.schemas.version_schema import VersionCreate

class VersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_version(self, version: Union[VersionCreate, Dict]) -> Version:
        # Handle both Pydantic models and dicts
        if isinstance(version, dict):
            version_data = version
        else:
            # For Pydantic v2, use model_dump(); for v1, use dict()
            version_data = version.model_dump() if hasattr(version, 'model_dump') else version.dict()
        
        db_version = Version(**version_data)
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        return db_version

    def get_version(self, version_id: int) -> Optional[Version]:
        return self.db.query(Version).filter(Version.id == version_id).first()

    def get_versions_by_template(self, template_logical_id: str, skip: int = 0, limit: int = 100) -> List[Version]:
        return self.db.query(Version).filter(
            Version.template_logical_id == template_logical_id
        ).offset(skip).limit(limit).all()

    def get_latest_version(self, template_logical_id: str) -> Optional[Version]:
        return self.db.query(Version).filter(
            Version.template_logical_id == template_logical_id
        ).order_by(Version.version_number.desc()).first()