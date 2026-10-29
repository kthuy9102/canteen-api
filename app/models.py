from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
 
class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    items: Mapped[list["MenuItem"]] = relationship(
        back_populates="category")
 
class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (CheckConstraint("price > 0", name="ck_price_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[int]
    available: Mapped[bool] = mapped_column(default=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())
    category: Mapped["Category"] = relationship(back_populates="items")
 
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_code: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    lines: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan")
 
    @property
    def total(self) -> int:  # tổng tiền, không lưu thành cột
        return sum(l.quantity * l.unit_price for l in self.lines)
 
class OrderItem(Base):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[int]
    order: Mapped["Order"] = relationship(back_populates="lines")
    item: Mapped["MenuItem"] = relationship()
    image_url: Mapped[str | None] = mapped_column(String(255))