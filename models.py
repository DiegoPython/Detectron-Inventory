from sqlalchemy import Column, Integer, String
from config import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    inventory = Column(Integer, nullable=False)
