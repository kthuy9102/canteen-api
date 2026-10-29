from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
 
class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
 
class CategoryOut(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
 
class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category_id: int = Field(gt=0)
    price: int = Field(gt=0, le=200_000, multiple_of=1000)
    available: bool = True
 
class MenuItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    category_id: int | None = Field(default=None, gt=0)
    price: int | None = Field(default=None, gt=0, le=200_000,
                              multiple_of=1000)
    available: bool | None = None
 
class MenuItemOut(MenuItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    updated_at: datetime
 
class OrderLineIn(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=20)
 
class OrderCreate(BaseModel):
    student_code: str = Field(pattern=r"^\d{10}$")
    lines: list[OrderLineIn] = Field(min_length=1)
 
class OrderLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item_id: int
    quantity: int
    unit_price: int
 
class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_code: str
    created_at: datetime
    lines: list[OrderLineOut]
    total: int
