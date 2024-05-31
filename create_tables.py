# create_tables.py
from config import engine, Base
from models import Product 

Base.metadata.create_all(bind=engine)
