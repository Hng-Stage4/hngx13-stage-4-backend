import re
from typing import Dict, Any, Optional
from app.repositories.template_repository import TemplateRepository
from app.repositories.version_repository import VersionRepository
from app.services.cache_service import CacheService
from app.services.variable_substitution import VariableSubstitutionService
from app.utils.logger import logger
from app.routers.metrics import TEMPLATES_LOADED_TOTAL, RENDER_DURATION

class TemplateService:
    def __init__(self, db):
        self.db = db
        self.template_repo = TemplateRepository(db)
        self.version_repo = VersionRepository(db)
        self.cache_service = CacheService()
        self.variable_substitution = VariableSubstitutionService()

    def create_template(self, template_data):
        template = self.template_repo.create_template(template_data)
        # Create initial version
        version_data = {
            "template_logical_id": template.logical_id,
            "version_number": 1,
            "subject": template.subject,
            "body": template.body,
            "changes": "Initial version"
        }
        self.version_repo.create_version(version_data)
        TEMPLATES_LOADED_TOTAL.inc()
        return template

    def get_template(self, logical_id: str, language: str = "en"):
        # Try cache first
        cache_key = f"template:{logical_id}:{language}"
        cached = self.cache_service.get(cache_key)
        if cached:
            return cached

        template = self.template_repo.get_template(logical_id, language)
        if template:
            self.cache_service.set(cache_key, template)
        return template

    def get_template_by_id(self, template_id: str):
        # Try cache first
        cached = self.cache_service.get(f"template:{template_id}")
        if cached:
            return cached

        template = self.template_repo.get_template_by_id(template_id)
        if template:
            self.cache_service.set(f"template:{template_id}", template)
        return template

    def update_template(self, template_id: str, update_data):
        template = self.template_repo.get_template_by_id(template_id)
        if template:
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(template, field, value)
            self.db.commit()
            self.db.refresh(template)

            # Create new version
            latest_version = self.template_repo.get_latest_version_number(template.logical_id)
            version_data = {
                "template_logical_id": template.logical_id,
                "version_number": latest_version + 1,
                "subject": template.subject,
                "body": template.body,
                "changes": "Updated template"
            }
            self.version_repo.create_version(version_data)
            # Invalidate cache
            cache_key = f"template:{template.logical_id}:{template.language}"
            self.cache_service.delete(cache_key)
        return template

    def render_template(self, template_id: str, variables: Dict[str, Any], language: str = "en") -> Optional[Dict]:
        import time
        start_time = time.time()

        template = self.get_template(template_id)
        if not template:
            return None

        # For now, assume single language, but could extend for localization
        subject = self.variable_substitution.substitute(template.subject or "", variables)
        body = self.variable_substitution.substitute(template.body, variables)

        render_time = time.time() - start_time
        RENDER_DURATION.observe(render_time)

        return {
            "subject": subject,
            "body": body
        }
