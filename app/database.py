import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
 
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=True)  # echo: in câu SQL
SessionLocal = sessionmaker(bind=engine)
 
class Base(DeclarativeBase):
    pass
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
DB = Annotated[Session, Depends(get_db)]  # dùng trong các endpoint
