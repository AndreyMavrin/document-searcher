from sqlalchemy import Column, Integer, DateTime, Text, String
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    rubrics = Column(ARRAY(String))
    created_date = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rubrics": self.rubrics,
            "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S") if self.created_date else None
        }