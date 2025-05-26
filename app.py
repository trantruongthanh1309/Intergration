from flask import (
    Flask, render_template, request, redirect, url_for, jsonify, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta, datetime
import config
from flask_mail import Mail, Message
import random
import string
import time
import os
from flask import request, session, flash, redirect, url_for, render_template
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'x3$9#1yPqT!vN8*7zLd@fG2kWmS'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'truongga471@gmail.com'
app.config['MAIL_PASSWORD'] = 'eguwsubamvrferrz' 

mail = Mail(app)
ma_xac_thuc = None
thoi_gian_gui = None

# Cấu hình kết nối SQL Server và MySQL
app.config["SQLALCHEMY_BINDS"] = {
    "default": config.SQL_SERVER_CONN,
    "mysql": config.MYSQL_CONN
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------- MODEL ------------------

class DepartmentMySQL(db.Model):
    __tablename__ = "departments"
    __bind_key__ = "mysql"

    DepartmentID = db.Column(db.Integer, primary_key=True)
    DepartmentName = db.Column(db.String(100))


class DepartmentSQL(db.Model):
    __tablename__ = "departments"
    __bind_key__ = "default"

    DepartmentID = db.Column(db.Integer, primary_key=True)
    DepartmentName = db.Column(db.String(100))


class PositionMySQL(db.Model):
    __tablename__ = "positions"
    __bind_key__ = "mysql"

    PositionID = db.Column(db.Integer, primary_key=True)
    PositionName = db.Column(db.String(100))


class PositionSQL(db.Model):
    __tablename__ = "positions"
    __bind_key__ = "default"

    PositionID = db.Column(db.Integer, primary_key=True)
    PositionName = db.Column(db.String(100))


class EmployeeSQL(db.Model):
    __tablename__ = "employees"
    __bind_key__ = "default"

    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer, db.ForeignKey("departments.DepartmentID"))
    PositionID = db.Column(db.Integer, db.ForeignKey("positions.PositionID"))
    Status = db.Column(db.String(50))
    Email = db.Column(db.String(255))
    BirthDate = db.Column(db.Date)
    Gender = db.Column(db.String(10))
    JoinDate = db.Column(db.Date)

    department = db.relationship("DepartmentSQL", backref="employees")
    position = db.relationship("PositionSQL", backref="employees")
    attendances = db.relationship('AttendanceSQL', backref='employee', cascade='all, delete-orphan')

class EmployeeMySQL(db.Model):
    __bind_key__ = 'mysql'
    __tablename__ = "employees"

    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer)
    PositionID = db.Column(db.Integer)
    Status = db.Column(db.String(50))
    Email = db.Column(db.String(255))
    BirthDate = db.Column(db.Date)
    Gender = db.Column(db.String(10))
    JoinDate = db.Column(db.Date)

    department = db.relationship(
        "DepartmentMySQL",
        primaryjoin="foreign(EmployeeMySQL.DepartmentID)==DepartmentMySQL.DepartmentID",
        lazy="joined"
    )
    position = db.relationship(
        "PositionMySQL",
        primaryjoin="foreign(EmployeeMySQL.PositionID)==PositionMySQL.PositionID",
        lazy="joined"
    )
    attendances = db.relationship(
        "AttendanceMySQL",
        primaryjoin="EmployeeMySQL.EmployeeID==AttendanceMySQL.EmployeeID",
        cascade="all, delete-orphan",
        lazy="joined"
    )


class AttendanceMySQL(db.Model):
    __tablename__ = "attendance"
    __bind_key__ = "mysql"

    AttendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey("employees.EmployeeID", ondelete='CASCADE'))  # CHỈ KHAI BÁO 1 LẦN
    
    WorkDays = db.Column(db.Integer, nullable=False)
    AbsentDays = db.Column(db.Integer, default=0)
    LeaveDays = db.Column(db.Integer, default=0)
    AttendanceMonth = db.Column(db.Date, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())


class AttendanceSQL(db.Model):
    __tablename__ = "attendance"
    __bind_key__ = "default"

    AttendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey("employees.EmployeeID"))
    WorkDays = db.Column(db.Integer, nullable=False)
    AbsentDays = db.Column(db.Integer, default=0)
    LeaveDays = db.Column(db.Integer, default=0)
    AttendanceMonth = db.Column(db.Date, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())
    EmployeeID = db.Column(db.Integer, db.ForeignKey("employees.EmployeeID", ondelete='CASCADE'))

class SalaryMySQL(db.Model):
    __tablename__ = "salaries"
    __bind_key__ = "mysql"

    SalaryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer)
    SalaryMonth = db.Column(db.Date, nullable=False)
    BaseSalary = db.Column(db.Float, nullable=False)
    Bonus = db.Column(db.Float, default=0.0)
    Deductions = db.Column(db.Float, default=0.0)
    NetSalary = db.Column(db.Float, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())


class SalarySQL(db.Model):
    __tablename__ = "salaries"
    __bind_key__ = "default"

    SalaryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey("employees.EmployeeID"))
    SalaryMonth = db.Column(db.Date, nullable=False)
    BaseSalary = db.Column(db.Float, nullable=False)
    Bonus = db.Column(db.Float, default=0.0)
    Deductions = db.Column(db.Float, default=0.0)
    NetSalary = db.Column(db.Float, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())

    employee = db.relationship('EmployeeSQL', backref='salary_records')

import json
# Lớp User
class User(db.Model):
    __bind_key__ = 'default'
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    FaceEncoding = db.Column(db.Text)  # Thêm trường lưu face encoding dạng JSON string

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def set_face_encoding(self, encoding):
        self.FaceEncoding = json.dumps(encoding.tolist())

    def get_face_encoding(self):
        if self.FaceEncoding:
            return np.array(json.loads(self.FaceEncoding))
        return None

    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    __tablename__ = 'roles'
    __bind_key__ = 'default'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(100), nullable=False)
    role_code = db.Column(db.String(50), nullable=False)

    # Quan hệ với bảng RolePermission
    role_permissions = db.relationship('RolePermission', back_populates='role')

    def __repr__(self):
        return f'<Role {self.role_name}>'


class RolePermission(db.Model):
    __tablename__ = 'role_permission'
    __bind_key__ = 'default'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), primary_key=True)

    role = db.relationship('Role', back_populates='role_permissions')
    permission = db.relationship('Permission', back_populates='role_permissions')


class Permission(db.Model):
    __tablename__ = 'permissions'
    __bind_key__ = 'default'

    permission_id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(100))
    permission_code = db.Column(db.String(50), unique=True)

    # Quan hệ với bảng RolePermission
    role_permissions = db.relationship('RolePermission', back_populates='permission')


# ----------------- ROUTES ------------------

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Bạn chưa đăng nhập!', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        flash('Người dùng không tồn tại!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        session['user_id'] = user.user_id  # Lưu user_id vào session sau khi đăng nhập
        session['logged_in'] = True
        session['role'] = user.role.role_code  # Lưu vai trò người dùng
        session['username'] = user.username  # Lưu tên người dùng
        session['email'] = user.email  # Lưu email
        session['phone_number'] = user.phone_number  # Lưu số điện thoại
        session['address'] = user.address  # Lưu địa chỉ
        session['birth_date'] = user.birth_date  # Lưu ngày sinh
        session['employee_id'] = user.user_id

        try:
            db.session.commit()
            flash('Thông tin đã được cập nhật!', 'success')
            session['email'] = user.email  # Lưu lại email vào session sau khi sửa
            session['phone_number'] = user.phone_number  # Lưu lại số điện thoại vào session
            session['address'] = user.address  # Lưu lại địa chỉ vào session
            session['birth_date'] = user.birth_date  # Lưu lại ngày sinh vào session
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật thông tin!', 'danger')

        return redirect(url_for('home'))  # Chuyển hướng đến trang chủ

    # Nếu là GET request, render form sửa đổi thông tin
    return render_template('edit_profile.html', user=user)


@app.route('/cancel_edit_profile')
def cancel_edit_profile():
    return redirect(url_for('home'))  # Điều hướng trở lại trang chủ khi nhấn hủy


@app.route('/view_profile')
def view_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('view_profile.html', user=user)


