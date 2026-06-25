from flask import Flask, render_template, request, redirect, session
import time
from werkzeug.security import generate_password_hash, check_password_hash

from db import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_usage,
    activate_pro,
    save_generation,
    get_generations,
    get_stats
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"

FREE_LIMIT = 5

init_db()


# =========================
# HELPERS
# =========================

def current_user():
    uid = session.get("user_id")

    if not uid:
        return None

    return get_user_by_id(uid)


def is_pro(user):
    return user and user["plan"] == "pro" and user["sub_end"] > int(time.time())


def can_use(user):
    return user and (is_pro(user) or user["used"] < FREE_LIMIT)


# =========================
# HOME
# =========================

@app.route("/")
def home():

    if current_user():
        return redirect("/dashboard")

    return render_template("home.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template(
                "register.html",
                error="Fill all fields"
            )

        if get_user_by_email(email):
            return render_template(
                "register.html",
                error="User already exists"
            )

        create_user(
            email,
            generate_password_hash(password)
        )

        user = get_user_by_email(email)

        session["user_id"] = user["id"]

        return redirect("/dashboard")

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        if not user:
            return render_template(
                "login.html",
                error="User not found"
            )

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return render_template(
                "login.html",
                error="Wrong password"
            )

        session["user_id"] = user["id"]

        return redirect("/dashboard")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    user = current_user()

    if not user:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=user,
        stats=get_stats()
    )


# =========================
# WB
# =========================

@app.route("/wb", methods=["GET", "POST"])
def wb():

    user = current_user()

    if not user:
        return redirect("/login")

    result = ""

    if request.method == "POST":

        if not can_use(user):
            return redirect("/pro")

        product = request.form.get("product")
        features = request.form.get("features")

        result = f"""
WB DESCRIPTION FOR:

{product}

{features}

🔥 GENERATED SELLING TEXT
"""

        if not is_pro(user):
            update_usage(
                user["id"],
                user["used"] + 1
            )

        save_generation(
            user["id"],
            "WB",
            product,
            result
        )

    return render_template(
        "wb.html",
        result=result
    )


# =========================
# AVITO
# =========================

@app.route("/avito", methods=["GET", "POST"])
def avito():

    user = current_user()

    if not user:
        return redirect("/login")

    result = ""

    if request.method == "POST":

        if not can_use(user):
            return redirect("/pro")

        product = request.form.get("product")
        features = request.form.get("features")

        result = f"""
AVITO AD FOR:

{product}

{features}

🚀 READY AD TEXT
"""

        if not is_pro(user):
            update_usage(
                user["id"],
                user["used"] + 1
            )

        save_generation(
            user["id"],
            "AVITO",
            product,
            result
        )

    return render_template(
        "avito.html",
        result=result
    )


# =========================
# PRO
# =========================

@app.route("/pro")
def pro():

    return render_template("pro.html")


# =========================
# PAY
# =========================

@app.route("/pay")
def pay():

    user = current_user()

    if not user:
        return redirect("/login")

    return render_template("pay_pending.html")


# =========================
# MOCK PAYMENT SUCCESS
# =========================

@app.route("/pay-success")
def pay_success():

    user = current_user()

    if not user:
        return redirect("/login")

    activate_pro(
        user["id"],
        int(time.time()) + 30 * 24 * 60 * 60
    )

    return redirect("/dashboard")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)