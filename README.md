# Canteen API – Hệ thống thực đơn Căng tin trường

API quản lý thực đơn căng tin, xây dựng bằng **FastAPI**, phục vụ hai giao diện: sinh viên xem thực đơn và nhân viên cập nhật món.

- **Học phần:** Lập trình mã nguồn mở (POS02024)
- **Trường:** Đại học Quản lý và Công nghệ Hải Phòng – Khoa CNTT
- **Chuẩn đầu ra:** PLO9a
- **Hình thức:** Bài thực hành cá nhân

---

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
| Postman Desktop | Kiểm thử API thủ công |
| Node.js LTS + Newman | Chạy test tự động |
| Git | Quản lý phiên bản |

---

## 3. Cấu trúc dự án

```text
canteen-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Khởi tạo FastAPI app, include router
│   ├── schemas.py           # Pydantic models (Create / Update / Out)
│   ├── repository.py        # Lớp lưu trữ (in-memory)
│   └── routers/
│       ├── __init__.py
│       └── menu.py          # Endpoint CRUD + quy tắc nghiệp vụ
├── postman/
│   ├── Canteen-API.postman_collection.json
│   ├── Canteen-Local.postman_environment.json
│   └── negative.csv         # Dữ liệu kiểm thử hướng dữ liệu
├── docs/
│   ├── design.md            # Đặc tả tài nguyên & endpoint
│   ├── postman_runner.png   # Ảnh chụp Collection Runner
│   └── newman.png           # Ảnh chụp kết quả Newman
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Quy tắc nghiệp vụ

| Mã | Nội dung | Mã lỗi |
|---|---|---|
| **BR1** | Tên món là duy nhất (không phân biệt hoa thường) | `409 Conflict` |
| **BR2** | Giá `0 < price ≤ 200.000` và là bội số của `1.000` | `422` |
| **BR3** | Loại món thuộc: `com`, `bun_pho`, `do_uong`, `an_vat` | `422` |
| **BR4** | Món hết hàng giữ trong thực đơn, chỉ chuyển `available = false` | – |

---

## 5. Đặc tả tài nguyên `MenuItem`

| Trường | Kiểu | Ràng buộc | Ví dụ |
|---|---|---|---|
| `id` | int | Hệ thống tự sinh | `1` |
| `name` | str | 2–100 ký tự, duy nhất (BR1) | `Bún cá Hải Phòng` |
| `category` | enum | `com \| bun_pho \| do_uong \| an_vat` (BR3) | `bun_pho` |
| `price` | int | `0 < price ≤ 200000`, bội số `1000` (BR2) | `30000` |
| `available` | bool | Mặc định `true` (BR4) | `true` |
| `updated_at` | datetime | Hệ thống tự cập nhật, chỉ đọc | `2026-10-20T11:30:00` |

---

## 6. Danh sách endpoint

| Phương thức | URI | User story | Thành công | Lỗi |
|---|---|---|---|---|
| `GET` | `/menu-items` | US1 | `200` | `422` |
| `GET` | `/menu-items/{id}` | US2 | `200` | `404`, `422` |
| `POST` | `/menu-items` | US3 | `201` + `Location` | `409`, `422` |
| `PUT` | `/menu-items/{id}` | US4 (toàn bộ) | `200` | `404`, `409`, `422` |
| `PATCH` | `/menu-items/{id}` | US4 (một phần) | `200` | `404`, `409`, `422` |
| `DELETE` | `/menu-items/{id}` | US5 | `204` | `404` |

**Query params của `GET /menu-items`:** `category`, `available`, `max_price`, `sort` (`id | price | name`), `order` (`asc | desc`).

Ví dụ: `/menu-items?category=do_uong&available=true&sort=price&order=desc`

---

## 7. Hướng dẫn cài đặt và chạy

### 7.1. Yêu cầu hệ thống

- Ubuntu / WSL2 hoặc Windows (dùng Git Bash)
- Python 3.10+
- Node.js LTS (cho Newman)
- Postman Desktop

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

### 7.3. Chạy server

```bash
python -m uvicorn app.main:app --reload
```
Swagger UI: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

Nếu báo uvicorn: command not found, dùng python -m uvicorn ....

### 7.4. Dữ liệu mẫu (seed)

Khi khởi động, repository nạp sẵn 4 món:

| Tên | Loại | Giá | Available |
|---|---|---|---|
| Cơm gà xối mỡ | `com` | 35.000 | ✅ |
| Bún cá Hải Phòng | `bun_pho` | 30.000 | ✅ |
| Bánh đa cua | `bun_pho` | 30.000 | ❌ |
| Trà chanh | `do_uong` | 10.000 | ✅ |
## 8. Kiểm thử bằng Postman
### 8.1. Cấu trúc Collection
```text
   Canteen API
