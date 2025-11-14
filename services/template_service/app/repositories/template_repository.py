from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Union, Dict
from app.models.template import Template
from app.models.version import Version
from app.schemas.template_schema import TemplateCreate, TemplateUpdate
import uuid

class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_template(self, template: Union[TemplateCreate, Dict]) -> Template:
        # Handle both Pydantic models and dicts
        if isinstance(template, dict):
            template_data = template
        else:
            # For Pydantic v2, use model_dump(); for v1, use dict()
            template_data = template.model_dump() if hasattr(template, 'model_dump') else template.dict()
        
        # Generate UUID for id if not provided
        if 'id' not in template_data or not template_data['id']:
            template_data['id'] = str(uuid.uuid4())
        
        db_template = Template(**template_data)
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def get_template(self, logical_id: str, language: str = "en") -> Optional[Template]:
        return self.db.query(Template).filter(
            Template.logical_id == logical_id,
            Template.language == language
        ).first()

    def get_template_by_id(self, template_id: str) -> Optional[Template]:
        return self.db.query(Template).filter(Template.id == template_id).first()

    def get_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
        return self.db.query(Template).offset(skip).limit(limit).all()

    def update_template(self, template_id: str, template_update: Union[TemplateUpdate, Dict]) -> Optional[Template]:
        db_template = self.get_template_by_id(template_id)
        if db_template:
            # Handle both Pydantic models and dicts
            if isinstance(template_update, dict):
                update_data = template_update
            else:
                update_data = template_update.model_dump(exclude_unset=True) if hasattr(template_update, 'model_dump') else template_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(db_template, field, value)
            self.db.commit()
            self.db.refresh(db_template)
        return db_template

    def delete_template(self, template_id: str) -> bool:
        db_template = self.get_template_by_id(template_id)
        if db_template:
            self.db.delete(db_template)
            self.db.commit()
            return True
        return False

    def get_latest_version_number(self, logical_id: str) -> int:
        version = self.db.query(Version).filter(
            Version.template_logical_id == logical_id
        ).order_by(desc(Version.version_number)).first()
        return version.version_number if version else 0