from flask import request, redirect, url_for, session, flash

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['role'] = user.role.role_code
            session['logged_in'] = True
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('cai_dat'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu', 'danger')
    return render_template('login.html')

@app.route("/home")
def home():
    # ✅ Kiểm tra đăng nhập
    if "logged_in" not in session:
        return redirect(url_for("login"))

    # ✅ Phân quyền
    role = session.get('role')
    permissions = {
        'ADMIN': ['quan_li_tai_chinh', 'quan_li_nhan_su', 'bao_cao_tai_chinh', 'phong_ban_chuc_vu', 'ho_so'],
        'HRM': ['quan_li_nhan_su', 'phong_ban_chuc_vu', 'ho_so'],
        'PM': ['quan_li_tai_chinh', 'bao_cao_tai_chinh', 'ho_so'],
        'EMP': ['ho_so'],
    }
    user_permissions = permissions.get(role, [])
    username = session.get("username", "")

    # ✅ Lấy thống kê nhân viên
    emps = EmployeeSQL.query.all() + EmployeeMySQL.query.all()
    total_employees = len(emps)
    working = len([e for e in emps if e.Status == "Đang làm"])
    on_leave = len([e for e in emps if e.Status == "Nghỉ phép"])
    resigned = total_employees - working - on_leave

    return render_template(
        "index.html",
        role=role,
        username=username,
        user_permissions=user_permissions,
        total_employees=total_employees,
        working=working,
        on_leave=on_leave,
        resigned=resigned,
        employees=emps,
        # placeholder cho biểu đồ công việc nếu chưa có bảng task:
        done=120,
        processing=80,
        remaining=40
    )

from collections import OrderedDict


@app.route("/quan-li-nhan-su")
def quan_li_nhan_su():
    role = session.get('role')
    permissions = {
        'ADMIN': ['quan_li_tai_chinh', 'quan_li_nhan_su', 'bao_cao_tai_chinh', 'phong_ban_chuc_vu', 'ho_so'],
        'HRM': ['quan_li_nhan_su', 'phong_ban_chuc_vu', 'ho_so'],
        'PM': ['quan_li_tai_chinh', 'bao_cao_tai_chinh', 'ho_so'],
        'EMP': ['ho_so'],
    }
    user_permissions = permissions.get(role, [])

    # --- 1) Lấy phòng ban, chức vụ và quyền ---
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()
    poss_sql = PositionSQL.query.all()
    poss_mysql = PositionMySQL.query.all()
    roles = Role.query.all()  # 👈 Lấy danh sách quyền từ bảng roles

    # Gộp phòng ban và chức vụ
    all_deps = deps_sql + deps_mysql
    all_pos = poss_sql + poss_mysql
    unique_deps = list(OrderedDict((d.DepartmentID, d) for d in all_deps).values())
    unique_pos = list(OrderedDict((p.PositionID, p) for p in all_pos).values())

    # --- 2) Lấy danh sách nhân viên ---
    emps_sql = EmployeeSQL.query.all()
    emps_mysql = EmployeeMySQL.query.all()
    merged_emps = emps_sql + emps_mysql

    dep_map = {d.DepartmentID: d.DepartmentName for d in unique_deps}
    pos_map = {p.PositionID: p.PositionName for p in unique_pos}

    nhan_viens = OrderedDict()
    for nv in merged_emps:
        if nv.EmployeeID in nhan_viens:
            continue
        nhan_viens[nv.EmployeeID] = {
            "EmployeeID": nv.EmployeeID,
            "FullName": nv.FullName,
            "DepartmentID": nv.DepartmentID,
            "PositionID": nv.PositionID,
            "DepartmentName": dep_map.get(nv.DepartmentID, "N/A"),
            "PositionName": pos_map.get(nv.PositionID, "N/A"),
            "Status": nv.Status,
            "Email": getattr(nv, 'Email', ''),
            "BirthDate": getattr(nv, 'BirthDate', None),
            "Gender": getattr(nv, 'Gender', ''),
            "JoinDate": getattr(nv, 'JoinDate', None)
        }

    return render_template(
        "quan_li_nhan_su.html",
        nhan_viens=list(nhan_viens.values()),
        departments=unique_deps,
        positions=unique_pos,
        roles=roles,
        role=role,
        user_permissions=user_permissions
    )



from sqlalchemy import text


@app.route("/them-nhan-vien", methods=["POST"])
def them_nhan_vien():
    # Lấy dữ liệu từ form
    employee_id = int(request.form["employee_id"])
    full_name = request.form["ho_ten"]
    department_id = int(request.form["phong_ban"])
    position_id = int(request.form["chuc_vu"])
    role_id = int(request.form["role_id"])
    status = request.form["trang_thai"]
    username = request.form["username"]
    password = request.form["password"]

    email = request.form.get("email")
    birth_date = request.form.get("birth_date")  # yyyy-mm-dd
    gender = request.form.get("gender")
    join_date = request.form.get("join_date")

    def to_date(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d") if d else None
        except:
            return None

    birth_date_dt = to_date(birth_date)
    join_date_dt = to_date(join_date)

    # Thêm nhân viên SQL Server
    engine_sqlserver = db.get_engine(app, bind='default')
    with engine_sqlserver.begin() as conn:
        conn.execute(text("SET IDENTITY_INSERT employees ON"))
        conn.execute(
            text(
                """
                INSERT INTO employees
                (EmployeeID, FullName, DepartmentID, PositionID, Status, Email, BirthDate, Gender, JoinDate)
                VALUES
                (:id, :name, :dep, :pos, :st, :email, :birth, :gender, :join)
                """
            ),
            {
                "id": employee_id,
                "name": full_name,
                "dep": department_id,
                "pos": position_id,
                "st": status,
                "email": email,
                "birth": birth_date_dt,
                "gender": gender,
                "join": join_date_dt,
            },
        )
        conn.execute(text("SET IDENTITY_INSERT employees OFF"))

    # Thêm nhân viên MySQL
    nv_mysql = EmployeeMySQL(
        EmployeeID=employee_id,
        FullName=full_name,
        DepartmentID=department_id,
        PositionID=position_id,
        Status=status,
        Email=email,
        BirthDate=birth_date_dt,
        Gender=gender,
        JoinDate=join_date_dt
    )
    db.session.add(nv_mysql)

    # Thêm user mới với mật khẩu đã băm
    user = User(
        user_id=employee_id,
        username=username,
        password=generate_password_hash(password),  # Băm mật khẩu trước khi lưu
        role_id=role_id,
        email=email,
        phone_number=None,
        address=None,
        birth_date=birth_date_dt,
    )
    db.session.add(user)

    db.session.commit()

    return redirect(url_for("quan_li_nhan_su"))



@app.route("/cap-nhat-nhan-vien/<int:ma_nv>", methods=["POST"])
def cap_nhat_nhan_vien(ma_nv):
    nv_sql = EmployeeSQL.query.get(ma_nv)
    nv_mysql = EmployeeMySQL.query.get(ma_nv)
    user = User.query.get(ma_nv)  # giả định user_id == EmployeeID

    full_name = request.form.get("ho_ten")
    department_id = request.form.get("phong_ban")
    position_id = request.form.get("chuc_vu")
    status = request.form.get("trang_thai", "Đang làm")

    username = request.form.get("username")
    password = request.form.get("password")
    role_id = request.form.get("role_id")
    email = request.form.get("email")
    birth_date = request.form.get("birth_date")
    gender = request.form.get("gender")
    join_date = request.form.get("join_date")

    from datetime import datetime
    def to_date(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d") if d else None
        except:
            return None

    birth_date_dt = to_date(birth_date)
    join_date_dt = to_date(join_date)

    if not nv_sql and not nv_mysql:
        flash("Không tìm thấy nhân viên!", "danger")
        return redirect(url_for("quan_li_nhan_su"))

    if nv_sql:
        nv_sql.FullName = full_name
        nv_sql.DepartmentID = department_id
        nv_sql.PositionID = position_id
        nv_sql.Status = status
        nv_sql.Email = email
        nv_sql.BirthDate = birth_date_dt
        nv_sql.Gender = gender
        nv_sql.JoinDate = join_date_dt

    if nv_mysql:
        nv_mysql.FullName = full_name
        nv_mysql.DepartmentID = department_id
        nv_mysql.PositionID = position_id
        nv_mysql.Status = status
        nv_mysql.Email = email
        nv_mysql.BirthDate = birth_date_dt
        nv_mysql.Gender = gender
        nv_mysql.JoinDate = join_date_dt

    # Cập nhật tài khoản nếu có
    if user:
        user.username = username
        if password:
            user.password = generate_password_hash(password)  # Băm mật khẩu nếu có đổi
        user.role_id = role_id
        user.email = email
        user.birth_date = birth_date_dt
        db.session.add(user)
    else:
        if not password:
            flash("Mật khẩu không được để trống khi tạo mới người dùng!", "danger")
            return redirect(url_for("quan_li_nhan_su"))
        
        new_user = User(
            user_id=ma_nv,
            username=username,
            password=generate_password_hash(password),
            role_id=role_id,
            email=email,
            phone_number=None,
            address=None,
            birth_date=birth_date_dt
        )
        db.session.add(new_user)

    db.session.commit()
    flash("Cập nhật nhân viên thành công!", "success")
    return redirect(url_for("quan_li_nhan_su"))



@app.route("/xoa-nhan-vien/<int:ma_nv>")
def xoa_nhan_vien(ma_nv):
    # Xóa bảng lương của nhân viên
    SalarySQL.query.filter_by(EmployeeID=ma_nv).delete()
    SalaryMySQL.query.filter_by(EmployeeID=ma_nv).delete()

    # Xóa chấm công của nhân viên
    AttendanceSQL.query.filter_by(EmployeeID=ma_nv).delete()
    AttendanceMySQL.query.filter_by(EmployeeID=ma_nv).delete()

    # Xóa nhân viên
    nv_sql = EmployeeSQL.query.get(ma_nv)
    nv_mysql = EmployeeMySQL.query.get(ma_nv)
    if nv_sql:
        db.session.delete(nv_sql)
    if nv_mysql:
        db.session.delete(nv_mysql)

    db.session.commit()
    return redirect(url_for("quan_li_nhan_su"))



@app.route("/quan_li_tai_chinh")
def quan_li_tai_chinh():
    role = session.get("role")
    permissions = {
        "ADMIN": [
            "quan_li_tai_chinh",
            "quan_li_nhan_su",
            "bao_cao_tai_chinh",
            "phong_ban_chuc_vu",
            "ho_so",
        ],
        "HRM": ["quan_li_nhan_su", "phong_ban_chuc_vu", "ho_so"],
        "PM": ["quan_li_tai_chinh", "bao_cao_tai_chinh", "ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    # --- 1) Gộp nhân viên (unique by EmployeeID) ---
    emps_sql = {e.EmployeeID: e for e in EmployeeSQL.query.all()}
    emps_mysql = {e.EmployeeID: e for e in EmployeeMySQL.query.all()}
    merged_emps = {}
    merged_emps.update(emps_sql)
    for eid, emp in emps_mysql.items():
        if eid not in merged_emps:
            merged_emps[eid] = emp
    sal_sql_q = SalarySQL.query.filter(SalarySQL.EmployeeID.isnot(None)).all()
    sal_mysql_q = SalaryMySQL.query.filter(SalaryMySQL.EmployeeID.isnot(None)).all()

    salary_employee_ids = {s.EmployeeID for s in sal_sql_q} | {s.EmployeeID for s in sal_mysql_q}
    employees_no_salary = [emp for eid, emp in merged_emps.items() if eid not in salary_employee_ids]
    # --- 2) Lấy salary và attendance ---
    sal_sql_q = SalarySQL.query.filter(SalarySQL.EmployeeID.isnot(None)).all()
    sal_mysql_q = SalaryMySQL.query.filter(SalaryMySQL.EmployeeID.isnot(None)).all()
    att_sql_q = AttendanceSQL.query.filter(AttendanceSQL.EmployeeID.isnot(None)).all()
    att_mysql_q = AttendanceMySQL.query.filter(AttendanceMySQL.EmployeeID.isnot(None)).all()

    # --- 3) Tạo map ---
    sal_sql_map = {s.EmployeeID: s for s in sal_sql_q}
    sal_mysql_map = {s.EmployeeID: s for s in sal_mysql_q}
    att_sql_map = {a.EmployeeID: a for a in att_sql_q}
    att_mysql_map = {a.EmployeeID: a for a in att_mysql_q}

    # --- 4) Tạo records ---
    
    records = []
    for eid, emp in merged_emps.items():
        sal = sal_sql_map.get(eid) or sal_mysql_map.get(eid)
        att = att_sql_map.get(eid) or att_mysql_map.get(eid)

        # Bỏ qua nếu không có salary hợp lệ hoặc SalaryID None
        if not sal or not getattr(sal, 'SalaryID', None):
            continue

        records.append({
            "SalaryID": sal.SalaryID,
            "EmployeeID": eid,
            "SalaryMonth": sal.SalaryMonth.strftime("%Y-%m") if sal.SalaryMonth else "---",
            "BaseSalary": f"{sal.BaseSalary:,.0f}" if sal.BaseSalary else "---",
            "Bonus": f"{sal.Bonus:,.0f}" if sal.Bonus else "0",
            "Deductions": f"{sal.Deductions:,.0f}" if sal.Deductions else "0",
            "NetSalary": f"{sal.NetSalary:,.0f}" if sal.NetSalary else "---",
            "SalaryCreated": sal.CreatedAt.strftime("%d/%m/%Y %H:%M") if sal.CreatedAt else "---",
            "AttendMonth": att.AttendanceMonth.strftime("%Y-%m") if att and att.AttendanceMonth else "---",
            "WorkDays": att.WorkDays if att else "---",
            "AbsentDays": att.AbsentDays if att else "---",
            "LeaveDays": att.LeaveDays if att else "---",
        })
      # ✅ Danh sách tháng từ 2022-01 đến 2028-12
    unique_months = sorted(
    { s["SalaryMonth"][:7] for s in records if s.get("SalaryMonth") },
    reverse=True
)
    return render_template(
        "quan_li_tai_chinh.html", records=records, role=role, unique_months=unique_months, user_permissions=user_permissions,employees_no_salary=employees_no_salary
    )

@app.route("/them-luong", methods=["POST"])
def them_luong():
    emp = int(request.form["employee_id"])
    mon = request.form["salary_month"] + "-01"  # YYYY-MM-01 format
    bs = float(request.form["base_salary"])
    bn = float(request.form["bonus"])
    ded = float(request.form["deductions"])
    net = bs + bn - ded
    now = datetime.now()

    # Tạo bản ghi mới trên SQL Server
    new_sql = SalarySQL(
        EmployeeID=emp,
        SalaryMonth=mon,
        BaseSalary=bs,
        Bonus=bn,
        Deductions=ded,
        NetSalary=net,
        CreatedAt=now,
    )
    db.session.add(new_sql)

    # Tạo bản ghi mới trên MySQL
    new_my = SalaryMySQL(
        EmployeeID=emp,
        SalaryMonth=mon,
        BaseSalary=bs,
        Bonus=bn,
        Deductions=ded,
        NetSalary=net,
        CreatedAt=now,
    )
    db.session.add(new_my)

    db.session.commit()

    return redirect(url_for("quan_li_tai_chinh"))


@app.route("/cap-nhat-luong/<int:salary_id>", methods=["POST"])
def cap_nhat_luong(salary_id):
    emp = int(request.form["employee_id"])
    mon = request.form["salary_month"] + "-01"
    bs = float(request.form["base_salary"])
    bn = float(request.form["bonus"])
    ded = float(request.form["deductions"])
    net = bs + bn - ded

    # SQL Server
    sal_sql = SalarySQL.query.get(salary_id)
    sal_sql.EmployeeID = emp
    sal_sql.SalaryMonth = mon
    sal_sql.BaseSalary = bs
    sal_sql.Bonus = bn
    sal_sql.Deductions = ded
    sal_sql.NetSalary = net

    # MySQL
    sal_my = SalaryMySQL.query.get(salary_id)
    sal_my.EmployeeID = emp
    sal_my.SalaryMonth = mon
    sal_my.BaseSalary = bs
    sal_my.Bonus = bn
    sal_my.Deductions = ded
    sal_my.NetSalary = net

    db.session.commit()
    return redirect(url_for("quan_li_tai_chinh"))


@app.route("/xoa-luong/<int:salary_id>")
def xoa_luong(salary_id):
    SalarySQL.query.filter_by(SalaryID=salary_id).delete()
    SalaryMySQL.query.filter_by(SalaryID=salary_id).delete()
    db.session.commit()
    return redirect(url_for("quan_li_tai_chinh"))

@app.route('/cham_cong', methods=['GET', 'POST'])
def cham_cong():
    if 'logged_in' not in session or session.get('role') not in ['EMP', 'HRM', 'ADMIN']:
        return redirect(url_for('login'))

    employee_id = session.get('employee_id')  # bạn cần lưu employee_id khi đăng nhập

    # Lấy thông tin chấm công nhân viên hiện tại
    attendance = AttendanceSQL.query.filter_by(EmployeeID=employee_id).first() or AttendanceMySQL.query.filter_by(EmployeeID=employee_id).first()

    # Nếu form submit
    if request.method == 'POST':
        work_days = request.form.get('work_days', type=int)
        absent_days = request.form.get('absent_days', type=int)
        leave_days = request.form.get('leave_days', type=int)
        attendance_month = request.form.get('attendance_month')  # yyyy-mm

        # Nếu chưa có bản ghi thì tạo mới
        if attendance is None:
            attendance = AttendanceSQL(EmployeeID=employee_id)
            db.session.add(attendance)

        attendance.WorkDays = work_days
        attendance.AbsentDays = absent_days
        attendance.LeaveDays = leave_days
        attendance.AttendanceMonth = datetime.strptime(attendance_month + '-01', '%Y-%m-%d')
        attendance.CreatedAt = datetime.now()

        db.session.commit()
        flash('Cập nhật chấm công thành công!', 'success')
        return redirect(url_for('cham_cong'))

    # Lấy thông tin nhân viên
    employee = EmployeeSQL.query.get(employee_id) or EmployeeMySQL.query.get(employee_id)

    return render_template('cham_cong.html', attendance=attendance, employee=employee)

@app.route("/phong-ban-chuc-vu")
def phong_ban_chuc_vu():
    role = session.get("role")
    permissions = {
        "ADMIN": [
            "quan_li_tai_chinh",
            "quan_li_nhan_su",
            "bao_cao_tai_chinh",
            "phong_ban_chuc_vu",
            "ho_so",
        ],
        "HRM": ["quan_li_nhan_su", "phong_ban_chuc_vu", "ho_so"],
        "PM": ["quan_li_tai_chinh", "bao_cao_tai_chinh", "ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    # Lấy phòng ban từ cả 2 csdl
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()

    # Gộp và loại bỏ trùng ID nếu có
    all_deps = deps_sql + deps_mysql
    unique_deps = {}
    for d in all_deps:
        if d.DepartmentID not in unique_deps:
            unique_deps[d.DepartmentID] = {
                "id": d.DepartmentID,
                "name": d.DepartmentName,
                "source": "HUMAN_2025_SQL" if isinstance(d, DepartmentSQL) else "HUMAN_2025_MYSQL"
            }

    depts = list(unique_deps.values())

    # Lấy chức vụ từ cả 2 csdl
    pos_sql = PositionSQL.query.all()
    pos_mysql = PositionMySQL.query.all()

    all_poses = pos_sql + pos_mysql
    unique_poses = {}
    for p in all_poses:
        if p.PositionID not in unique_poses:
            unique_poses[p.PositionID] = {
                "id": p.PositionID,
                "name": p.PositionName,
                "source": "HUMAN_2025_SQL" if isinstance(p, PositionSQL) else "HUMAN_2025_MYSQL"
            }

    poses = list(unique_poses.values())

    return render_template(
        "phong_ban_chuc_vu.html",
        depts=depts,
        poses=poses,
        role=role,
        user_permissions=user_permissions,
    )

@app.route("/bao-cao-tai-chinh")
def bao_cao_tai_chinh():
    role = session.get("role")
    permissions = {
        "ADMIN": [
            "quan_li_tai_chinh",
            "quan_li_nhan_su",
            "bao_cao_tai_chinh",
            "phong_ban_chuc_vu",
            "ho_so",
        ],
        "HRM": ["quan_li_nhan_su", "phong_ban_chuc_vu", "ho_so"],
        "PM": ["quan_li_tai_chinh", "bao_cao_tai_chinh", "ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    # Lấy tên phòng ban, tạo dict DepartmentID -> DepartmentName
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()
    all_deps = {}
    for d in deps_sql + deps_mysql:
        all_deps[d.DepartmentID] = d.DepartmentName

    # Lấy dữ liệu nhân sự từ SQL Server
    bao_cao_nhan_su_sql = (
        db.session.query(
            DepartmentSQL.DepartmentID.label("dept_id"),
            db.func.count(EmployeeSQL.EmployeeID).label("total"),
            db.func.sum(db.case((EmployeeSQL.Status == "Đang làm", 1), else_=0)).label("danglam"),
            db.func.sum(db.case((EmployeeSQL.Status == "Nghỉ việc", 1), else_=0)).label("nghiviec"),
        )
        .join(EmployeeSQL, DepartmentSQL.DepartmentID == EmployeeSQL.DepartmentID)
        .group_by(DepartmentSQL.DepartmentID)
        .all()
    )
    # Lấy dữ liệu nhân sự từ MySQL
    bao_cao_nhan_su_mysql = (
        db.session.query(
            DepartmentMySQL.DepartmentID.label("dept_id"),
            db.func.count(EmployeeMySQL.EmployeeID).label("total"),
            db.func.sum(db.case((EmployeeMySQL.Status == "Đang làm", 1), else_=0)).label("danglam"),
            db.func.sum(db.case((EmployeeMySQL.Status == "Nghỉ việc", 1), else_=0)).label("nghiviec"),
        )
        .join(EmployeeMySQL, DepartmentMySQL.DepartmentID == EmployeeMySQL.DepartmentID)
        .group_by(DepartmentMySQL.DepartmentID)
        .all()
    )

    # Tạo dict ưu tiên dữ liệu SQL Server trước
    nhan_su_dict = {}
    for rec in bao_cao_nhan_su_sql:
        nhan_su_dict[rec.dept_id] = {
            "total": rec.total,
            "danglam": rec.danglam,
            "nghiviec": rec.nghiviec,
        }

    # Thêm dữ liệu MySQL nếu dept_id chưa tồn tại trong SQL Server
    for rec in bao_cao_nhan_su_mysql:
        if rec.dept_id not in nhan_su_dict:
            nhan_su_dict[rec.dept_id] = {
                "total": rec.total,
                "danglam": rec.danglam,
                "nghiviec": rec.nghiviec,
            }

    ns_all = [
        (all_deps.get(dept_id, "N/A"), v["total"], v["danglam"], v["nghiviec"])
        for dept_id, v in nhan_su_dict.items()
    ]

    # Lấy dữ liệu lương từ SQL Server
    bao_cao_luong_sql = (
        db.session.query(
            DepartmentSQL.DepartmentID.label("dept_id"),
            db.func.sum(SalarySQL.NetSalary).label("total_salary"),
            db.func.count(SalarySQL.EmployeeID).label("count"),
            db.func.max(SalarySQL.SalaryMonth).label("latest_month"),
        )
        .join(EmployeeSQL, DepartmentSQL.DepartmentID == EmployeeSQL.DepartmentID)
        .join(SalarySQL, SalarySQL.EmployeeID == EmployeeSQL.EmployeeID)
        .group_by(DepartmentSQL.DepartmentID)
        .all()
    )
    # Lấy dữ liệu lương từ MySQL
    bao_cao_luong_mysql = (
        db.session.query(
            DepartmentMySQL.DepartmentID.label("dept_id"),
            db.func.sum(SalaryMySQL.NetSalary).label("total_salary"),
            db.func.count(SalaryMySQL.EmployeeID).label("count"),
            db.func.max(SalaryMySQL.SalaryMonth).label("latest_month"),
        )
        .join(EmployeeMySQL, DepartmentMySQL.DepartmentID == EmployeeMySQL.DepartmentID)
        .join(SalaryMySQL, SalaryMySQL.EmployeeID == EmployeeMySQL.EmployeeID)
        .group_by(DepartmentMySQL.DepartmentID)
        .all()
    )

    # Tạo dict ưu tiên dữ liệu SQL Server trước
    luong_dict = {}
    for rec in bao_cao_luong_sql:
        luong_dict[rec.dept_id] = {
            "total_salary": rec.total_salary or 0,
            "count": rec.count or 0,
            "latest_month": rec.latest_month,
        }

    # Thêm dữ liệu MySQL nếu dept_id chưa tồn tại trong SQL Server
    for rec in bao_cao_luong_mysql:
        if rec.dept_id not in luong_dict:
            luong_dict[rec.dept_id] = {
                "total_salary": rec.total_salary or 0,
                "count": rec.count or 0,
                "latest_month": rec.latest_month,
            }

    luong_all = [
        (
            all_deps.get(dept_id, "N/A"),
            val["total_salary"],
            int(val["total_salary"] / val["count"]) if val["count"] else 0,
            val["latest_month"],
        )
        for dept_id, val in luong_dict.items()
    ]

    return render_template(
        "bao_cao_tai_chinh.html",
        ns_all=ns_all,
        luong_all=luong_all,
        role=role,
        user_permissions=user_permissions,
    )



@app.route("/ho_so", methods=["GET", "POST"])
def ho_so():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    employee_id = session.get("employee_id")  # Lấy employee_id của người đang đăng nhập
    attendances = []
    permissions = {
        "ADMIN": [
            "quan_li_tai_chinh",
            "quan_li_nhan_su",
            "bao_cao_tai_chinh",
            "phong_ban_chuc_vu",
            "ho_so",
        ],
        "HRM": ["quan_li_nhan_su", "phong_ban_chuc_vu", "ho_so"],
        "PM": ["quan_li_tai_chinh", "bao_cao_tai_chinh", "ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    # Lấy dữ liệu employee nếu có employee_id
    employee = None
    salaries = []
    if employee_id:
        employee = EmployeeSQL.query.options(
            joinedload(EmployeeSQL.department),
            joinedload(EmployeeSQL.position)
        ).filter_by(EmployeeID=employee_id).first()

        if not employee:
            employee = EmployeeMySQL.query.options(
                joinedload(EmployeeMySQL.department),
                joinedload(EmployeeMySQL.position)
            ).filter_by(EmployeeID=employee_id).first()

        # Lấy lịch sử lương của nhân viên
        if employee:
            salaries = SalarySQL.query.filter_by(EmployeeID=employee_id).order_by(SalarySQL.SalaryMonth.desc()).all()

        if not salaries:
            salaries = SalaryMySQL.query.filter_by(EmployeeID=employee_id).order_by(SalaryMySQL.SalaryMonth.desc()).all()

    # Chấm công: chỉ lấy 1 nguồn
        attendance_sql = AttendanceSQL.query.filter_by(EmployeeID=employee_id).order_by(AttendanceSQL.AttendanceMonth.desc()).all()
        attendance_mysql = AttendanceMySQL.query.filter_by(EmployeeID=employee_id).order_by(AttendanceMySQL.AttendanceMonth.desc()).all()

        # Ưu tiên SQL Server, nếu không có thì dùng MySQL
        attendances = attendance_sql if attendance_sql else attendance_mysql

    if request.method == "POST":
        # Cập nhật thông tin người dùng nếu có
        # (cái này bạn đã xử lý rồi)
        return redirect(url_for("ho_so"))

    return render_template(
        "ho_so.html",
        user_permissions=user_permissions,
        employee=employee,
        attendances=attendances,
        salaries=salaries,
        role=role,
    )

@app.route("/cham_cong_ho_so", methods=["POST"])
def cham_cong_ho_so():
    employee_id = session.get("employee_id")
    attendance_month = request.form.get("attendance_month") + "-01"
    work_days = int(request.form.get("work_days"))
    absent_days = int(request.form.get("absent_days"))
    leave_days = int(request.form.get("leave_days"))

    existing = AttendanceSQL.query.filter_by(EmployeeID=employee_id, AttendanceMonth=attendance_month).first()
    if not existing:
        existing = AttendanceMySQL.query.filter_by(EmployeeID=employee_id, AttendanceMonth=attendance_month).first()

    if existing:
        existing.WorkDays = work_days
        existing.AbsentDays = absent_days
        existing.LeaveDays = leave_days
    else:
        new_att = AttendanceSQL(
            EmployeeID=employee_id,
            AttendanceMonth=attendance_month,
            WorkDays=work_days,
            AbsentDays=absent_days,
            LeaveDays=leave_days,
            CreatedAt=datetime.now()
        )
        db.session.add(new_att)

        new_att2 = AttendanceMySQL(
            EmployeeID=employee_id,
            AttendanceMonth=attendance_month,
            WorkDays=work_days,
            AbsentDays=absent_days,
            LeaveDays=leave_days,
            CreatedAt=datetime.now()
        )
        db.session.add(new_att2)

    db.session.commit()
    flash("Chấm công thành công!", "success")
    return redirect(url_for("ho_so"))



from datetime import date, timedelta
from collections import defaultdict

@app.route("/canh-bao-thong-bao", endpoint="canh_bao_thong_bao")
def canh_bao_thong_bao():
    role = session.get("role")
    permissions = {
        "ADMIN": ["quan_li_tai_chinh","quan_li_nhan_su","bao_cao_tai_chinh","phong_ban_chuc_vu","ho_so"],
        "HRM": ["quan_li_nhan_su","phong_ban_chuc_vu","ho_so"],
        "PM": ["quan_li_tai_chinh","bao_cao_tai_chinh","ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    # 1. Cảnh báo kỷ niệm công tác (30 ngày tới)
    today = date.today()
    days_ahead = 30
# Lấy tất cả nhân viên cả 2 DB
    employees_sql = EmployeeSQL.query.all()
    employees_mysql = EmployeeMySQL.query.all()

    # Gộp trùng theo EmployeeID
    all_employees_dict = {}
    for emp in employees_sql + employees_mysql:
        if emp.EmployeeID not in all_employees_dict:
            all_employees_dict[emp.EmployeeID] = emp
    all_employees = list(all_employees_dict.values())


    thong_bao_ky_niem = []
    for emp in all_employees:
        join_date = getattr(emp, 'JoinDate', None)  # Phải có trường này trong DB
        if join_date:
            next_anniversary = join_date.replace(year=today.year)
            if next_anniversary < today:
                next_anniversary = join_date.replace(year=today.year + 1)
            delta_days = (next_anniversary - today).days
            if 0 <= delta_days <= days_ahead:
                years = next_anniversary.year - join_date.year
                thong_bao_ky_niem.append({
                    "FullName": emp.FullName,
                    "anniversary": next_anniversary.strftime("%d/%m/%Y"),
                    "years": years,
                })

    # 2. Cảnh báo nghỉ phép quá nhiều
    gioi_han_phep = 1
    attendance_sql = AttendanceSQL.query.all()
    attendance_mysql = AttendanceMySQL.query.all()
    all_attendance = attendance_sql + attendance_mysql

    vuot_ngay_phep = []
    for att in all_attendance:
        if getattr(att, 'LeaveDays', 0) > gioi_han_phep:
            emp = EmployeeSQL.query.get(att.EmployeeID) or EmployeeMySQL.query.get(att.EmployeeID)
            if emp:
                vuot_ngay_phep.append({
                    "FullName": emp.FullName,
                    "LeaveDays": att.LeaveDays,
                })

    # 3. Cảnh báo chênh lệch lương lớn
    luong_sql = SalarySQL.query.order_by(SalarySQL.EmployeeID, SalarySQL.SalaryMonth).all()
    luong_mysql = SalaryMySQL.query.order_by(SalaryMySQL.EmployeeID, SalaryMySQL.SalaryMonth).all()
    all_luong = sorted(
    [l for l in luong_sql + luong_mysql if l.EmployeeID is not None and l.SalaryMonth is not None],
    key=lambda x: (x.EmployeeID, x.SalaryMonth)
)

    luong_by_emp = defaultdict(list)
    for l in all_luong:
        luong_by_emp[l.EmployeeID].append(l)

    chenh_lech_luong = []
    for emp_id, luongs in luong_by_emp.items():
        for i in range(1, len(luongs)):
            luong_truoc = luongs[i-1].NetSalary
            luong_hien_tai = luongs[i].NetSalary
            if luong_truoc == 0:
                continue
            chenh_lech = abs(luong_hien_tai - luong_truoc) / luong_truoc
            if chenh_lech > 0.2:  # trên 20%
                emp = EmployeeSQL.query.get(emp_id) or EmployeeMySQL.query.get(emp_id)
                if emp:
                    chenh_lech_luong.append({
                        "FullName": emp.FullName,
                        "thang_1": luongs[i-1].SalaryMonth.strftime("%Y-%m"),
                        "thang_2": luongs[i].SalaryMonth.strftime("%Y-%m"),
                        "chuyen_doi": "{:,.0f}".format(luong_hien_tai - luong_truoc),
                    })
    thong_bao_sinh_nhat = []
    for emp in all_employees:
        birth_date = getattr(emp, 'BirthDate', None)
        if birth_date:
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = birth_date.replace(year=today.year + 1)
            days_until = (next_birthday - today).days
            if 0 <= days_until <= days_ahead:
                thong_bao_sinh_nhat.append({
                    "FullName": emp.FullName,
                    "birthday": next_birthday.strftime("%d/%m/%Y"),
                    "days_left": days_until,
                })
    # 4. Danh sách email đã gửi (giả định)
    ds_email_gui_luong = []  # Cần tích hợp email gửi thực tế nếu có
    ds_email_gui_luong = session.pop('ds_email_gui_luong', [])  # chỉ hiển thị 1 lần
    return render_template("canh_bao_thong_bao.html",
                           thong_bao_ky_niem=thong_bao_ky_niem,
                           vuot_ngay_phep=vuot_ngay_phep,
                           gioi_han_phep=gioi_han_phep,
                           chenh_lech_luong=chenh_lech_luong,
                           ds_email_gui_luong=ds_email_gui_luong,
                            thong_bao_sinh_nhat=thong_bao_sinh_nhat,
                           role=role,
                           user_permissions=user_permissions)

class PayrollSalary(db.Model):
    __bind_key__ = 'payroll'  # nếu bạn dùng nhiều DB, nếu không bỏ dòng này
    __tablename__ = 'payroll_salary'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20))  # Tháng, vd "Tháng 1"
    amount = db.Column(db.Integer)    # Số tiền lương

@app.route('/dashboard')
def dashboard():
    # Chỉ lấy từ 1 bảng (ví dụ EmployeeSQL)
    total_employees = EmployeeSQL.query.count()

    working = EmployeeSQL.query.filter(EmployeeSQL.Status == 'Đang làm').count()

    on_leave = EmployeeSQL.query.filter(EmployeeSQL.Status == 'Nghỉ việc').count()

    # Dữ liệu biểu đồ lương mẫu (hoặc từ DB nếu bạn muốn)
    salary_labels = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4"]
    salary_data = [12000000, 13000000, 12500000, 14000000]

    return render_template('dashboard.html',
                           total_employees=total_employees,
                           working=working,
                           on_leave=on_leave,
                           salary_labels=salary_labels,
                           salary_data=salary_data)




@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    # Kiểm tra mật khẩu và nếu đúng, lưu thông tin vào session
    if user and check_password_hash(user.password, password):
        session["logged_in"] = True
        session["role"] = user.role.role_code if user.role else None
        session["username"] = user.username
        session["email"] = user.email
        session["phone_number"] = user.phone_number
        session["address"] = user.address
        session["birth_date"] = user.birth_date

        session["employee_id"] = user.user_id  # Quan trọng: lưu mã nhân viên để lấy thông tin chi tiết

        flash("Đăng nhập thành công!", "success")
        return redirect(url_for("home"))
    else:
        flash("Thông tin đăng nhập sai, vui lòng thử lại.", "danger")
        return redirect(url_for("login"))



from flask_jwt_extended import get_jwt_identity


# API chỉ cho phép người dùng có quyền Admin truy cập
@app.route("/admin-data", methods=["GET"])
def admin_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role.role_code != "Admin Manager":
        return jsonify({"msg": "Access denied"}), 403
    return jsonify({"msg": "Welcome to the admin area!"}), 200


# API chỉ cho phép HR Manager truy cập
@app.route("/hr-manager", methods=["GET"])
def hr_manager_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role.role_code != "HR Manager":
        return jsonify({"msg": "Access denied"}), 403
    return jsonify({"msg": "Welcome to the HR Manager area!"}), 200


# API chỉ cho phép Payroll Manager truy cập
@app.route("/payroll-manager", methods=["GET"])
def payroll_manager_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role.role_code != "Payroll Manager":
        return jsonify({"msg": "Access denied"}), 403
    return jsonify({"msg": "Welcome to the Payroll Manager area!"}), 200


# API cho Employee chỉ có quyền xem thông tin cá nhân
@app.route("/employee", methods=["GET"])
def employee_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role.role_code != "Employee":
        return jsonify({"msg": "Access denied"}), 403
    return jsonify({"msg": "Welcome to your personal area!"}), 200


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"msg": "Unauthorized access"}), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({"msg": "Forbidden access"}), 403


@app.route("/tc")
def index():
    return render_template("index.html")  # Hiển thị trang index.html nếu đã đăng nhập


@app.route("/cap-nhat-ho-so", methods=["POST"])
def cap_nhat_ho_so():
    # Lấy thông tin từ form
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if user:
        # Cập nhật các trường thông tin
        user.FullName = request.form.get("username")
        user.email = request.form.get("email")
        user.phone_number = request.form.get("phone")
        user.address = request.form.get("address")

        # Lưu thay đổi
        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for("ho_so"))  # Quay lại trang hồ sơ
    else:
        flash("Không tìm thấy người dùng!", "danger")
        return redirect(url_for("home"))

import pandas as pd
import io
from flask import send_file

@app.route("/xuat-nhan-vien")
def xuat_excel_nhan_vien():
    # Lấy dữ liệu nhân viên từ cả SQL Server và MySQL
    emps_sql = EmployeeSQL.query.all()
    emps_mysql = EmployeeMySQL.query.all()

    # Ưu tiên bản SQL nếu bị trùng EmployeeID
    combined = {}
    for emp in emps_mysql + emps_sql:
        combined[emp.EmployeeID] = emp  # SQL sẽ ghi đè

    data = []
    for emp in combined.values():
        data.append({
            "Mã NV": emp.EmployeeID,
            "Họ Tên": emp.FullName,
            "Phòng Ban": emp.department.DepartmentName if emp.department else "N/A",
            "Chức Vụ": emp.position.PositionName if emp.position else "N/A",
            "Trạng Thái": emp.Status,
            "Email": getattr(emp, "Email", "N/A") or "N/A",  # Phòng trường hợp không có trường Email
            "Ngày sinh": emp.BirthDate.strftime('%d/%m/%Y') if getattr(emp, "BirthDate", None) else "N/A",
            "Giới tính": getattr(emp, "Gender", "N/A") or "N/A",
            "Ngày vào làm": emp.JoinDate.strftime('%d/%m/%Y') if getattr(emp, "JoinDate", None) else "N/A"
        })

    # Xuất ra Excel
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="NhanVien")
    output.seek(0)

    return send_file(output, download_name="nhan_vien.xlsx", as_attachment=True)


@app.route('/xuat-phongban')
def xuat_phongban():
    # Lấy dữ liệu phòng ban từ SQL Server
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()
    
    # Lấy dữ liệu chức vụ từ SQL Server
    pos_sql = PositionSQL.query.all()
    pos_mysql = PositionMySQL.query.all()

    # Chuyển về list of dict
    phong_ban_data = [{"ID": d.DepartmentID, "Tên phòng ban": d.DepartmentName} for d in deps_sql + deps_mysql]
    chuc_vu_data = [{"ID": p.PositionID, "Tên chức vụ": p.PositionName} for p in pos_sql + pos_mysql]

    # Tạo file Excel với 2 sheet
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(phong_ban_data).to_excel(writer, index=False, sheet_name='PhongBan')
        pd.DataFrame(chuc_vu_data).to_excel(writer, index=False, sheet_name='ChucVu')
    output.seek(0)

    return send_file(output, download_name="phong_ban_chuc_vu.xlsx", as_attachment=True)

@app.route("/xuat-luong-chamcong")
def xuat_luong_chamcong():
    # Lấy dữ liệu lương từ 2 bảng
    salaries_sql = SalarySQL.query.all()
    salaries_mysql = SalaryMySQL.query.all()
    salaries = salaries_sql + salaries_mysql

    # Gộp lương theo EmployeeID lấy bản mới nhất
    latest_salaries = {}
    for s in salaries:
        emp_id = s.EmployeeID
        if emp_id not in latest_salaries:
            latest_salaries[emp_id] = s
        else:
            existing = latest_salaries[emp_id]
            if (s.SalaryMonth and existing.SalaryMonth and s.SalaryMonth > existing.SalaryMonth) or \
               (hasattr(s, 'CreatedAt') and hasattr(existing, 'CreatedAt') and s.CreatedAt > existing.CreatedAt):
                latest_salaries[emp_id] = s

    # Lấy dữ liệu chấm công từ 2 bảng
    attendance_sql = AttendanceSQL.query.all()
    attendance_mysql = AttendanceMySQL.query.all()
    attendances = attendance_sql + attendance_mysql

    # Gộp chấm công theo EmployeeID lấy bản mới nhất
    latest_attendances = {}
    for c in attendances:
        emp_id = c.EmployeeID
        if emp_id not in latest_attendances:
            latest_attendances[emp_id] = c
        else:
            existing = latest_attendances[emp_id]
            if (c.AttendanceMonth and existing.AttendanceMonth and c.AttendanceMonth > existing.AttendanceMonth) or \
               (hasattr(c, 'CreatedAt') and hasattr(existing, 'CreatedAt') and c.CreatedAt > existing.CreatedAt):
                latest_attendances[emp_id] = c

    # Tạo DataFrame từ dữ liệu lương và chấm công đã gộp
    df_luong = pd.DataFrame([{
        "Mã Lương": s.SalaryID,
        "Mã NV": s.EmployeeID,
        "Tháng": s.SalaryMonth.strftime("%Y-%m") if s.SalaryMonth else "",
        "Lương Cơ Bản": s.BaseSalary,
        "Thưởng": s.Bonus,
        "Khấu Trừ": s.Deductions,
        "Lương Thực Nhận": s.NetSalary,
        "Ngày Tạo": s.CreatedAt.strftime("%d/%m/%Y %H:%M") if hasattr(s, 'CreatedAt') and s.CreatedAt else ""
    } for s in latest_salaries.values()])

    df_cc = pd.DataFrame([{
        "Mã NV": c.EmployeeID,
        "Tháng": c.AttendanceMonth.strftime("%Y-%m") if c.AttendanceMonth else "",
        "Ngày Làm Việc": c.WorkDays,
        "Ngày Vắng": c.AbsentDays,
        "Ngày Nghỉ Phép": c.LeaveDays
    } for c in latest_attendances.values()])

    # Xuất file Excel với 2 sheet
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_luong.to_excel(writer, index=False, sheet_name="Luong")
        df_cc.to_excel(writer, index=False, sheet_name="ChamCong")

    output.seek(0)
    return send_file(output, download_name="luong_cham_cong.xlsx", as_attachment=True)


@app.route("/xuat-bao-cao")
def xuat_bao_cao():
    # Lấy nhân viên
    employees_sql = EmployeeSQL.query.all()
    employees_mysql = EmployeeMySQL.query.all()
    # Ưu tiên bản SQL Server, nếu trùng sẽ ghi đè MySQL
    emp_dict = {emp.EmployeeID: emp for emp in employees_mysql}
    emp_dict.update({emp.EmployeeID: emp for emp in employees_sql})
    all_employees = list(emp_dict.values())

    # Lấy lương
    salaries_sql = SalarySQL.query.all()
    salaries_mysql = SalaryMySQL.query.all()
    sal_dict = {}
    for s in salaries_mysql:
        sal_dict[s.EmployeeID] = s
    for s in salaries_sql:
        sal_dict[s.EmployeeID] = s  # ghi đè nếu trùng EmployeeID
    all_salaries = list(sal_dict.values())

    # Lấy thông tin phòng ban
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()
    dep_dict = {d.DepartmentID: d.DepartmentName for d in deps_mysql}
    dep_dict.update({d.DepartmentID: d.DepartmentName for d in deps_sql})
    all_deps = dep_dict

    # Báo cáo nhân sự
    nhan_su = {}
    # Báo cáo nhân sự
    nhan_su = {}
    for emp in all_employees:
        dept_name = all_deps.get(emp.DepartmentID, "N/A")
        if dept_name not in nhan_su:
            nhan_su[dept_name] = {"Tổng NV": 0, "Đang Làm": 0, "Nghỉ Việc": 0}
        nhan_su[dept_name]["Tổng NV"] += 1

        status_clean = emp.Status.strip().lower() if emp.Status else ""
        print(f"Status raw: {repr(emp.Status)}, cleaned: {status_clean}")  # Debug xem giá trị thực tế

        if status_clean == "đang làm":
            nhan_su[dept_name]["Đang Làm"] += 1
        elif status_clean == "nghỉ việc" or status_clean == "nghỉ việc?c?":  # có thể sửa thêm ký tự lạ
            nhan_su[dept_name]["Nghỉ Việc"] += 1



    df_nhansu = pd.DataFrame([
        {
            "Phòng Ban": k,
            "Tổng NV": v["Tổng NV"],
            "Đang Làm": v["Đang Làm"],
            "Nghỉ Việc": v["Nghỉ Việc"]
        }
        for k, v in nhan_su.items()
    ])

    # Báo cáo lương
    luong = {}
    for s in all_salaries:
        emp = next((e for e in all_employees if e.EmployeeID == s.EmployeeID), None)
        if not emp:
            continue
        dept_name = all_deps.get(emp.DepartmentID, "N/A")
        if dept_name not in luong:
            luong[dept_name] = {
                "Tổng Lương": 0,
                "Số Người": 0,
                "Tháng Gần Nhất": s.SalaryMonth
            }
        luong[dept_name]["Tổng Lương"] += s.NetSalary
        luong[dept_name]["Số Người"] += 1
        if s.SalaryMonth and s.SalaryMonth > luong[dept_name]["Tháng Gần Nhất"]:
            luong[dept_name]["Tháng Gần Nhất"] = s.SalaryMonth

    df_luong = pd.DataFrame([
        {
            "Phòng Ban": k,
            "Tổng Lương": "{:,.0f}".format(v["Tổng Lương"]),
            "Lương Trung Bình": "{:,.0f}".format(v["Tổng Lương"] / v["Số Người"]) if v["Số Người"] else "0",
            "Tháng Gần Nhất": v["Tháng Gần Nhất"].strftime("%Y-%m") if v["Tháng Gần Nhất"] else ""
        }
        for k, v in luong.items()
    ])

    # Xuất Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_nhansu.to_excel(writer, index=False, sheet_name='NhanSu')
        df_luong.to_excel(writer, index=False, sheet_name='Luong')

    output.seek(0)
    return send_file(output, download_name="bao_cao_thong_ke.xlsx", as_attachment=True)


import pandas as pd

@app.route("/nhap-excel-nhan-vien", methods=["POST"])
def nhap_excel_nhan_vien():
    file = request.files.get("excel_file")
    if not file:
        flash("Không có file được chọn!", "danger")
        return redirect(url_for("quan_li_nhan_su"))

    try:
        df = pd.read_excel(file)
    except Exception as e:
        flash("Không đọc được file Excel!", "danger")
        print("Lỗi đọc Excel:", e)
        return redirect(url_for("quan_li_nhan_su"))

    dep_map = {d.DepartmentName: d.DepartmentID for d in DepartmentSQL.query.all()}
    pos_map = {p.PositionName: p.PositionID for p in PositionSQL.query.all()}

    for _, row in df.iterrows():
        try:
            emp_id = int(row["Mã NV"])
            if EmployeeSQL.query.get(emp_id):
                continue  # đã tồn tại

            emp = EmployeeSQL(
                EmployeeID=emp_id,
                FullName=row["Họ Tên"],
                DepartmentID=dep_map.get(row["Phòng Ban"]),
                PositionID=pos_map.get(row["Chức Vụ"]),
                Status=row["Trạng Thái"]
            )
            db.session.add(emp)
        except Exception as e:
            print("Lỗi:", e)
            continue

    db.session.commit()
    flash("Nhập dữ liệu từ Excel thành công!", "success")
    return redirect(url_for("quan_li_nhan_su"))


@app.route("/dang-xuat")
def dang_xuat():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        birth_date = request.form.get("birth_date")

        # Kiểm tra username đã tồn tại chưa
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Tên đăng nhập đã tồn tại!", "danger")
            return redirect(url_for("register"))

        # Hash password trước khi lưu
        hashed_password = generate_password_hash(password)

        # Tạo User mới với role nhân viên (EMP)
        role_emp = Role.query.filter_by(role_code="EMP").first()
        if not role_emp:
            flash("Role EMP chưa được cấu hình trong hệ thống.", "danger")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password=hashed_password,
            role_id=role_emp.role_id,
            email=email,
            phone_number=phone,
            address=address,
            birth_date=datetime.strptime(birth_date, "%Y-%m-%d") if birth_date else None
        )
        db.session.add(new_user)
        db.session.commit()

        # Tự động đăng nhập sau khi đăng ký thành công
        session["logged_in"] = True
        session["role"] = role_emp.role_code
        session["username"] = username
        session["employee_id"] = new_user.user_id

        flash("Đăng ký thành công! Bạn đã được đăng nhập với vai trò nhân viên.", "success")
        return redirect(url_for("home"))

    return render_template("dang_ki.html")

@app.route('/them-phong-ban', methods=['POST'])
def them_phong_ban():
    department_id = request.form.get('department_id')
    department_name = request.form.get('department_name')

    if not department_id or not department_name:
        flash('Mã phòng ban và tên phòng ban không được để trống.', 'danger')
        return redirect(url_for('phong_ban_chuc_vu'))

    try:
        department_id = int(department_id)
    except ValueError:
        flash('Mã phòng ban phải là số nguyên.', 'danger')
        return redirect(url_for('phong_ban_chuc_vu'))

    try:
        # Kiểm tra xem department_id đã tồn tại trong cả 2 cơ sở dữ liệu chưa
        exist_sql = DepartmentSQL.query.get(department_id)
        exist_mysql = DepartmentMySQL.query.get(department_id)

        if exist_sql or exist_mysql:
            flash('Mã phòng ban đã tồn tại.', 'danger')
            return redirect(url_for('phong_ban_chuc_vu'))

        # Tạo đối tượng mới cho SQL Server
        new_dep_sql = DepartmentSQL(
            DepartmentID=department_id,
            DepartmentName=department_name
        )
        # Tạo đối tượng mới cho MySQL
        new_dep_mysql = DepartmentMySQL(
            DepartmentID=department_id,
            DepartmentName=department_name
        )

        db.session.add(new_dep_sql)
        db.session.add(new_dep_mysql)

        db.session.commit()
        flash('Thêm phòng ban thành công ở cả 2 cơ sở dữ liệu!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi thêm phòng ban: {str(e)}', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))




@app.route('/sua-phong-ban/<int:id>', methods=['POST'])
def sua_phong_ban(id):
    dep_sql = DepartmentSQL.query.get(id)
    dep_mysql = DepartmentMySQL.query.get(id)
    name = request.form.get('department_name')
    if not name:
        flash('Tên phòng ban không được để trống.', 'danger')
        return redirect(url_for('phong_ban_chuc_vu'))

    if dep_sql:
        dep_sql.DepartmentName = name
    if dep_mysql:
        dep_mysql.DepartmentName = name

    if dep_sql or dep_mysql:
        db.session.commit()
        flash('Cập nhật phòng ban thành công ở cả 2 CSDL!', 'success')
    else:
        flash('Phòng ban không tồn tại.', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))



@app.route('/xoa-phong-ban/<int:id>', methods=['POST'])
def xoa_phong_ban(id):
    dep_sql = DepartmentSQL.query.get(id)
    dep_mysql = DepartmentMySQL.query.get(id)

    if dep_sql:
        db.session.delete(dep_sql)
    if dep_mysql:
        db.session.delete(dep_mysql)

    if dep_sql or dep_mysql:
        db.session.commit()
        flash('Xóa phòng ban thành công ở cả 2 CSDL!', 'success')
    else:
        flash('Phòng ban không tồn tại.', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))


# Tương tự với chức vụ

@app.route('/them-chuc-vu', methods=['POST'])
def them_chuc_vu():
    position_name = request.form.get('position_name')

    if not position_name:
        flash('Tên chức vụ không được để trống.', 'danger')
        return redirect(url_for('phong_ban_chuc_vu'))

    try:
        print(f"Đang thêm chức vụ: {position_name}")  # Debug

        new_pos_sql = PositionSQL(PositionName=position_name)
        new_pos_mysql = PositionMySQL(PositionName=position_name)

        db.session.add(new_pos_sql)
        db.session.add(new_pos_mysql)
        db.session.commit()

        print("Thêm chức vụ thành công")  # Debug
        flash('Thêm chức vụ thành công ở cả 2 cơ sở dữ liệu!', 'success')

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi thêm chức vụ: {e}")  # Debug
        flash(f'Lỗi khi thêm chức vụ: {str(e)}', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))



@app.route('/sua-chuc-vu/<int:id>', methods=['POST'])
def sua_chuc_vu(id):
    pos_sql = PositionSQL.query.get(id)
    pos_mysql = PositionMySQL.query.get(id)
    name = request.form.get('position_name')

    if not name:
        flash('Tên chức vụ không được để trống.', 'danger')
        return redirect(url_for('phong_ban_chuc_vu'))

    if pos_sql:
        pos_sql.PositionName = name
    if pos_mysql:
        pos_mysql.PositionName = name

    if pos_sql or pos_mysql:
        db.session.commit()
        flash('Cập nhật chức vụ thành công ở cả 2 CSDL!', 'success')
    else:
        flash('Chức vụ không tồn tại.', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))


@app.route('/xoa-chuc-vu/<int:id>', methods=['POST'])
def xoa_chuc_vu(id):
    pos_sql = PositionSQL.query.get(id)
    pos_mysql = PositionMySQL.query.get(id)

    if pos_sql:
        db.session.delete(pos_sql)
    if pos_mysql:
        db.session.delete(pos_mysql)

    if pos_sql or pos_mysql:
        db.session.commit()
        flash('Xóa chức vụ thành công ở cả 2 CSDL!', 'success')
    else:
        flash('Chức vụ không tồn tại.', 'danger')

    return redirect(url_for('phong_ban_chuc_vu'))

@app.route('/api/get-employees-by-department/<int:department_id>')
def get_employees_by_department(department_id):
    emps_sql = EmployeeSQL.query.filter_by(DepartmentID=department_id).all()
    emps_mysql = EmployeeMySQL.query.filter_by(DepartmentID=department_id).all()

    # Dùng dict để gộp, key là EmployeeID (ưu tiên dữ liệu SQL Server nếu trùng)
    merged_emps = {}
    for emp in emps_mysql:
        merged_emps[emp.EmployeeID] = emp
    for emp in emps_sql:
        merged_emps[emp.EmployeeID] = emp  # Ghi đè nếu trùng

    data = []
    for e in merged_emps.values():
        data.append({
            "EmployeeID": e.EmployeeID,
            "FullName": e.FullName,
            "PositionName": (e.position.PositionName if hasattr(e, 'position') and e.position else "N/A"),
            "Status": e.Status
        })

    return jsonify(data)


import re
import base64
import io
import numpy as np
from PIL import Image
import face_recognition
from flask import jsonify

from flask import request, jsonify, session
import numpy as np
import base64
import io
import face_recognition
from PIL import Image
import re

@app.route('/api/face-login', methods=['POST'])
def face_login():
    try:
        data = request.get_json()  # Nhận ảnh từ frontend
        img_data = data.get('image')
        if not img_data:
            return jsonify({'success': False, 'message': 'Không nhận được dữ liệu ảnh'}), 400

        # Xử lý ảnh base64
        img_str = re.sub('^data:image/.+;base64,', '', img_data)
        img_bytes = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_bytes))
        img_np = np.array(img)

        encodings = face_recognition.face_encodings(img_np)
        if not encodings:
            return jsonify({'success': False, 'message': 'Không phát hiện khuôn mặt'}), 400
        unknown_encoding = encodings[0]

        # Truy vấn tất cả người dùng và FaceEncoding của họ
        users = User.query.filter(User.FaceEncoding.isnot(None)).all()

        for user in users:
            # Chuyển FaceEncoding từ string (hoặc bytes) thành numpy array
            known_encoding = np.array(eval(user.FaceEncoding))  # Sử dụng json.loads() nếu lưu dạng JSON

            # So sánh khuôn mặt
            matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.6)
            if matches[0]:  # Nếu trùng khớp
                # Lưu thông tin đăng nhập vào session
                session['logged_in'] = True
                session['employee_id'] = user.user_id
                session['user_id'] = user.user_id
                session['username'] = user.username
                session['role'] = user.role.role_code if user.role else None
                session['email'] = user.email
                session['phone_number'] = user.phone_number
                session['birth_date'] = user.birth_date


                return jsonify({
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'redirect': '/home'  # Gửi URL trang đích đến frontend
                })

        return jsonify({'success': False, 'message': 'Khuôn mặt không khớp với bất kỳ tài khoản nào'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': 'Lỗi server: ' + str(e)}), 500

    
@app.route('/api/register-user', methods=['POST'], endpoint='register_user')
def register_user():

    data = request.json
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')

    # Kiểm tra trùng username trên 2 DB
    if User.query.filter_by(Username=username).first() or User.query.filter_by(Username=username).first():
        return jsonify({'success': False, 'message': 'Username đã tồn tại'}), 400

    # Ví dụ lưu vào SQL Server, bạn có thể đổi thành lưu MySQL tùy yêu cầu
    new_emp = User(Username=username, Password=password, FullName=fullname)
    db.session.add(new_emp)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Đăng ký thành công', 'employee_id': new_emp.EmployeeID})

from PIL import Image
import io


@app.route('/api/register-face/<int:employee_id>', methods=['POST'])
def register_face(employee_id):
    data = request.json
    img_data = data.get('image')

    img_str = re.sub('^data:image/.+;base64,', '', img_data)
    img_bytes = base64.b64decode(img_str)
    img = Image.open(io.BytesIO(img_bytes))
    img_np = np.array(img)

    encodings = face_recognition.face_encodings(img_np)
    if not encodings:
        return jsonify({'success': False, 'message': 'Không phát hiện khuôn mặt'}), 400
    face_encoding = encodings[0]

    # Tìm và cập nhật trên SQL Server
    emp_sql = User.query.get(employee_id)
    if emp_sql:
        emp_sql.set_face_encoding(face_encoding)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật khuôn mặt thành công (SQL Server)'})

    # Nếu không tìm thấy thì trên MySQL
    emp_mysql = User.query.get(employee_id)
    if emp_mysql:
        emp_mysql.set_face_encoding(face_encoding)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật khuôn mặt thành công (MySQL)'})

    return jsonify({'success': False, 'message': 'Nhân viên không tồn tại'}), 404

@app.route('/api/login', methods=['POST'], endpoint='api_login')
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Truy vấn bảng User thay vì EmployeeSQL
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Sai tên đăng nhập hoặc mật khẩu'}), 401

    return jsonify({'success': True, 'message': 'Đăng nhập thành công', 'user_id': user.user_id})


@app.route('/api/login-face', methods=['POST'], endpoint='api_login_face')
def api_login_face():
    data = request.json
    img_data = data.get('image')

    img_str = re.sub('^data:image/.+;base64,', '', img_data)
    img_bytes = base64.b64decode(img_str)
    img = Image.open(io.BytesIO(img_bytes))
    img_np = np.array(img)

    encodings = face_recognition.face_encodings(img_np)
    if not encodings:
        return jsonify({'success': False, 'message': 'Không phát hiện khuôn mặt'}), 400
    face_encoding = encodings[0]

    emps_sql = EmployeeSQL.query.filter(EmployeeSQL.FaceEncoding != None).all()
    emps_mysql = EmployeeMySQL.query.filter(EmployeeMySQL.FaceEncoding != None).all()

    employees = emps_sql + emps_mysql
    known_encodings = [emp.get_face_encoding() for emp in employees]

    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    if True in matches:
        idx = matches.index(True)
        matched_emp = employees[idx]
        return jsonify({'success': True, 'message': 'Đăng nhập thành công', 'employee_id': matched_emp.EmployeeID})

    return jsonify({'success': False, 'message': 'Khuôn mặt không khớp'}), 401


@app.route("/cai-dat", methods=["GET", "POST"])
def cai_dat():
    role = session.get("role")
    user_id = session.get("user_id")
    employee_id = session.get("employee_id")
    user = User.query.get(user_id)
    employee = EmployeeSQL.query.get(employee_id)
    if not employee:
        employee = EmployeeMySQL.query.get(employee_id)

    permissions = {
        "ADMIN": ["quan_li_tai_chinh", "quan_li_nhan_su", "bao_cao_tai_chinh", "phong_ban_chuc_vu", "ho_so"],
        "HRM": ["quan_li_nhan_su", "phong_ban_chuc_vu", "ho_so"],
        "PM": ["quan_li_tai_chinh", "bao_cao_tai_chinh", "ho_so"],
        "EMP": ["ho_so"],
    }
    user_permissions = permissions.get(role, [])

    if request.method == "POST":
        old_password = request.form.get("oldPassword")
        new_password = request.form.get("newPassword")

        if user and user.password and check_password_hash(user.password, old_password):
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Mật khẩu đã được thay đổi thành công", "success")
        else:
            flash("Mật khẩu cũ không chính xác", "danger")

    return render_template("cai_dat.html", role=role, user_permissions=user_permissions, user=user, employee=employee)


    
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import random
import string
from datetime import datetime, timedelta

# Khai báo biến toàn cục ở ngoài hàm
verification_codes = {}

@app.route("/send-verification-code", methods=["POST"])
def send_verification_code():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'error': 'Email không hợp lệ'}), 400

        code = ''.join(random.choices(string.digits, k=6))
        verification_codes[email] = {'code': code, 'expires_at': datetime.now() + timedelta(minutes=10)}

        sender_email = "truongga471@gmail.com"
        sender_password = "eguwsubamvrferrz"


        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = Header("Mã xác nhận đổi mật khẩu", 'utf-8')

        body = f"Đây là mã xác nhận của bạn: {code}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_bytes())  # Gửi dưới dạng bytes

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json or request.form
    email = data.get('email')
    new_password = data.get('password')
    entered_code = data.get('verificationCode')

    if not email or not new_password or not entered_code:
        return jsonify({'success': False, 'message': 'Thiếu dữ liệu yêu cầu'}), 400

    # Lấy mã xác nhận đúng từ dictionary verification_codes
    code_info = verification_codes.get(email)
    if not code_info:
        return jsonify({'success': False, 'message': 'Chưa gửi mã xác nhận hoặc mã đã hết hạn.'}), 400

    # Kiểm tra mã còn hiệu lực không
    if datetime.now() > code_info['expires_at']:
        del verification_codes[email]  # Xóa mã hết hạn
        return jsonify({'success': False, 'message': 'Mã xác nhận đã hết hạn.'}), 400

    # So sánh mã xác nhận
    if entered_code != code_info['code']:
        return jsonify({'success': False, 'message': 'Mã xác nhận không chính xác.'}), 400

    # Tìm user theo email trực tiếp từ DB
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại.'}), 404

    # Cập nhật mật khẩu mới (hash)
    user.password = generate_password_hash(new_password)
    db.session.commit()

    # Xóa mã xác nhận đã dùng
    del verification_codes[email]

    return jsonify({'success': True, 'message': 'Mật khẩu đã được thay đổi.'})

