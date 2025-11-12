from app.repositories.version_repository import VersionRepository
from app.routers.metrics import VERSION_COUNT_TOTAL

class VersionService:
    def __init__(self, db):
        self.version_repo = VersionRepository(db)

    def create_version(self, version_data):
        version = self.version_repo.create_version(version_data)
        VERSION_COUNT_TOTAL.inc()
        return version

    def get_version(self, version_id: int):
        return self.version_repo.get_version(version_id)

    def get_versions_by_template(self, template_id: str):
        return self.version_repo.get_versions_by_template(template_id)

    def get_latest_version(self, template_id: str):
        return self.version_repo.get_latest_version(template_id)
