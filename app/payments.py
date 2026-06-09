from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# BUG: Hardcoded payment gateway credentials in source code.
STRIPE_SECRET_KEY = "sk_live_HARDCODED_DO_NOT_USE_abc123xyz"
PAYPAL_CLIENT_SECRET = "HARDCODED_PAYPAL_SECRET_DO_NOT_USE_abc123"


def get_balance(user_id: int) -> float:
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # BUG: SQL injection - user_id is an integer from user input but never validated.
    cursor.execute("SELECT balance FROM accounts WHERE user_id = " + str(user_id))
    row = cursor.fetchone()
    return row[0] if row else 0.0


@app.route("/transfer", methods=["POST"])
def transfer_funds():
    sender_id = request.json.get("sender_id")
    receiver_id = request.json.get("receiver_id")
    amount = request.json.get("amount")

    # BUG: No authentication check - any caller can initiate a transfer.
    # BUG: No authorization check - sender_id is not verified against the logged-in user.
    # BUG: Negative amount not rejected - attacker can transfer a negative value to
    #      increase their own balance (business logic flaw).
    # BUG: Race condition - balance is read and written in separate queries with no
    #      locking, allowing a double-spend via concurrent requests.
    balance = get_balance(sender_id)

    if balance >= amount:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
            (amount, sender_id),
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE user_id = ?",
            (amount, receiver_id),
        )
        conn.commit()
        return jsonify({"status": "transferred"})

    return jsonify({"error": "Insufficient funds"}), 400


@app.route("/apply-coupon", methods=["POST"])
def apply_coupon():
    coupon_code = request.json.get("code")
    order_id = request.json.get("order_id")
    user_id = request.json.get("user_id")

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: SQL injection via f-string in coupon lookup.
    cursor.execute(f"SELECT discount FROM coupons WHERE code = '{coupon_code}'")
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Invalid coupon"}), 400

    discount = row[0]

    # BUG: No check that the coupon has already been used - allows unlimited reuse.
    # BUG: No check that coupon belongs to this user or order.
    cursor.execute(
        "UPDATE orders SET discount = ? WHERE id = ?",
        (discount, order_id),
    )
    conn.commit()
    return jsonify({"discount": discount})


@app.route("/refund", methods=["POST"])
def refund():
    order_id = request.json.get("order_id")
    amount = request.json.get("amount")

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # BUG: No check that the order belongs to the requesting user (IDOR).
    # BUG: No check that the refund amount does not exceed the original payment.
    # BUG: No check that a refund for this order hasn't already been issued.
    cursor.execute(
        "UPDATE accounts SET balance = balance + ? WHERE user_id = "
        "(SELECT user_id FROM orders WHERE id = ?)",
        (amount, order_id),
    )
    conn.commit()
    return jsonify({"refunded": amount})


@app.route("/withdraw", methods=["POST"])
def withdraw():
    user_id = request.json.get("user_id")
    amount = request.json.get("amount")

    # BUG: No input type validation - amount could be a string or None, causing
    # silent failures or incorrect comparisons.
    balance = get_balance(user_id)

    # BUG: Integer vs float comparison without rounding - floating point precision
    # issues can allow withdrawals of fractionally more than the balance.
    if balance >= amount:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id),
        )
        conn.commit()
        return jsonify({"withdrawn": amount})

    return jsonify({"error": "Insufficient funds"}), 400
