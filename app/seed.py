from sqlalchemy import select
from app.database import SessionLocal
from app.models import Category, MenuItem
 
def run():
    with SessionLocal() as db:
        if db.scalar(select(Category).limit(1)):
            print("Đã có dữ liệu, bỏ qua.")
            return
        com = Category(name="Cơm")
        bun = Category(name="Bún phở")
        uong = Category(name="Đồ uống")
        com.items.append(MenuItem(name="Cơm gà xối mỡ", price=35000))
        bun.items.append(MenuItem(name="Bún cá Hải Phòng", price=30000))
        bun.items.append(MenuItem(name="Bánh đa cua", price=30000,
                                  available=False))
        uong.items.append(MenuItem(name="Trà chanh", price=10000))
        db.add_all([com, bun, uong])
        db.commit()
        print("Đã thêm 3 danh mục, 4 món.")
 
if __name__ == "__main__":
    run()
    