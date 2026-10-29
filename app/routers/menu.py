from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import DB
from app.models import Category, MenuItem
from app.schemas import MenuItemCreate, MenuItemOut, MenuItemUpdate
 
router = APIRouter(prefix="/menu-items", tags=["Menu"])
ItemId = Annotated[int, Path(gt=0)]
 
def get_or_404(db: Session, item_id: int) -> MenuItem:
    item = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(404, f"Không tìm thấy món id={item_id}")
    return item
 
def check_category(db: Session, category_id: int) -> None:  # BR6
    if db.get(Category, category_id) is None:
        raise HTTPException(422, f"Danh mục id={category_id} không tồn tại")
 
def commit_or_409(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, message)

@router.get("", response_model=list[MenuItemOut])
def list_items(
    db: DB,
    category_id: int | None = None,
    available: bool | None = None,
    max_price: Annotated[int | None, Query(gt=0)] = None,
    sort: Literal["id", "price", "name"] = "id",
    order: Literal["asc", "desc"] = "asc",
):
    stmt = select(MenuItem)
    if category_id:
        stmt = stmt.where(MenuItem.category_id == category_id)
    if available is not None:
        stmt = stmt.where(MenuItem.available == available)
    if max_price:
        stmt = stmt.where(MenuItem.price <= max_price)
    column = getattr(MenuItem, sort)
    stmt = stmt.order_by(column.desc() if order == "desc" else column)
    return db.scalars(stmt).all()
 
@router.get("/{item_id}", response_model=MenuItemOut)
def get_item(item_id: ItemId, db: DB):
    return get_or_404(db, item_id)

@router.post("", response_model=MenuItemOut, status_code=201)
def create_item(payload: MenuItemCreate, response: Response, db: DB):
    check_category(db, payload.category_id)
    item = MenuItem(**payload.model_dump())
    db.add(item)
    commit_or_409(db, f"Món '{payload.name}' đã có trong thực đơn")
    db.refresh(item)
    response.headers["Location"] = f"/menu-items/{item.id}"
    return item
 
@router.put("/{item_id}", response_model=MenuItemOut)
def replace_item(item_id: ItemId, payload: MenuItemCreate, db: DB):
    item = get_or_404(db, item_id)
    check_category(db, payload.category_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    commit_or_409(db, f"Món '{payload.name}' đã có trong thực đơn")
    db.refresh(item)
    return item
 
@router.patch("/{item_id}", response_model=MenuItemOut)
def update_item(item_id: ItemId, payload: MenuItemUpdate, db: DB):
    item = get_or_404(db, item_id)
    changes = payload.model_dump(exclude_unset=True)
    if "category_id" in changes:
        check_category(db, changes["category_id"])
    for key, value in changes.items():
        setattr(item, key, value)
    commit_or_409(db, "Tên món đã có trong thực đơn")
    db.refresh(item)
    return item
 
@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: ItemId, db: DB):
    item = get_or_404(db, item_id)
    db.delete(item)
    commit_or_409(db, "Món đã có trong đơn hàng, hãy đánh dấu hết "
                      "thay vì xóa")  # BR8: vi phạm khóa ngoại
