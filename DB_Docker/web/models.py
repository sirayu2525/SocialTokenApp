# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class DataRecord(Base):
    __tablename__ = "data_records"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    value = Column(String)
