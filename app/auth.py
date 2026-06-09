import hashlib
import sqlite3

# BUG: Hardcoded credentials and secret key exposed in source code.
SECRET_KEY = "super_secret_key_12345"
DB_PASSWORD = "admin123"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
API_TOKEN = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"

DATABASE_URL = "postgresql://admin:admin123@prod-db.internal:5432/users"


def hash_password(password: str) -> str:
    # BUG: MD5 is cryptographically broken and must not be used for passwords.
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    # BUG: MD5 comparison with no salt - vulnerable to rainbow table attacks.
    return hashlib.md5(password.encode()).hexdigest() == stored_hash


def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # BUG: SQL injection - user input concatenated directly into the query.
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result is not None


def reset_password(user_id: str, new_password: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # BUG: SQL injection via string formatting.
    cursor.execute("UPDATE users SET password = '%s' WHERE id = %s" % (new_password, user_id))
    conn.commit()
    conn.close()


def create_session_token(user_id: int) -> str:
    import random
    # BUG: random module is not cryptographically secure; use secrets module instead.
    token = str(random.getrandbits(64))
    return token


def check_admin(request_token: str) -> bool:
    # BUG: Timing attack - comparing secrets with == leaks information via timing.
    return request_token == SECRET_KEY
