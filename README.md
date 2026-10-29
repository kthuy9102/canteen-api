# Canteen API – Hệ thống thực đơn Căng tin trường

## 1. Mục tiêu

- Đi đúng quy trình: phân tích nghiệp vụ → thiết kế API → hiện thực → kiểm thử.
- Hiện thực 6 endpoint CRUD với FastAPI, tách lớp **router – schema – repository**.
- Áp dụng quy tắc nghiệp vụ và trả đúng mã trạng thái: `201`, `204`, `404`, `409`, `422`.
- Tổ chức Postman Collection theo thư mục, viết test script, kiểm thử hướng dữ liệu (CSV) và chạy tự động bằng **Newman**.

---

## 2. Công nghệ sử dụng

| Thành phần | Phiên bản / Ghi chú |
|---|---|
| Python | 3.10+ |
| FastAPI | `fastapi[standard]` |
| Uvicorn | Chạy server ASGI |
| Pydantic | Validate dữ liệu (v2) |
| **PostgreSQL** | **16-alpine (qua Docker Compose)** |
| **SQLAlchemy** | **2.0 (ORM)** |
| **Alembic** | **Migration** |
| **psycopg** | **`psycopg[binary]` driver** |
| **python-dotenv** | **Đọc biến môi trường từ `.env`** |
| **DBeaver Community** | **Xem bảng/dữ liệu, ERD (khuyến khích)** |
| Postman Desktop | Kiểm thử API thủ công |
| Node.js LTS + Newman | Chạy test tự động |
| Git | Quản lý phiên bản |

---

## 3. Cấu trúc dự án

