from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import DB
from app.models import Category
from app.schemas import CategoryCreate, CategoryOut
 
router = APIRouter(prefix="/categories", tags=["Categories"])
 
@router.get("", response_model=list[CategoryOut])
def list_categories(db: DB):
    return db.scalars(select(Category).order_by(Category.id)).all()
 
@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: DB):
    cat = Category(name=payload.name)
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:  # BR5: vi phạm UNIQUE
        db.rollback()
        raise HTTPException(409, f"Danh mục '{payload.name}' đã tồn tại")
    db.refresh(cat)
    return cat
