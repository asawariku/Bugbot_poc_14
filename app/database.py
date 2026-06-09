import sqlite3
import os
import subprocess


def get_user_by_name(username: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: SQL injection - unsanitised user input concatenated into query.
    query = "SELECT id, email, role FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


def get_orders_by_status(status: str, user_id: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: SQL injection via % string formatting.
    query = "SELECT * FROM orders WHERE status = '%s' AND user_id = %s" % (status, user_id)
    cursor.execute(query)
    return cursor.fetchall()


def search_products(keyword: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: SQL injection - f-string interpolation into SQL query.
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{keyword}%'")
    return cursor.fetchall()


def delete_user(user_id: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: SQL injection - no parameterised query for a destructive operation.
    cursor.execute("DELETE FROM users WHERE id = " + user_id)
    conn.commit()


def export_user_report(username: str):
    # BUG: OS command injection - unsanitised username passed into shell command.
    os.system("mysqldump app users --where=\"username='" + username + "'\" > /tmp/report.sql")


def run_db_backup(db_name: str):
    # BUG: Command injection via subprocess with shell=True and user-controlled input.
    subprocess.call("pg_dump " + db_name + " > /backup/db.sql", shell=True)
