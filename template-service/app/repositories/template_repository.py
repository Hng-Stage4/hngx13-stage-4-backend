from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.template import Template
from app.models.version import Version
from app.schemas.template_schema import TemplateCreate, TemplateUpdate

class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_template(self, template: TemplateCreate) -> Template:
        db_template = Template(**template.dict())
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def get_template(self, template_id: str) -> Optional[Template]:
        return self.db.query(Template).filter(Template.id == template_id).first()

    def get_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
        return self.db.query(Template).offset(skip).limit(limit).all()

    def update_template(self, template_id: str, template_update: TemplateUpdate) -> Optional[Template]:
        db_template = self.get_template(template_id)
        if db_template:
            update_data = template_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_template, field, value)
            self.db.commit()
            self.db.refresh(db_template)
        return db_template

    def delete_template(self, template_id: str) -> bool:
        db_template = self.get_template(template_id)
        if db_template:
            self.db.delete(db_template)
            self.db.commit()
            return True
        return False

    def get_latest_version_number(self, template_id: str) -> int:
        version = self.db.query(Version).filter(Version.template_id == template_id).order_by(desc(Version.version_number)).first()
        return version.version_number if version else 0