```text
canteen-api/
├── app/
│   ├── __init__.py
|   ├── database.py          
│   ├── main.py              # Khởi tạo FastAPI app, include router
|   ├── models.py
│   ├── schemas.py           # Pydantic models (Create / Update / Out)
│   ├── repository.py        # Lớp lưu trữ (in-memory)
│   └── routers/
│       ├── __init__.py
|       ├── categories.py    # Quản lý danh mục 
|       ├── menu.py          # Endpoint CRUD + quy tắc nghiệp vụ
│       └── orders.py        # Để có thể đặt món
├── migrations
|   └── env.py
├── postman/
│   ├── Canteen-API.postman_collection.json
│   ├── Canteen-Local.postman_environment.json
│   └── negative.csv         # Dữ liệu kiểm thử hướng dữ liệu
├── docs/
│   ├── design.md            # Đặc tả tài nguyên & endpoint
│   ├── postman_runner.png   # Ảnh chụp Collection Runner
│   └── newman.png           # Ảnh chụp kết quả Newman
├── .env
├── .env.example
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Quy tắc nghiệp vụ(updated)

| Mã | Nội dung | Mã lỗi |
|---|---|---|
| **BR1** | Tên món là duy nhất (không phân biệt hoa thường) | `409 Conflict` |
| **BR2** | Giá `0 < price ≤ 200.000` và là bội số của `1.000` | `422` |
| **BR3** | Loại món thuộc: `com`, `bun_pho`, `do_uong`, `an_vat` | `422` |
| **BR4** | Món hết hàng giữ trong thực đơn, chỉ chuyển `available = false` | – |
| **BR5** | Tên danh mục là duy nhất; trùng → 409 | `409` |
| **BR6** | `category_id` của món phải tồn tại; sai → 422 | `422` |
| **BR7** | Không đặt món đã hết (`available = false`) → 409; mỗi món chỉ xuất hiện **một lần** trong một đơn | `409` / `422` |
| **BR8** | `unit_price` lưu giá tại thời điểm đặt; món đã có trong đơn hàng thì **không được xóa** (→ 409), chỉ đánh dấu hết | `409` |

---

## 5. Thiết kế cơ sở dữ liệu (Lab 5)

### Bảng 1. Thiết kế CSDL (theo ERD Chương 5)

| Bảng | Cột chính | Quan hệ |
|---|---|---|
| `categories` | `id` (PK), `name` (UNIQUE) | 1 danh mục – N món |
| `menu_items` | `id` (PK), `name` (UNIQUE), `price` (CHECK > 0), `available`, `category_id` (FK), `updated_at`, `image_url` | N món thuộc 1 danh mục |
| `orders` | `id` (PK), `student_code`, `created_at` | 1 đơn – N dòng chi tiết |
| `order_items` | `order_id` (PK, FK), `item_id` (PK, FK), `quantity`, `unit_price` | Bảng trung gian N:N giữa `orders` và `menu_items` |

### Đặc tả tài nguyên `MenuItem` (cập nhật)

| Trường | Kiểu | Ràng buộc | Ví dụ |
|---|---|---|---|
| `id` | int | Hệ thống tự sinh | `1` |
| `name` | str | 2–100 ký tự, duy nhất (BR1) | `Bún cá Hải Phòng` |
| `category_id` | int | FK → `categories.id`, phải tồn tại (BR6) | `2` |
| `price` | int | `0 < price ≤ 200000`, bội số `1000` (BR2) | `30000` |
| `available` | bool | Mặc định `true` (BR4) | `true` |
| `image_url` | str \| null | Ảnh minh họa (≤ 255 ký tự) | `null` |
| `updated_at` | datetime | Hệ thống tự cập nhật, chỉ đọc | `2026-10-20T11:30:00` |

---


## 6. Danh sách endpoint(updated)

### 6.1. Menu Items 

| Phương thức | URI | Thành công | Lỗi |
|---|---|---|---|
| `GET` | `/menu-items` | `200` | `422` |
| `GET` | `/menu-items/{id}` | `200` | `404`, `422` |
| `POST` | `/menu-items` | `201` + `Location` | `409`, `422` |
| `PUT` | `/menu-items/{id}` | `200` | `404`, `409`, `422` |
| `PATCH` | `/menu-items/{id}` | `200` | `404`, `409`, `422` |
| `DELETE` | `/menu-items/{id}` | `204` | `404`, `409` (BR8) |

**Query params của `GET /menu-items` (Lab 5):** `category_id`, `available`, `max_price`, `sort` (`id | price | name`), `order` (`asc | desc`).

Ví dụ: `/menu-items?category_id=2&sort=price&order=desc`

> **Thay đổi so với Lab 4:** tham số `category` (chuỗi enum) được thay bằng `category_id` (int).

### 6.2. Categories (mới)

| Phương thức | URI | Thành công | Lỗi |
|---|---|---|---|
| `GET` | `/categories` | `200` | – |
| `POST` | `/categories` | `201` | `409` (BR5), `422` |

### 6.3. Orders (mới)

| Phương thức | URI | Thành công | Lỗi |
|---|---|---|---|
| `POST` | `/orders` | `201` kèm tổng tiền | `409` (BR7), `422` |
| `GET` | `/orders/{id}` | `200` | `404` |

### 6.4. Bảng 2. Tổng hợp thay đổi của API

| Phương thức | Endpoint | Thay đổi |
|---|---|---|
| GET, POST | `/categories` | Mới: xem và thêm danh mục |
| GET | `/menu-items` | Lọc theo `category_id` thay cho `category` dạng chuỗi |
| POST, PUT, PATCH | `/menu-items…` | Body dùng `category_id`; kiểm tra danh mục tồn tại |
| DELETE | `/menu-items/{id}` | Trả `409` nếu món đã có trong đơn hàng (BR8) |
| POST | `/orders` | Mới: đặt món, trả `201` kèm tổng tiền |
| GET | `/orders/{id}` | Mới: xem chi tiết đơn |

---

## 7. Hướng dẫn cài đặt và chạy

### 7.1. Yêu cầu hệ thống

- Ubuntu / WSL2 hoặc Windows (dùng Git Bash)
- Python 3.10+
- **Docker Desktop (Windows) hoặc Docker Engine (Ubuntu) – mở sẵn trước khi làm**
- Node.js LTS (cho Newman)
- Postman Desktop
- **DBeaver Community (khuyến khích, để xem bảng và ERD)**

### 7.2. Cài đặt

```bash
git clone <repo-url> canteen-api
cd canteen-api

