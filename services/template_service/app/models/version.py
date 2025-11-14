from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_logical_id = Column(String, ForeignKey("templates.logical_id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    changes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    template = relationship("Template", back_populates="versions")
