"""
=============================================================
  CAFE PRODUCT MANAGEMENT SYSTEM - Flask + SQLAlchemy + SQLite
  Senior Backend Developer Guide for Software Engineering Course
=============================================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ─── APP CONFIGURATION ────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cafe-secret-key-2024'

# SQLite (dễ test): đổi sang SQL Server bằng cách thay chuỗi kết nối bên dưới
# SQL Server: 'mssql+pyodbc://user:pass@server/dbname?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─── MODELS (Bước 1: Thiết kế CSDL) ─────────────────────────────────────────

class Category(db.Model):
    """Bảng danh mục sản phẩm"""
    __tablename__ = 'categories'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False, unique=True)
    # Quan hệ 1-nhiều: một danh mục có nhiều sản phẩm
    products   = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Bảng sản phẩm — đủ các trường theo yêu cầu bài toán"""
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    price       = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url   = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    # status: True = Còn hàng | False = Hết hàng
    status      = db.Column(db.Boolean, default=True, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def status_label(self):
        return "Còn hàng" if self.status else "Hết hàng"

    def __repr__(self):
        return f'<Product {self.name}>'


# ─── DATABASE INITIALIZATION + SEED DATA ─────────────────────────────────────

def seed_database():
    """Tạo dữ liệu mẫu nếu DB còn trống"""
    if Category.query.count() > 0:
        return  # Đã có dữ liệu rồi, không seed lại

    # Tạo danh mục
    categories = [
        Category(name="Cà Phê"),
        Category(name="Trà & Matcha"),
        Category(name="Sinh Tố"),
        Category(name="Bánh & Snack"),
    ]
    db.session.add_all(categories)
    db.session.flush()  # Lấy ID trước khi commit

    # Tạo sản phẩm mẫu
    products = [
        Product(name="Cà Phê Đen",       price=25000, category_id=1, status=True,
                description="Robusta nguyên chất, đậm vị, thơm nồng.",
                image_url="https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=400"),
        Product(name="Cà Phê Sữa",       price=30000, category_id=1, status=True,
                description="Pha trộn hoàn hảo giữa cà phê và sữa đặc.",
                image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"),
        Product(name="Cappuccino",        price=55000, category_id=1, status=True,
                description="Espresso Ý, milk foam mịn, bột quế nhẹ.",
                image_url="https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400"),
        Product(name="Cold Brew",         price=45000, category_id=1, status=False,
                description="Ủ lạnh 12 giờ, vị ngọt tự nhiên, không đắng.",
                image_url="https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=400"),
        Product(name="Trà Xanh Matcha",   price=50000, category_id=2, status=True,
                description="Matcha Nhật Bản nguyên chất, thêm sữa tươi.",
                image_url="https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=400"),
        Product(name="Hồng Trà Sữa",      price=40000, category_id=2, status=True,
                description="Trà hồng Đài Loan, sữa tươi và trân châu đen.",
                image_url="https://images.unsplash.com/photo-1558857563-b371033873b8?w=400"),
        Product(name="Sinh Tố Xoài",      price=45000, category_id=3, status=True,
                description="Xoài Cát Hòa Lộc tươi, béo ngậy, vitamin C cao.",
                image_url="https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400"),
        Product(name="Sinh Tố Dâu",       price=50000, category_id=3, status=True,
                description="Dâu tây Đà Lạt, sữa chua, mật ong.",
                image_url="https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400"),
        Product(name="Bánh Croissant",    price=35000, category_id=4, status=True,
                description="Bánh bơ Pháp, giòn lớp ngoài, mềm bên trong.",
                image_url="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400"),
        Product(name="Cheese Cake",       price=55000, category_id=4, status=False,
                description="Cheesecake New York style, mịn tan, không quá ngọt.",
                image_url="https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400"),
    ]
    db.session.add_all(products)
    db.session.commit()
    print("✅ Đã seed dữ liệu mẫu thành công!")


# ─── CLIENT ROUTES (Bước 2 - Phân hệ Khách Hàng) ───────────────────────────

@app.route('/')
def index():
    """
    Trang khách hàng: hiển thị sản phẩm dạng Card Grid
    Hỗ trợ lọc theo category_id và tìm kiếm theo tên
    """
    # Lấy query parameters từ URL
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category_id', type=int)

    # Bắt đầu query cơ bản
    query = Product.query

    # Áp dụng filter tìm kiếm (LIKE query - không phân biệt hoa/thường)
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    # Áp dụng filter danh mục
    if category_filter:
        query = query.filter(Product.category_id == category_filter)

    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()

    return render_template('index.html',
                           products=products,
                           categories=categories,
                           search_query=search_query,
                           active_category=category_filter)


# ─── ADMIN ROUTES (Bước 2 - Phân hệ Quản Trị - CRUD) ───────────────────────

@app.route('/admin')
def admin():
    """Admin: Hiển thị danh sách sản phẩm dạng bảng"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin.html', products=products, categories=categories)


@app.route('/admin/product/create', methods=['GET', 'POST'])
def create_product():
    """
    GET:  Hiển thị form thêm sản phẩm mới
    POST: Validate và lưu vào CSDL
    """
    categories = Category.query.all()

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        price_str   = request.form.get('price', '')
        description = request.form.get('description', '').strip()
        image_url   = request.form.get('image_url', '').strip()
        category_id = request.form.get('category_id', type=int)
        status      = request.form.get('status') == 'true'

        # ── BACKEND VALIDATION ──────────────────────────────────────────────
        errors = []
        if not name:
            errors.append("Tên sản phẩm không được để trống.")

        try:
            price = float(price_str)
            if price <= 0:
                errors.append("Giá sản phẩm phải lớn hơn 0.")
        except (ValueError, TypeError):
            price = 0
            errors.append("Giá sản phẩm không hợp lệ.")

        if not category_id:
            errors.append("Vui lòng chọn danh mục.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('product_form.html',
                                   categories=categories,
                                   form_data=request.form,
                                   action='create')

        # ── LƯU VÀO DATABASE ───────────────────────────────────────────────
        new_product = Product(
            name=name, price=price, description=description,
            image_url=image_url, category_id=category_id, status=status
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'✅ Đã thêm sản phẩm "{name}" thành công!', 'success')
        return redirect(url_for('admin'))

    return render_template('product_form.html',
                           categories=categories,
                           form_data={},
                           action='create')


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    """
    GET:  Tải dữ liệu sản phẩm cũ vào form
    POST: Validate và cập nhật vào CSDL
    """
    # Truy vấn hoặc trả về 404 nếu không tìm thấy
    product    = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        price_str   = request.form.get('price', '')
        description = request.form.get('description', '').strip()
        image_url   = request.form.get('image_url', '').strip()
        category_id = request.form.get('category_id', type=int)
        status      = request.form.get('status') == 'true'

        # ── BACKEND VALIDATION (tái sử dụng logic giống Create) ────────────
        errors = []
        if not name:
            errors.append("Tên sản phẩm không được để trống.")

        try:
            price = float(price_str)
            if price <= 0:
                errors.append("Giá sản phẩm phải lớn hơn 0.")
        except (ValueError, TypeError):
            price = 0
            errors.append("Giá sản phẩm không hợp lệ.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('product_form.html',
                                   categories=categories,
                                   form_data=request.form,
                                   product=product,
                                   action='edit')

        # ── CẬP NHẬT VÀO DATABASE ─────────────────────────────────────────
        product.name        = name
        product.price       = price
        product.description = description
        product.image_url   = image_url
        product.category_id = category_id
        product.status      = status
        db.session.commit()
        flash(f'✅ Đã cập nhật sản phẩm "{name}" thành công!', 'success')
        return redirect(url_for('admin'))

    return render_template('product_form.html',
                           categories=categories,
                           form_data={},
                           product=product,
                           action='edit')


@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """
    Xóa sản phẩm theo ID.
    Confirm được xử lý bằng JavaScript ở phía client trước khi submit.
    """
    product = Product.query.get_or_404(product_id)
    name    = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'🗑️ Đã xóa sản phẩm "{name}".', 'warning')
    return redirect(url_for('admin'))


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()      # Tạo bảng nếu chưa có
        seed_database()      # Insert dữ liệu mẫu
    app.run(debug=True, port=5000)