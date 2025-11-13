import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    logical_id = Column(String, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    versions = relationship(
        "Version",
        back_populates="template",
        cascade="all, delete-orphan"
    )
