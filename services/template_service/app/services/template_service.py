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

    def _template_to_dict(self, template) -> dict:
        """Convert SQLAlchemy Template model to dictionary for caching."""
        return {
            "id": template.id,
            "logical_id": template.logical_id,
            "name": template.name,
            "subject": template.subject,
            "body": template.body,
            "language": template.language,
            "created_at": str(template.created_at),
            "updated_at": str(template.updated_at) if template.updated_at else None
        }

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
            logger.info(f"Cache hit for template: {logical_id}")
            # Return the dict - let the router handle serialization
            # Note: We're not reconstructing the model to avoid session issues
            return cached

        template = self.template_repo.get_template(logical_id, language)
        if template:
            template_dict = self._template_to_dict(template)
            self.cache_service.set(cache_key, template_dict)
            logger.info(f"Cached template: {logical_id}")
        return template

    def get_template_by_id(self, template_id: str):
        # Try cache first
        cache_key = f"template:id:{template_id}"
        cached = self.cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for template id: {template_id}")
            return cached

        template = self.template_repo.get_template_by_id(template_id)
        if template:
            template_dict = self._template_to_dict(template)
            self.cache_service.set(cache_key, template_dict)
            logger.info(f"Cached template id: {template_id}")
        return template

    def update_template(self, template_id: str, update_data):
        # Let the repository handle the Pydantic model conversion
        template = self.template_repo.update_template(template_id, update_data)
        
        if template:
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
            cache_key_id = f"template:id:{template_id}"
            self.cache_service.delete(cache_key)
            self.cache_service.delete(cache_key_id)
            logger.info(f"Invalidated cache for template: {template.logical_id}")
        
        return template

    def render_template(self, template_id: str, variables: Dict[str, Any], language: str = "en") -> Optional[Dict]:
        import time
        start_time = time.time()

        template = self.get_template(template_id, language)
        if not template:
            return None

        # Handle both SQLAlchemy models and dicts from cache
        if isinstance(template, dict):
            subject = template.get("subject", "")
            body = template.get("body", "")
        else:
            subject = template.subject or ""
            body = template.body

        # Substitute variables
        rendered_subject = self.variable_substitution.substitute(subject, variables)
        rendered_body = self.variable_substitution.substitute(body, variables)

        render_time = time.time() - start_time
        RENDER_DURATION.observe(render_time)

        return {
            "subject": rendered_subject,
            "body": rendered_body
        }