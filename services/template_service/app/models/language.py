from sqlalchemy import Column, String, Text
from app.config.database import Base

class Language(Base):
    __tablename__ = "languages"

    code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    direction = Column(String, default="ltr")  # ltr or rtl