python3 -m venv .venv
source .venv/bin/activate          # Ubuntu/WSL2
# source .venv/Scripts/activate    # Git Bash trên Windows

pip install "fastapi[standard]"
pip freeze > requirements.txt
```

  Lưu ý Windows (Git Bash): dùng python thay cho python3, kích hoạt bằng source .venv/Scripts/activate. Mỗi lần mở terminal mới phải kích hoạt lại — dấu nhắc phải có (.venv).

### 7.3. Chạy PostgreSQL bằng Docker Compose

Khởi động và kiểm tra:

```bash
docker compose up -d
docker compose ps          # cột STATUS phải là running
docker compose exec db psql -U canteen -d canteen -c "SELECT version();"
```
### 7.4. Tạo bảng bằng Alembic

```bash
alembic init migrations
```

Mở `migrations/env.py`, thêm ngay dưới dòng `config = context.config`:

```python
from app.database import Base, DATABASE_URL
from app import models  # noqa: F401  nạp model để Alembic nhìn thấy

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata
```

Sinh và áp dụng migration:

```bash
alembic revision --autogenerate -m "create canteen tables"
alembic upgrade head
```

**Kiểm tra:** tệp sinh ra trong `migrations/versions/` phải có 4 lệnh `op.create_table` cùng các khóa ngoại. Nếu `upgrade()` chỉ có `pass` → `env.py` chưa nạp model.

Kiểm tra trong psql — phải thấy 5 bảng: `alembic_version`, `categories`, `menu_items`, `orders`, `order_items`:

```bash
docker compose exec db psql -U canteen -d canteen
canteen=# \dt
canteen=# \d menu_items
canteen=# SELECT * FROM alembic_version;
canteen=# \q
```

### 7.5. Thực hành nâng/hoàn tác migration (minh chứng có ≥ 2 phiên bản)

Thêm cột ảnh vào `MenuItem`:

```python
image_url: Mapped[str | None] = mapped_column(String(255))
```

```bash
alembic revision --autogenerate -m "add image_url to menu_items"
alembic upgrade head      # \d menu_items: có cột image_url
alembic downgrade -1      # cột image_url bị xóa
alembic upgrade head      # áp dụng lại
alembic history           # xem chuỗi phiên bản
```
### 7.6. Nạp dữ liệu mẫu (seed)

```bash
python -m app.seed
```

Kỳ vọng: in ra `"Đã thêm 3 danh mục, 4 món."` (nếu CSDL đã có dữ liệu → `"Đã có dữ liệu, bỏ qua."`). Nhờ `echo=True`, terminal in ra các câu `INSERT`.

Dữ liệu mẫu:

| Tên | Danh mục | Giá | Available |
|---|---|---|---|
| Cơm gà xối mỡ | Cơm | 35.000 | ✅ |
| Bún cá Hải Phòng | Bún phở | 30.000 | ✅ |
| Bánh đa cua | Bún phở | 30.000 | ❌ |
| Trà chanh | Đồ uống | 10.000 | ✅ |

### 7.7. Chạy server

```bash
python -m uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs — phải thấy **4 nhóm**: System, Categories, Menu, Orders.
- Health check: http://127.0.0.1:8000/health

Nếu báo `uvicorn: command not found`, dùng `python -m uvicorn ...`.

<img width="1469" height="932" alt="Swagger UI" src="https://github.com/user-attachments/assets/85719b98-39e5-42df-b147-a6ce5f8999ff" />

---

## 8. Kiểm thử bằng Postman
### 8.1. Cấu trúc Collection (cập nhật Lab 5)

```text
   Canteen API
├── 01-Read         TC01–TC07
├── 02-Create       TC08
├── 03-Update       TC09–TC11
├── 04-Delete       TC12–TC13
├── 05-Data-driven  DD (chạy riêng với negative.csv)
└── 06-Orders and categories      TC14–TC17  (mới)

```

### 8.2. Environment
Tạo environment Canteen-Local với biến baseUrl = http://localhost:8000.

### 8.3. Danh sách test case

