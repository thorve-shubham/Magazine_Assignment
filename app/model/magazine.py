from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR

class MagazineInformation(Base):
    __tablename__ = "magazine_information"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String)
    category = Column(String)
    publish_date = Column(Date)

    # One-to-One relationship with MagazineContent
    content = relationship("MagazineContent", back_populates="magazine", uselist=False, cascade="all, delete")

class MagazineContent(Base):
    __tablename__ = "magazine_content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    magazine_id = Column(Integer, ForeignKey("magazine_information.id"))
    content = Column(String)
    content_tsvector = Column(TSVECTOR)
    content_embedding = Column(Vector(384))

    # One-to-One relationship back to MagazineInformation
    magazine = relationship("MagazineInformation", back_populates="content")