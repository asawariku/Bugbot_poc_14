from flask import Flask, request, session, redirect, make_response, jsonify
import hashlib
import time

app = Flask(__name__)

# BUG: Hardcoded Flask secret key - session cookies are trivially forged.
app.secret_key = "dev_secret"


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "admin":
        # BUG: Session fixation - session ID is never regenerated after login,
        # so an attacker who plants a session ID can hijack the authenticated session.
        session["user"] = username
        session["role"] = "admin"
        return redirect("/dashboard")

    return "Invalid credentials", 401


@app.route("/set-cookie")
def set_cookie():
    resp = make_response("Cookie set")
    user = request.args.get("user", "guest")

    # BUG: Cookie set without HttpOnly - accessible to JavaScript, enabling XSS theft.
    # BUG: Cookie set without Secure - transmitted over HTTP in plaintext.
    # BUG: Cookie set without SameSite - vulnerable to CSRF.
    resp.set_cookie("session_user", user)
    return resp


@app.route("/remember-me")
def remember_me():
    user_id = request.args.get("uid")

    # BUG: Persistent cookie stores user ID in plaintext - no integrity check.
    # BUG: Very long max_age (10 years) increases exposure window.
    resp = make_response("Remembered")
    resp.set_cookie("uid", user_id, max_age=315360000)
    return resp


@app.route("/dashboard")
def dashboard():
    # BUG: No CSRF protection on a state-changing endpoint.
    # BUG: Role is read from the cookie/session without re-validation server-side.
    role = session.get("role")
    if role != "admin":
        return "Forbidden", 403
    return "Admin Dashboard"


@app.route("/change-email", methods=["POST"])
def change_email():
    # BUG: No CSRF token check - any site can trigger this action on behalf of a
    # logged-in user by submitting a cross-origin form.
    new_email = request.form.get("email")
    session["email"] = new_email
    return jsonify({"updated": new_email})


def generate_session_id(user_id: int) -> str:
    # BUG: Session ID derived from predictable values (user_id + timestamp);
    # an attacker who knows the rough login time can brute-force the token.
    raw = f"{user_id}{int(time.time())}"
    return hashlib.md5(raw.encode()).hexdigest()