| Mã | Phương thức | URL | Mong đợi |
|---|---|---|---|
| TC01 | GET | `/health` | 200 |
| TC02 | GET | `/menu-items` | 200, đủ 4 món |
| TC03 | GET | `/menu-items?category_id=2&sort=price&order=desc` | 200, đúng danh mục, giá giảm dần |
| TC04 | GET | `/menu-items?available=false` | 200, 1 món |
| TC05 | GET | `/menu-items/1` | 200 |
| TC06 | GET | `/menu-items/999` | 404 |
| TC07 | GET | `/menu-items/0` | 422 |
| TC08 | POST | `/menu-items` | 201 + Location |
| TC09 | PUT | `/menu-items/{{itemId}}` | 200 |
| TC10 | PATCH | `/menu-items/{{itemId}}` | 200 |
| TC11 | PATCH | `/menu-items/{{itemId}}` | 409 |
| TC12 | DELETE | `/menu-items/{{itemId}}` | 204 |
| TC13 | GET | `/menu-items/{{itemId}}` | 404 |

**Nội dung cần sửa do API đổi `category` → `category_id`:**

| Mã | Nội dung cần sửa |
|---|---|
| TC03 | URL: `{{baseUrl}}/menu-items?category_id=2&sort=price&order=desc`; test kiểm tra `i.category_id === 2`. |
| TC08 | Body: `{"name": "{{itemName}}", "category_id": 3, "price": 15000}` |
| TC09 | Body: `{"name": "{{itemName}} sửa", "category_id": 3, "price": 20000, "available": true}` |
| CSV | Đổi cột `category` thành `category_id`; dòng `sai_loai` dùng `category_id = 99` (mong đợi 422). Body: `"category_id": {{category_id}}` |

### 8.4. Test case Lab 5 (mới)

Dữ liệu mẫu: `id 2` = Bún cá 30.000đ, `id 3` = Bánh đa cua đã hết, `id 4` = Trà chanh 10.000đ.

| Mã | Request | Body / mục đích | Mong đợi |
|---|---|---|---|
| TC14 | POST `/orders` | 2 suất Bún cá + 1 Trà chanh; lưu `orderId` | 201, `total = 70000` |
| TC15 | GET `/orders/{{orderId}}` | Xem lại đơn vừa đặt | 200, 2 dòng |
| TC16 | POST `/orders` | Đặt Bánh đa cua (đã hết) | 409 (BR7) |
| TC17 | POST `/categories` | `{"name": "Cơm"}` | 409 (BR5) |
| TC18 | DELETE `/menu-items/2` | Bún cá đã có trong đơn | 409 (BR8) |
### 8.5. Chạy Collection Runner
Khởi động lại server. Vào **Canteen API → ⋯ → Run collection**. Bỏ chọn `05-Data-driven`, giữ thứ tự TC01 → TC18. Nhấn **Run** — kỳ vọng **100% Passed, 0 Failed**.

Ảnh minh chứng: `docs/postman_runner.png`.
### 8.5. Kiểm thử hướng dữ liệu (Data-driven)
File postman/negative.csv (UTF-8):
```csv
case,name,category_id,price,expected
thieu_ten,,1,30000,422
gia_am,Phở bò,2,-5000,422
gia_le,Phở bò,2,30500,422
gia_qua_cao,Phở bò,2,250000,422
sai_loai,Phở bò,99,30000,422
trung_ten,Cơm gà xối mỡ,1,35000,409
```

Chạy: thư mục 05-Data-driven → ⋯ → Run folder → Data: chọn negative.csv → Run — 6 iterations, tất cả Passed.

### 8.6. Đưa CSDL về trạng thái ban đầu trước khi chạy lại Runner

Khác với Lab 4, dữ liệu giờ **lưu bền vững** nên số lượng món thay đổi theo các lần chạy. Dùng 3 lệnh:

```bash
alembic downgrade base    # xóa toàn bộ bảng
alembic upgrade head      # tạo lại bảng
python -m app.seed        # nạp lại dữ liệu mẫu
```

---

## 9. Chạy tự động bằng Newman
### 9.1. Cài Node.js
```bash
Ubuntu: sudo apt install -y nodejs npm
```

