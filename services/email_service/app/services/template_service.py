import httpx
from typing import Dict, Optional
from app.config.settings import settings
from app.utils.logger import logger

class TemplateServiceClient:
    def __init__(self):
        self.base_url = settings.template_service_url

    async def get_rendered_template(self, template_id: str, variables: Dict[str, str], language: str = "en") -> Optional[Dict]:
        """Fetch and render template from template service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/templates/{template_id}/render",
                    json={
                        "variables": variables,
                        "language": language
                    }
                )
                response.raise_for_status()
                data = response.json()
                if data.get("success"):
                    return data.get("data")
                else:
                    logger.error(f"Template service error: {data.get('error')}")
                    return None
        except Exception as e:
            logger.error(f"Failed to fetch template: {str(e)}")
            return None
