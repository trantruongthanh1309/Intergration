from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import config  # Import file config.py

app = Flask(__name__)

# Sử dụng thông tin kết nối từ config.py
app.config["SQLALCHEMY_BINDS"] = {
    "default": config.SQL_SERVER_CONN,  # Thêm dòng này để tránh lỗi
    "mysql": config.MYSQL_CONN
}

db = SQLAlchemy(app)

# Mô hình dữ liệu SQL Server
class HoSoNhanVienSQL(db.Model):
    __tablename__ = "HoSoNhanVien"
    __bind_key__ = "default"
    
    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    DiaChi = db.Column(db.String(255))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)

# Mô hình dữ liệu MySQL
class HoSoNhanVienMySQL(db.Model):
    __tablename__ = "HoSoNhanVien"
    __bind_key__ = "mysql"
    
    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)

class LuongNhanVien(db.Model):
    __tablename__ = "LuongNhanVien"
    __bind_key__ = "mysql"
    
    MaLuong = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaNV = db.Column(db.Integer, db.ForeignKey("HoSoNhanVien.MaNV"))
    ThangNam = db.Column(db.Date)
    LuongCoBan = db.Column(db.Float)
    PhuCap = db.Column(db.Float)
    Thuong = db.Column(db.Float)
    KhauTru = db.Column(db.Float)
    LuongThucNhan = db.Column(db.Float)

# Trang chủ (Dashboard)
@app.route("/")
def index():
    return render_template("index.html")


# Trang thêm nhân viên
@app.route("/them-nhan-vien", methods=["GET", "POST"])
def them_nhan_vien():
    if request.method == "POST":
        ho_ten = request.form["ho_ten"]
        ngay_sinh = request.form["ngay_sinh"]
        gioi_tinh = request.form["gioi_tinh"]
        dia_chi = request.form["dia_chi"]
        so_dien_thoai = request.form["so_dien_thoai"]
        email = request.form["email"]
        ngay_vao_lam = request.form["ngay_vao_lam"]

        # Thêm vào cơ sở dữ liệu SQL Server
        nhan_vien_sql = HoSoNhanVienSQL(
            HoTen=ho_ten,
            NgaySinh=ngay_sinh,
            GioiTinh=gioi_tinh,
            DiaChi=dia_chi,
            SoDienThoai=so_dien_thoai,
            Email=email,
            NgayVaoLam=ngay_vao_lam,
        )
        db.session.add(nhan_vien_sql)
        db.session.commit()

        # Thêm vào MySQL
        nhan_vien_mysql = HoSoNhanVienMySQL(
            MaNV=nhan_vien_sql.MaNV,
            HoTen=ho_ten,
            NgaySinh=ngay_sinh,
            GioiTinh=gioi_tinh,
            SoDienThoai=so_dien_thoai,
            Email=email,
            NgayVaoLam=ngay_vao_lam,
        )
        db.session.add(nhan_vien_mysql)
        db.session.commit()

        # Sau khi thêm xong, quay lại trang quản lý nhân sự
        return redirect(url_for("quan_li_nhan_su"))

    # Nếu là phương thức GET, render form thêm nhân viên mới
    return render_template("them_nhan_vien.html")


@app.route("/bao-cao-tai-chinh", methods=["GET"])
def bao_cao_tai_chinh():
    # Thực hiện các công việc cần thiết, ví dụ: lấy dữ liệu từ cơ sở dữ liệu
    # Các dữ liệu có thể là thống kê tài chính, báo cáo doanh thu, chi phí, v.v.
    return render_template("bao_cao_tai_chinh.html")

@app.route("/ho-so", methods=["GET", "POST"])
def ho_so():
    if request.method == "POST":
        # Xử lý việc cập nhật thông tin hồ sơ từ form POST
        # Ví dụ: Cập nhật thông tin người dùng từ request.form
        ho_ten = request.form['ho_ten']
        dia_chi = request.form['dia_chi']
        email = request.form['email']
        # Lưu thông tin vào cơ sở dữ liệu nếu cần
        return redirect(url_for("ho_so"))  # Quay lại trang hồ sơ sau khi cập nhật
    # Trả về trang hồ sơ với các thông tin người dùng (nếu có)
    return render_template("ho_so.html")