Windows: tải bản LTS (.msi) tại nodejs.org

Kiểm tra:
```bash
node -v
npx -v
```

### 9.2. Export từ Postman
Collection: Canteen API → ⋯ → Export → Collection v2.1 → postman/Canteen-API.postman_collection.json

Environment: Canteen-Local → ⋯ → Export → postman/Canteen-Local.postman_environment.json

### 9.3. Chạy test
```bash
# Test chức năng (TC01–TC18)
npx newman run postman/Canteen-API.postman_collection.json \
    -e postman/Canteen-Local.postman_environment.json \
    --folder 01-Read --folder 02-Create \
    --folder 03-Update --folder 04-Delete \
    --folder 06-Orders --folder Categories

# Test hướng dữ liệu
npx newman run postman/Canteen-API.postman_collection.json \
    -e postman/Canteen-Local.postman_environment.json \
    --folder 05-Data-driven -d postman/negative.csv
```

Kỳ vọng: bảng tổng kết có cột `failed = 0`. Ảnh minh chứng: `docs/newman.png`.

---
## 10. Minh chứng lưu bền vững và truy vấn SQL (Lab 5)

### 10.1. Chứng minh dữ liệu được lưu bền vững

1. Thêm món **"Cơm rang dưa bò"** bằng Postman.
2. Dừng uvicorn (`Ctrl + C`), chạy `docker compose restart`, rồi chạy lại uvicorn.
3. Gọi `GET /menu-items`: món vừa thêm **vẫn còn**.

Chụp màn hình lưu thành `docs/persist.png`.

> **Lưu ý:** `docker compose down` vẫn giữ dữ liệu, nhưng `docker compose down -v` sẽ xóa volume và **mất toàn bộ dữ liệu**.

### 10.2. Truy vấn SQL đơn hàng

Trong psql (hoặc SQL Editor của DBeaver):

```sql
SELECT o.id, o.student_code, m.name, oi.quantity, oi.unit_price,
       oi.quantity * oi.unit_price AS thanh_tien
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN menu_items m ON m.id = oi.item_id
ORDER BY o.id;
```

Chụp kết quả lưu thành `docs/sql_orders.png`.

### 10.3. Xem ERD bằng DBeaver

**Database → New Database Connection → PostgreSQL** → Host `localhost`, Port `5432`, Database `canteen`, Username `canteen`, Password `secret` → **Test Connection** → **Finish**. Chọn schema `public` → chuột phải → **View Diagram** để xem ERD sinh tự động; chụp lại lưu thành `docs/erd.png`.

---

## 11. Lỗi thường gặp

### 11.1. Lab 4

| Hiện tượng | Cách khắc phục |
|---|---|
| `{{baseUrl}}` màu đỏ, Could not send request | Chưa chọn environment `Canteen-Local` hoặc server chưa chạy |
| Postman Web không gọi được localhost | Chuyển sang Postman Desktop (hoặc cài Postman Agent) |
| TC02/TC04 sai số lượng món | Dữ liệu còn từ lần chạy trước → khởi động lại server |
| TC09–TC13 trả 404/405 | Biến `itemId` trống → chạy TC08 trước |
| POST luôn trả 422 | Body chưa chọn `raw + JSON` hoặc JSON sai cú pháp |
| CSV lỗi tiếng Việt | Lưu file với encoding UTF-8 |
| `npx: command not found` | Chưa cài Node.js → cài LTS rồi mở lại terminal |
| `Connection refused`, cổng 5432 | Docker Desktop chưa mở hoặc container chưa chạy: `docker compose up -d`, kiểm tra `docker compose ps`. |
| `port is already allocated` | Máy đã có PostgreSQL khác dùng cổng 5432: đổi `ports` thành `"5433:5432"` và sửa cổng trong `DATABASE_URL`. |
| `password authentication failed` | Sai user/mật khẩu, hoặc volume cũ được tạo với mật khẩu khác: `docker compose down -v` rồi `up` lại (mất dữ liệu cũ). |
| `KeyError: 'DATABASE_URL'` | Thiếu tệp `.env` hoặc chạy lệnh không ở thư mục gốc dự án. |
| Migration sinh ra chỉ có `pass` | `env.py` chưa `import app.models` hoặc vẫn để `target_metadata = None`. |
| `the input device is not a TTY` (Git Bash) | Thêm `winpty` trước lệnh `docker compose exec`. |
| `ResponseValidationError` khi trả đối tượng ORM | Schema đầu ra thiếu `model_config = ConfigDict(from_attributes=True)`. |
| Lỗi sau một lần `IntegrityError`, mọi request đều hỏng | Thiếu `db.rollback()` trong khối `except`. |

