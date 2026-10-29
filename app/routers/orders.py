from typing import Annotated
from fastapi import APIRouter, HTTPException, Path
from app.database import DB
from app.models import MenuItem, Order, OrderItem
from app.schemas import OrderCreate, OrderOut
 
router = APIRouter(prefix="/orders", tags=["Orders"])
 
@router.post("", response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, db: DB):
    ids = [line.item_id for line in payload.lines]
    if len(ids) != len(set(ids)):  # BR7
        raise HTTPException(422, "Mỗi món chỉ xuất hiện một lần trong đơn")
    order = Order(student_code=payload.student_code)
    for line in payload.lines:
        item = db.get(MenuItem, line.item_id)
        if item is None:
            raise HTTPException(422, f"Món id={line.item_id} không tồn tại")
        if not item.available:  # BR7
            raise HTTPException(409, f"Món '{item.name}' đã hết")
        order.lines.append(OrderItem(item_id=item.id,
                                     quantity=line.quantity,
                                     unit_price=item.price))  # BR8
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
 
@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: Annotated[int, Path(gt=0)], db: DB):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(404, f"Không tìm thấy đơn id={order_id}")
    return order
