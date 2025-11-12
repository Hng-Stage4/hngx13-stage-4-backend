from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(String, ForeignKey("templates.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    changes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    template = relationship("Template", back_populates="versions")