@app.route("/cai-dat", methods=["GET", "POST"])
def cai_dat():
    if request.method == "POST":
        # Xử lý các thay đổi cài đặt từ form POST
        # Ví dụ: Thay đổi mật khẩu, cài đặt thông báo, v.v.
        mat_khau_moi = request.form['mat_khau_moi']
        # Cập nhật cài đặt vào cơ sở dữ liệu nếu cần
        return redirect(url_for("cai_dat"))  # Quay lại trang cài đặt sau khi thay đổi
    # Trả về trang cài đặt với các lựa chọn và form
    return render_template("cai_dat.html")

# Trang cập nhật nhân viên
@app.route("/cap-nhat-nhan-vien/<int:ma_nv>", methods=["GET", "POST"])
def cap_nhat_nhan_vien(ma_nv):
    nhan_vien = HoSoNhanVienSQL.query.get(ma_nv)
    
    if not nhan_vien:
        return "Nhân viên không tồn tại!", 404

    if request.method == "POST":
        nhan_vien.HoTen = request.form["ho_ten"]
        nhan_vien.NgaySinh = request.form["ngay_sinh"]
        nhan_vien.GioiTinh = request.form["gioi_tinh"]
        nhan_vien.DiaChi = request.form["dia_chi"]
        nhan_vien.SoDienThoai = request.form["so_dien_thoai"]
        nhan_vien.Email = request.form["email"]
        nhan_vien.NgayVaoLam = request.form["ngay_vao_lam"]
        db.session.commit()

       # Sau khi thêm xong, quay lại trang quản lý nhân sự
        return redirect(url_for("quan_li_nhan_su"))

    # Nếu là phương thức GET, render form thêm nhân viên mới
    return render_template("them_nhan_vien.html")


# Xóa nhân viên
from flask import jsonify

@app.route("/xoa-nhan-vien/<int:ma_nv>", methods=["GET"])
def xoa_nhan_vien(ma_nv):
    nhan_vien = HoSoNhanVienSQL.query.get(ma_nv)
    if nhan_vien:
        db.session.delete(nhan_vien)
        db.session.commit()
      # Sau khi thêm xong, quay lại trang quản lý nhân sự
        return redirect(url_for("quan_li_nhan_su"))

    # Nếu là phương thức GET, render form thêm nhân viên mới
    return render_template("them_nhan_vien.html")

# Trang in danh sách nhân viên
# Trang quản lý nhân sự
@app.route("/quan-li-nhan-su")
def quan_li_nhan_su():
    nhan_viens = HoSoNhanVienSQL.query.all()  # Lấy tất cả nhân viên từ cơ sở dữ liệu
    return render_template("quan_li_nhan_su.html", nhan_viens=nhan_viens)
    
@app.route("/quan_li_tai_chinh")
def quan_li_tai_chinh():
    nhan_viens = HoSoNhanVienSQL.query.all()
    luong_nhan_vien = LuongNhanVien.query.all()
    
    data = []
    for nv in nhan_viens:
        luong = next((l for l in luong_nhan_vien if l.MaNV == nv.MaNV), None)
        if luong:
            data.append((nv, luong))
    return render_template("quan_li_tai_chinh.html", nhan_viens=data)

# Trang in bảng lương
# @app.route("/in-bang-luong")
# def in_bang_luong():
#     nhan_viens = HoSoNhanVienSQL.query.all()
#     luong_nhan_vien = LuongNhanVien.query.all()
    
#     data = []
#     for nv in nhan_viens:
#         luong = next((l for l in luong_nhan_vien if l.MaNV == nv.MaNV), None)
#         if luong:
#             data.append((nv, luong))
    
#     return render_template("in_bang_luong.html", nhan_viens=data)

if __name__ == "__main__":
    app.run(debug=True)