---

## 13. Câu hỏi củng cố

**1. Vì sao "đánh dấu món đã hết" nên dùng `PATCH` thay vì `PUT`? Nếu dùng `PUT`, client phải gửi những gì?**
- **Dùng `PATCH`:** Vì `PATCH` dùng để cập nhật một phần tài nguyên. Khi nhân viên chỉ muốn đổi trạng thái, client chỉ cần gửi đúng 1 trường: `{"available": false}`. Điều này giúp tiết kiệm băng thông và tránh rủi ro vô tình ghi đè dữ liệu cũ.
- **Nếu dùng `PUT`:** `PUT` dùng để thay thế toàn bộ tài nguyên. Do đó, client sẽ phải gửi lại **toàn bộ** thông tin của món ăn (bao gồm `name`, `category`, `price`, và `available: false`). Nếu chỉ gửi mỗi `available`, các trường còn lại sẽ bị lỗi hoặc bị ghi đè thành giá trị mặc định.

**2. Gửi `DELETE /menu-items/5` hai lần liên tiếp nhận được mã nào ở mỗi lần? Điều đó có mâu thuẫn với tính idempotent không?**
- **Lần 1:** Trả về `204 No Content` (Xóa thành công).
- **Lần 2:** Trả về `404 Not Found` (Không tìm thấy món để xóa).
- **Không mâu thuẫn với tính idempotent:** Tính idempotent trong HTTP nghĩa là dù gọi request 1 lần hay nhiều lần, **trạng thái của server (dữ liệu) phải giống hệt nhau**. Ở đây, dù gọi lần 1 hay lần 2 thì kết quả cuối cùng là món id=5 đều đã bị xóa khỏi hệ thống. Việc mã trạng thái khác nhau giữa các lần gọi không làm mất tính idempotent của phương thức `DELETE`.

**3. Tại sao trùng tên món trả `409` mà không phải `400` hay `422`?**
- `400 Bad Request`: Dành cho lỗi cú pháp chung khiến server không hiểu request.
- `422 Unprocessable Entity`: Dành cho lỗi vi phạm validation dữ liệu đầu vào (ví dụ: giá âm, sai định dạng).
- `409 Conflict`: Dành cho trường hợp request hợp lệ về mặt cú pháp và định dạng, nhưng **xung đột với trạng thái hiện tại của tài nguyên trên server**. Việc tên món đã tồn tại (vi phạm quy tắc BR1) là một xung đột về mặt nghiệp vụ, nên `409` là mã chuẩn xác nhất.

**4. Khi chuyển sang cơ sở dữ liệu ở Chương 5, những tệp nào cần sửa và vì sao `routers/menu.py` gần như giữ nguyên?**
- **Các tệp cần sửa:** Chủ yếu là `repository.py` (viết lại các hàm để kết nối với Database như SQLAlchemy/MySQL thay vì List/Dict) và `requirements.txt` (thêm thư viện DB).
- **Vì sao `routers/menu.py` giữ nguyên:** Nhờ kiến trúc **tách lớp (phân lớp)**. Lớp Router chỉ giao tiếp với lớp Repository qua các hàm (`repo.get()`, `repo.add()`, v.v.). Miễn là lớp Repository vẫn giữ nguyên tên hàm và kiểu dữ liệu trả về, lớp Router không cần quan tâm bên dưới dữ liệu được lưu ở RAM hay ở Database thực tế.

---

## 14. Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [Postman Learning Center](https://learning.postman.com/)
- [Newman Documentation](https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/)
