# SQL_SERVER_CONN = "mssql+pyodbc://@MSI/SQLEXPRESS01/HUMAN_BAITAP?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# MYSQL_CONN = "mysql+mysqlconnector://root:Thanh123+@localhost/payroll_baitap"
from sqlalchemy import create_engine

# Chuỗi kết nối SQL Server
SQL_SERVER_CONN = "mssql+pyodbc://thanh:12@MSI\SQLEXPRESS01/HUMAN_BAITAP?driver=ODBC+Driver+17+for+SQL+Server"
# Chuỗi kết nối MySQL
MYSQL_CONN = "mysql+mysqlconnector://root:Thanh123+@localhost/payroll_baitap"

# Hàm kiểm tra kết nối
def check_connection(db_url, db_name):
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print(f"✅ Kết nối thành công tới {db_name}!")
        return True
    except Exception as e:
        print(f"❌ Lỗi kết nối tới {db_name}: {e}") 
        return False

# Kiểm tra kết nối SQL Server
sql_server_status = check_connection(SQL_SERVER_CONN, "SQL Server")

# Kiểm tra kết nối MySQL
mysql_status = check_connection(MYSQL_CONN, "MySQL")

# Nếu cả hai kết nối đều thành công
if sql_server_status and mysql_status:
    print("🎉 Cả hai kết nối đều thành công!")
elif sql_server_status:
    print("⚠️ Kết nối SQL Server thành công, nhưng MySQL thất bại.")
elif mysql_status:
    print("⚠️ Kết nối MySQL thành công, nhưng SQL Server thất bại.")
else:
    print("❌ Cả hai kết nối đều thất bại!")

