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

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

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


class EmployeeMySQL(db.Model):
    __bind_key__ = 'mysql'
    __tablename__ = "employees"

    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer)
    PositionID = db.Column(db.Integer)
    Status = db.Column(db.String(50))

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


class EmployeeSQL(db.Model):
    __tablename__ = "employees"
    __bind_key__ = "default"

    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer, db.ForeignKey("departments.DepartmentID"))
    PositionID = db.Column(db.Integer, db.ForeignKey("positions.PositionID"))
    Status = db.Column(db.String(50))

    department = db.relationship("DepartmentSQL", backref="employees")
    position = db.relationship("PositionSQL", backref="employees")


class AttendanceMySQL(db.Model):
    __tablename__ = "attendance"
    __bind_key__ = "mysql"

    AttendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer)
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

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

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


@app.route('/', methods=['GET'])
def login():
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
            "Status": nv.Status
        }

    return render_template(
        "quan_li_nhan_su.html",
        nhan_viens=list(nhan_viens.values()),
        departments=unique_deps,
        positions=unique_pos,
        roles=roles,  # 👈 Truyền danh sách role vào template
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
    username = request.form["username"]  # thêm trường username
    password = request.form["password"]  # thêm trường password

    # Thêm nhân viên SQL Server
    engine_sqlserver = db.get_engine(app, bind='default')
    with engine_sqlserver.begin() as conn:
        conn.execute(text("SET IDENTITY_INSERT employees ON"))
        conn.execute(
            text(
                """
                INSERT INTO employees
                (EmployeeID, FullName, DepartmentID, PositionID, Status)
                VALUES
                (:id, :name, :dep, :pos, :st)
                """
            ),
            {
                "id": employee_id,
                "name": full_name,
                "dep": department_id,
                "pos": position_id,
                "st": status,
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
    )
    db.session.add(nv_mysql)

    # Thêm user mới
    user = User(
        user_id=employee_id,  # nếu user_id trùng EmployeeID
        username=username,
        password=password,  # Có thể hash password nếu muốn
        role_id=role_id,  # vd: 3 là HR, bạn chỉnh theo role_id bạn muốn cấp
        email=None,
        phone_number=None,
        address=None,
        birth_date=None,
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

    # phần mở rộng thêm
    username = request.form.get("username")
    password = request.form.get("password")
    role_id = request.form.get("role_id")

    if not nv_sql and not nv_mysql:
        return "Không tìm thấy nhân viên", 404

    if nv_sql:
        nv_sql.FullName = full_name
        nv_sql.DepartmentID = department_id
        nv_sql.PositionID = position_id
        nv_sql.Status = status

    if nv_mysql:
        nv_mysql.FullName = full_name
        nv_mysql.DepartmentID = department_id
        nv_mysql.PositionID = position_id
        nv_mysql.Status = status

    # Cập nhật tài khoản nếu có
    if user:
        user.username = username
        if password:
            user.password = password
        user.role_id = role_id
        db.session.add(user)  # Thêm dòng này nếu cần
    else:
        new_user = User(
            user_id=ma_nv,
            username=username,
            password=password,
            role_id=role_id,
            email=None,
            phone_number=None,
            address=None,
            birth_date=None
        )
        db.session.add(new_user)


    db.session.commit()
    return redirect(url_for("quan_li_nhan_su"))


@app.route("/xoa-nhan-vien/<int:ma_nv>")
def xoa_nhan_vien(ma_nv):
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

    # ——— Phòng ban ———
    # SQL Server
    deps_sql = DepartmentSQL.query.all()
    # MySQL
    deps_mysql = DepartmentMySQL.query.all()
    # Gộp
    depts = [
        {"id": d.DepartmentID, "name": d.DepartmentName, "source": "HUMAN_2025"}
        for d in deps_sql
    ]
    # ——— Chức vụ ———
    pos_sql = PositionSQL.query.all()
    pos_mysql = PositionMySQL.query.all()
    poses = [
        {"id": p.PositionID, "name": p.PositionName, "source": "HUMAN_2025"}
        for p in pos_sql
    ]
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

    # Báo cáo nhân sự
    bao_cao_nhan_su_sql = (
        db.session.query(
            DepartmentSQL.DepartmentName.label("dept"),
            db.func.count(EmployeeSQL.EmployeeID).label("total"),
            db.func.sum(db.case((EmployeeSQL.Status == "Đang làm", 1), else_=0)).label(
                "danglam"
            ),
            db.func.sum(db.case((EmployeeSQL.Status == "Nghỉ việc", 1), else_=0)).label(
                "nghiviec"
            ),
        )
        .join(EmployeeSQL, DepartmentSQL.DepartmentID == EmployeeSQL.DepartmentID)
        .group_by(DepartmentSQL.DepartmentName)
        .all()
    )
    bao_cao_nhan_su_mysql = (
        db.session.query(
            DepartmentMySQL.DepartmentName.label("dept"),
            db.func.count(EmployeeMySQL.EmployeeID).label("total"),
            db.func.sum(db.case((EmployeeMySQL.Status == "Đang làm", 1), else_=0)).label(
                "danglam"
            ),
            db.func.sum(db.case((EmployeeMySQL.Status == "Nghỉ việc", 1), else_=0)).label(
                "nghiviec"
            ),
        )
        .join(EmployeeMySQL, DepartmentMySQL.DepartmentID == EmployeeMySQL.DepartmentID)
        .group_by(DepartmentMySQL.DepartmentName)
        .all()
    )

    # Báo cáo lương
    bao_cao_luong_sql = (
        db.session.query(
            DepartmentSQL.DepartmentName.label("dept"),
            db.func.sum(SalarySQL.NetSalary).label("total_salary"),
            db.func.avg(SalarySQL.NetSalary).label("avg_salary"),
            db.func.max(SalarySQL.SalaryMonth).label("latest_month"),
        )
        .join(EmployeeSQL, DepartmentSQL.DepartmentID == EmployeeSQL.DepartmentID)
        .join(SalarySQL, SalarySQL.EmployeeID == EmployeeSQL.EmployeeID)
        .group_by(DepartmentSQL.DepartmentName)
        .all()
    )
    bao_cao_luong_mysql = (
        db.session.query(
            DepartmentMySQL.DepartmentName.label("dept"),
            db.func.sum(SalaryMySQL.NetSalary).label("total_salary"),
            db.func.avg(SalaryMySQL.NetSalary).label("avg_salary"),
            db.func.max(SalaryMySQL.SalaryMonth).label("latest_month"),
        )
        .join(EmployeeMySQL, DepartmentMySQL.DepartmentID == EmployeeMySQL.DepartmentID)
        .join(SalaryMySQL, SalaryMySQL.EmployeeID == EmployeeMySQL.EmployeeID)
        .group_by(DepartmentMySQL.DepartmentName)
        .all()
    )

    return render_template(
        "bao_cao_tai_chinh.html",
        ns_sql=bao_cao_nhan_su_sql,
        ns_mysql=bao_cao_nhan_su_mysql,
        luong_sql=bao_cao_luong_sql,
        luong_mysql=bao_cao_luong_mysql,
        role=role,
        user_permissions=user_permissions,
    )


@app.route("/ho_so", methods=["GET", "POST"])
def ho_so():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    employee_id = session.get("employee_id")  # Lấy employee_id của người đang đăng nhập

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
    if "logged_in" not in session or session.get("role") != "EMP":
        return redirect(url_for("login"))

    employee_id = session.get("employee_id")
    if not employee_id:
        flash("Không tìm thấy mã nhân viên.", "danger")
        return redirect(url_for("ho_so"))

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


@app.route("/cai-dat", methods=["GET", "POST"])
def cai_dat():
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
    if request.method == "POST":
        # Cập nhật cài đặt nếu có
        return redirect(url_for("cai_dat"))
    return render_template("cai_dat.html", role=role, user_permissions=user_permissions)

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

    employees_sql = EmployeeSQL.query.all()
    employees_mysql = EmployeeMySQL.query.all()
    all_employees = employees_sql + employees_mysql

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

    # 4. Danh sách email đã gửi (giả định)
    ds_email_gui_luong = []  # Cần tích hợp email gửi thực tế nếu có

    return render_template("canh_bao_thong_bao.html",
                           thong_bao_ky_niem=thong_bao_ky_niem,
                           vuot_ngay_phep=vuot_ngay_phep,
                           gioi_han_phep=gioi_han_phep,
                           chenh_lech_luong=chenh_lech_luong,
                           ds_email_gui_luong=ds_email_gui_luong,
                           role=role,
                           user_permissions=user_permissions)


@app.route("/dashboard")
def dashboard():
    if "logged_in" not in session:
        return redirect(url_for("login"))  # Kiểm tra đăng nhập

    role = session.get("role")  # Lấy vai trò từ session
    username = session.get("username")  # Lấy tên người dùng từ session

    return render_template("index.html", role=role, username=username)  # Truyền vai trò và tên người dùng vào template


@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Tìm người dùng từ bảng User
    user = User.query.filter_by(username=username).first()

    # Kiểm tra mật khẩu và nếu đúng, lưu thông tin vào session
    if user and user.password == password:
        session["logged_in"] = True
        session["role"] = user.role.role_code
        session["username"] = user.username
        session["email"] = user.email
        session["phone_number"] = user.phone_number
        session["address"] = user.address
        session["birth_date"] = user.birth_date

        session["employee_id"] = user.user_id  # ✅ Quan trọng: lưu mã nhân viên để lấy thông tin chi tiết

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
    # ✅ Lấy dữ liệu nhân viên từ cả SQL Server và MySQL
    emps_sql = EmployeeSQL.query.all()
    emps_mysql = EmployeeMySQL.query.all()

    # ✅ Ưu tiên bản SQL nếu bị trùng EmployeeID
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
            "Trạng Thái": emp.Status
        })

    # ✅ Xuất ra Excel
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
    # Lấy dữ liệu lương (2 bảng)
    salaries_sql = SalarySQL.query.all()
    salaries_mysql = SalaryMySQL.query.all()
    salaries = salaries_sql + salaries_mysql

    # Lấy dữ liệu chấm công (2 bảng)
    attendance_sql = AttendanceSQL.query.all()
    attendance_mysql = AttendanceMySQL.query.all()
    attendances = attendance_sql + attendance_mysql

    # Chuyển sang DataFrame - bảng lương
    df_luong = pd.DataFrame([{
        "Mã Lương": s.SalaryID,
        "Mã NV": s.EmployeeID,
        "Tháng": s.SalaryMonth.strftime("%Y-%m") if s.SalaryMonth else "",
        "Lương Cơ Bản": s.BaseSalary,
        "Thưởng": s.Bonus,
        "Khấu Trừ": s.Deductions,
        "Lương Thực Nhận": s.NetSalary,
        "Ngày Tạo": s.SalaryCreated.strftime("%d/%m/%Y %H:%M") if hasattr(s, 'SalaryCreated') and s.SalaryCreated else ""
    } for s in salaries])

    # Chuyển sang DataFrame - bảng chấm công
    df_cc = pd.DataFrame([{
        "Mã NV": c.EmployeeID,
        "Tháng": c.AttendanceMonth.strftime("%Y-%m") if c.AttendanceMonth else "",
        "Ngày Làm Việc": c.WorkDays,
        "Ngày Vắng": c.AbsentDays,
        "Ngày Nghỉ Phép": c.LeaveDays
    } for c in attendances])

    # Xuất file Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_luong.to_excel(writer, index=False, sheet_name="Luong")
        df_cc.to_excel(writer, index=False, sheet_name="ChamCong")

    output.seek(0)
    return send_file(output, download_name="luong_cham_cong.xlsx", as_attachment=True)

@app.route("/xuat-bao-cao")
def xuat_bao_cao():
    # Lấy nhân viên từ SQL + MySQL
    employees_sql = EmployeeSQL.query.all()
    employees_mysql = EmployeeMySQL.query.all()
    all_employees = employees_sql + employees_mysql

    # Lấy lương từ SQL + MySQL
    salaries_sql = SalarySQL.query.all()
    salaries_mysql = SalaryMySQL.query.all()
    all_salaries = salaries_sql + salaries_mysql

    # Lấy thông tin phòng ban
    deps_sql = DepartmentSQL.query.all()
    deps_mysql = DepartmentMySQL.query.all()
    all_deps = {d.DepartmentID: d.DepartmentName for d in deps_sql + deps_mysql}

    # --- Báo cáo nhân sự ---
    nhan_su = {}
    for emp in all_employees:
        dept_name = all_deps.get(emp.DepartmentID, "N/A")
        if dept_name not in nhan_su:
            nhan_su[dept_name] = {"Tổng NV": 0, "Đang Làm": 0, "Nghỉ Việc": 0}
        nhan_su[dept_name]["Tổng NV"] += 1
        if emp.Status == "Đang làm":
            nhan_su[dept_name]["Đang Làm"] += 1
        else:
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

    # --- Báo cáo lương ---
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
            "Tổng Lương": v["Tổng Lương"],
            "Lương Trung Bình": int(v["Tổng Lương"] / v["Số Người"]) if v["Số Người"] else 0,
            "Tháng Gần Nhất": v["Tháng Gần Nhất"].strftime("%Y-%m") if v["Tháng Gần Nhất"] else ""
        }
        for k, v in luong.items()
    ])

    # --- Xuất Excel ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_nhansu.to_excel(writer, index=False, sheet_name='NhanSu')
        df_luong.to_excel(writer, index=False, sheet_name='Luong')

    output.seek(0)
    return send_file(output, download_name="bao_cao_thong_ke.xlsx", as_attachment=True)

@app.route("/dang-xuat")
def dang_xuat():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)