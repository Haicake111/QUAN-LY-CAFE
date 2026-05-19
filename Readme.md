# ☕ Café Product Management System
**Bài Tập Lớn — Môn Công Nghệ Phần Mềm**

## Cấu Trúc Dự Án
```
cafe_app/
│
├── app.py                  ← Entry point: Models + Routes (Controllers)
├── requirements.txt        ← Thư viện cần cài
│
└── templates/
    ├── base.html           ← Layout chung (Navbar, Footer, Flash messages)
    ├── index.html          ← Trang khách hàng (Card Grid + Search + Filter)
    ├── admin.html          ← Trang quản trị (Table + Nút CRUD)
    └── product_form.html   ← Form thêm / sửa sản phẩm
```

## Cài Đặt & Chạy

```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Chạy app (tự tạo DB + seed dữ liệu mẫu)
python app.py
```

Mở trình duyệt: **http://localhost:5000**

## Tính Năng

### Trang Khách Hàng (`/`)
- Hiển thị Card Grid tất cả sản phẩm
- Tìm kiếm theo tên (LIKE query)
- Lọc theo danh mục (category pills + dropdown)
- Badge trạng thái Còn hàng / Hết hàng

### Trang Quản Trị (`/admin`)
- Bảng thống kê nhanh (tổng, còn hàng, hết hàng)
- Table đầy đủ thông tin sản phẩm
- Nút Sửa → chuyển sang form edit
- Nút Xóa → `confirm()` JavaScript trước khi xóa

### Form Thêm / Sửa (`/admin/product/create`, `/admin/product/edit/<id>`)
- Validation cả Frontend (JS) và Backend (Python)
- Preview hình ảnh real-time khi nhập URL
- Radio button trạng thái Còn/Hết hàng

## Đổi Sang SQL Server

Trong `app.py`, thay dòng SQLALCHEMY_DATABASE_URI:

```python
# SQLite (mặc định - test nhanh)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'

# SQL Server (production)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://sa:YourPassword@localhost/CafeDB'
    '?driver=ODBC+Driver+17+for+SQL+Server'
)
```

Sau đó cài thêm: `pip install pyodbc`

## Validation Rules
| Trường | Rule |
|--------|------|
| `name` | Không được để trống (cả FE + BE) |
| `price` | Phải là số, > 0 (cả FE + BE) |
| `category_id` | Bắt buộc chọn (cả FE + BE) |