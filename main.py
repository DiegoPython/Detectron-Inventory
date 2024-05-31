from Detector import *
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from sqlalchemy.orm import Session
from models import Product 
from dependencies import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to '*' to allow all origins, or specify specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allowed HTTP methods
    allow_headers=["*"],  # Set to '*' to allow all headers, or specify specific headers
)

@app.get("/")
def posts():
    return {"message" : "this is working"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploaded_images/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    detector = Detector(model_type="LVIS")
    detector.onImage("./uploaded_images/"+file.filename)
    for key, value in dict(detector.getObjectsDetected()).items():
        db_products = db.query(Product).filter(Product.name == key).first()
        if db_products is None:
            db_products = Product(name=key, inventory=value)
            db.add(db_products)
            db.commit()
            db.refresh(db_products)
        else:
            updatedInventory = db_products.inventory + value
            db_products.inventory=updatedInventory
            db.commit()
            db.refresh(db_products)
    return {"message" : "success"}

@app.get("/products/")
def read_users(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products 
