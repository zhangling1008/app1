import pymysql
from config import DB_CONFIG


def init_database():
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )

    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS d06 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE d06")

            # 读取schema.sql
            with open('database/schema.sql', 'r') as f:
                sql_script = f.read()

            # 执行建表语句
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)

        connection.commit()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
    finally:
        connection.close()


if __name__ == "__main__":
    init_database()