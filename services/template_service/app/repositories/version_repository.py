from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.version import Version
from app.schemas.version_schema import VersionCreate

class VersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_version(self, version: VersionCreate) -> Version:
        db_version = Version(**version.dict())
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        return db_version

    def get_version(self, version_id: int) -> Optional[Version]:
        return self.db.query(Version).filter(Version.id == version_id).first()

    def get_versions_by_template(self, template_id: str, skip: int = 0, limit: int = 100) -> List[Version]:
        return self.db.query(Version).filter(Version.template_id == template_id).offset(skip).limit(limit).all()

    def get_latest_version(self, template_id: str) -> Optional[Version]:
        return self.db.query(Version).filter(Version.template_id == template_id).order_by(Version.version_number.desc()).first()