@app.route('/gui-email-luong/<int:employee_id>')
def gui_email_luong(employee_id):
    emp = EmployeeSQL.query.get(employee_id) or EmployeeMySQL.query.get(employee_id)
    user = User.query.get(employee_id)
    salary = SalarySQL.query.filter_by(EmployeeID=employee_id).order_by(SalarySQL.SalaryMonth.desc()).first()

    if not (emp and user and salary and user.email):
        return "Không đủ dữ liệu để gửi email.", 400

    msg = Message(
        subject=f"[PAYROLL] Bảng lương tháng {salary.SalaryMonth.strftime('%Y-%m')}",
        sender="your_email@gmail.com",
        recipients=[user.email]
    )

    msg.html = render_template('email_template.html', emp=emp, salary=salary)
    mail.send(msg)

    return f"Đã gửi bảng lương cho {emp.FullName} qua email {user.email}"

@app.route('/gui-email-toan-bo')
def gui_email_toan_bo():
    employees = EmployeeSQL.query.all() + EmployeeMySQL.query.all()
    users = {u.user_id: u for u in User.query.all()}
    count = 0

    for emp in employees:
        user = users.get(emp.EmployeeID)
        if not user or not user.email:
            continue

        salary = SalarySQL.query.filter_by(EmployeeID=emp.EmployeeID).order_by(SalarySQL.SalaryMonth.desc()).first()
        if not salary:
            continue

        msg = Message(
            subject=f"[PAYROLL] Bảng lương tháng {salary.SalaryMonth.strftime('%Y-%m')}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.html = f"""
        <p>Chào {emp.FullName},</p>
        <p>Lương tháng {salary.SalaryMonth.strftime('%Y-%m')}:</p>
        <ul>
          <li>Lương cơ bản: {salary.BaseSalary:,.0f} VND</li>
          <li>Thưởng: {salary.Bonus:,.0f} VND</li>
          <li>Khấu trừ: {salary.Deductions:,.0f} VND</li>
          <li><strong>Lương thực nhận: {salary.NetSalary:,.0f} VND</strong></li>
        </ul>
        <p>Phòng Nhân sự</p>
        """
        try:
            mail.send(msg)
            count += 1
        except Exception as e:
            continue

    return f"✅ Đã gửi email cho {count} nhân viên."

@app.route('/gui-email-da-chon', methods=['POST'])
def gui_email_da_chon():
    data = request.get_json()
    ids = data.get("ids", [])
    users = {u.user_id: u for u in User.query.all()}
    count = 0

    for eid in ids:
        eid = int(eid)
        emp = EmployeeSQL.query.get(eid) or EmployeeMySQL.query.get(eid)
        user = users.get(eid)
        if not emp or not user or not user.email:
            continue

        salary = SalarySQL.query.filter_by(EmployeeID=eid).order_by(SalarySQL.SalaryMonth.desc()).first()
        if not salary:
            continue

        msg = Message(
            subject=f"[PAYROLL] Bảng lương tháng {salary.SalaryMonth.strftime('%Y-%m')}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.html = f"""
        <p>Chào {emp.FullName},</p>
        <p>Bảng lương tháng {salary.SalaryMonth.strftime('%Y-%m')}:</p>
        <ul>
          <li>Lương cơ bản: {salary.BaseSalary:,.0f} VND</li>
          <li>Thưởng: {salary.Bonus:,.0f} VND</li>
          <li>Khấu trừ: {salary.Deductions:,.0f} VND</li>
          <li><strong>Lương thực nhận: {salary.NetSalary:,.0f} VND</strong></li>
        </ul>
        <p>Trân trọng,<br>Phòng Nhân sự</p>
        """
        try:
            mail.send(msg)
            count += 1
        except:
            continue

    return f"✅ Đã gửi email cho {count} nhân viên được chọn."

@app.route('/chuc-vu/<int:id>/nhan-vien')
def get_employees_by_position(id):
    employees = EmployeeSQL.query.filter(EmployeeSQL.PositionID == id).all()
    result = [{
        "id": emp.EmployeeID,
        "name": emp.FullName,
        "department": emp.Department.name if emp.Department else "Không rõ",
        "status": emp.Status
    } for emp in employees]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)