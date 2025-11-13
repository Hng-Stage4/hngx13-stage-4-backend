import httpx
import logging
import json
from app.config.settings import settings
from app.config.redis import redis_manager

logger = logging.getLogger(__name__)

TEMPLATE_CACHE_TTL = 3600  # seconds (1 hour)


class TemplateService:
    def __init__(self):
        self.base_url = settings.TEMPLATE_SERVICE_URL
        logger.debug(f"TemplateService initialized with base_url={self.base_url}")

    async def get_template(self, template_code: str, language: str = None) -> dict:
        """
        Fetch a template from the Template Service with optional language.
        Uses Redis caching to reduce network calls.
        """
        cache_key = f"template:{template_code}:{language or 'default'}"
        logger.debug(f"Fetching template: code={template_code}, language={language}, cache_key={cache_key}")

        try:
            # Check Redis cache first
            cached = await redis_manager.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key={cache_key}")
                try:
                    data = json.loads(cached)
                    logger.debug(f"Cache data successfully decoded for {cache_key}")
                    return data
                except json.JSONDecodeError:
                    logger.warning(f"Corrupted cache data for {cache_key}, ignoring and fetching fresh")

            logger.info(f"Cache miss for {cache_key}, fetching from Template Service")

            # Fetch from Template Service API
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {"language": language} if language else None
                logger.debug(f"Sending GET {self.base_url}/api/v1/templates/{template_code} with params={params}")
                response = await client.get(
                    f"{self.base_url}/api/v1/templates/{template_code}",
                    params=params
                )
                response.raise_for_status()

                template_data = response.json()
                logger.debug(f"Response received for template_code={template_code}: {template_data}")

                # Cache in Redis
                await redis_manager.set(
                    cache_key, json.dumps(template_data), ttl=TEMPLATE_CACHE_TTL
                )
                logger.info(f"Template {template_code} cached with TTL={TEMPLATE_CACHE_TTL}s")

                return template_data

        except httpx.RequestError as e:
            logger.error(
                f"Network error contacting Template Service for code={template_code}: {e}",
                exc_info=True
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Template Service returned HTTP {e.response.status_code} for code={template_code}, response={e.response.text}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error fetching template {template_code}: {e}")

        logger.warning(f"Returning None for template_code={template_code} due to previous errors")
        return None