├── 01-Read         TC01–TC07
├── 02-Create       TC08
├── 03-Update       TC09–TC11
├── 04-Delete       TC12–TC13
└── 05-Data-driven  DD (chạy riêng với negative.csv)
```

### 8.2. Environment
Tạo environment Canteen-Local với biến baseUrl = http://localhost:8000.

### 8.3. Danh sách test case

| Mã | Phương thức | URL | Mong đợi |
|---|---|---|---|
| TC01 | GET | `/health` | 200 |
| TC02 | GET | `/menu-items` | 200, đủ 4 món |
| TC03 | GET | `/menu-items?category=bun_pho&sort=price&order=desc` | 200, đúng loại, giá giảm dần |
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
### 8.4. Chạy Collection Runner
Khởi động lại server để dữ liệu về 4 món ban đầu.

Vào Canteen API → ⋯ → Run collection.

Bỏ chọn 05-Data-driven, giữ thứ tự TC01 → TC13.

Nhấn Run — kỳ vọng 100% Passed, 0 Failed.

Ảnh minh chứng: docs/postman_runner.png.

### 8.5. Kiểm thử hướng dữ liệu (Data-driven)
File postman/negative.csv (UTF-8):
```csv
case,name,category,price,expected
thieu_ten,,com,30000,422
gia_am,Phở bò,bun_pho,-5000,422
gia_le,Phở bò,bun_pho,30500,422
gia_qua_cao,Phở bò,bun_pho,250000,422
sai_loai,Phở bò,lau,30000,422
trung_ten,Cơm gà xối mỡ,com,35000,409
```

Chạy: thư mục 05-Data-driven → ⋯ → Run folder → Data: chọn negative.csv → Run — 6 iterations, tất cả Passed.

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
# Test chức năng (TC01–TC13)
```bash
npx newman run postman/Canteen-API.postman_collection.json \
    -e postman/Canteen-Local.postman_environment.json \
    --folder 01-Read --folder 02-Create \
    --folder 03-Update --folder 04-Delete
```

# Test hướng dữ liệu
```bash
npx newman run postman/Canteen-API.postman_collection.json \
    -e postman/Canteen-Local.postman_environment.json \
    --folder 05-Data-driven -d postman/negative.csv
```

Kỳ vọng: bảng tổng kết có cột failed = 0. Ảnh minh chứng: docs/newman.png.

## 10. Lỗi thường gặp

| Hiện tượng | Cách khắc phục |
|---|---|
| `{{baseUrl}}` màu đỏ, Could not send request | Chưa chọn environment `Canteen-Local` hoặc server chưa chạy |
| Postman Web không gọi được localhost | Chuyển sang Postman Desktop (hoặc cài Postman Agent) |
| TC02/TC04 sai số lượng món | Dữ liệu còn từ lần chạy trước → khởi động lại server |
| TC09–TC13 trả 404/405 | Biến `itemId` trống → chạy TC08 trước |
| POST luôn trả 422 | Body chưa chọn `raw + JSON` hoặc JSON sai cú pháp |
| CSV lỗi tiếng Việt | Lưu file với encoding UTF-8 |
| `npx: command not found` | Chưa cài Node.js → cài LTS rồi mở lại terminal |

---

## 11. Sản phẩm nộp

- Link **Pull Request** nhánh `feature/menu-crud` → `main`.
- Kho mã nguồn gồm:
  - Mã nguồn (`app/`)
  - `requirements.txt`
  - `docs/design.md`
  - `postman/` (collection, environment, `negative.csv`)
  - `README.md` (file này) kèm ảnh Swagger, Runner, Newman

---

## 12. Tiêu chí đánh giá

| TT | Tiêu chí | Điểm |
|---|---|---|
| 1 | Phần A: `design.md` có đặc tả tài nguyên, bảng endpoint, mã lỗi khớp BR | 1,5 |
| 2 | Schema đúng BR2, BR3; tách Create/Update/Out; phân lớp repository | 1,5 |
| 3 | GET: lọc, sắp xếp đúng; 404 và 422 đúng | 1,5 |
| 4 | POST (201 + Location, 409), PUT, PATCH, DELETE (204) đúng đặc tả | 1,5 |
| 5 | Postman: đủ 5 thư mục, 13 test case có script, Runner đạt 100% | 1,5 |
| 6 | Data-driven bằng CSV đủ 6 trường hợp; chạy được bằng Newman | 1,5 |
| 7 | Git: commit chuẩn, PR có mô tả; README kèm ảnh minh chứng | 1,0 |
| | **Tổng cộng** | **10** |

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
