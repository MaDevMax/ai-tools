from flask import Flask, request, session, redirect
import requests
import os
import time
import re

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET"

FREE_LIMIT = 5
SUB_PRICE = 299


# =========================================================
# 🧠 CLEAN TEXT
# =========================================================
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    return text


# =========================================================
# 🤖 AI
# =========================================================
def ask_ai(prompt):
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        return clean_text(r.json()["choices"][0]["message"]["content"])

    except Exception as e:
        return f"AI ERROR: {str(e)}"


# =========================================================
# 💳 SUB STATUS
# =========================================================
def is_pro():
    return session.get("sub_status") == "active" and time.time() < session.get("sub_end", 0)


def can_use():
    return is_pro() or session.get("used", 0) < FREE_LIMIT


def add_use():
    if not is_pro():
        session["used"] = session.get("used", 0) + 1


# =========================================================
# 🎨 UI WRAPPER
# =========================================================
def page(title, content):

    used = session.get("used", 0)
    pro = is_pro()

    return f"""
<html>
<head>
<title>{title}</title>

<style>
body {{
    font-family: Arial;
    margin:0;
    background:#f4f6fb;
}}

.container {{
    width: 900px;
    margin: 30px auto;
    background: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

.nav {{
    display:flex;
    gap:10px;
    margin-bottom:20px;
}}

.nav a {{
    text-decoration:none;
    padding:10px 15px;
    background:#eee;
    border-radius:8px;
    color:#333;
}}

.nav a:hover {{
    background:#ddd;
}}

.hero {{
    background: linear-gradient(90deg,#111,#333);
    color:white;
    padding:20px;
    border-radius:14px;
}}

input, textarea, select {{
    width:100%;
    margin-top:10px;
    padding:12px;
    border-radius:8px;
    border:1px solid #ddd;
}}

button {{
    background:#2d6cdf;
    color:white;
    border:none;
    padding:12px;
    border-radius:8px;
    cursor:pointer;
}}

.result {{
    margin-top:15px;
    background:#f7f7f7;
    padding:15px;
    border-radius:10px;
    white-space:pre-wrap;
    border-left:4px solid #2d6cdf;
}}
</style>

</head>

<body>

<div class="container">

<div class="nav">
<a href="/">🏠 Home</a>
<a href="/wb">📦 WB/Ozon</a>
<a href="/avito">📢 Avito</a>
<a href="/pro">💎 Pro</a>
</div>

<div class="hero">
<h2>🚀 AI SaaS Builder</h2>
<p>{"💎 PRO ACTIVE" if pro else "🆓 FREE MODE"}</p>
<p>Free left: {max(FREE_LIMIT - used, 0)}</p>
</div>

{content}

</div>

</body>
</html>
"""


# =========================================================
# 🏠 HOME
# =========================================================
@app.route("/")
def home():
    return page("Home", """
<h2>🔥 AI сервис для карточек товаров</h2>
<p>Маркетинг уровня агентства в одном инструменте</p>
""")


# =========================================================
# 📦 WB / OZON
# =========================================================
@app.route("/wb", methods=["GET", "POST"])
def wb():

    result = ""

    if request.method == "POST":

        if not can_use():
            return page("BLOCKED", """
<h2>❌ Лимит исчерпан</h2>
<a href="/pro"><button>💎 Купить Pro 299₽</button></a>
""")

        product = request.form.get("product")
        features = request.form.get("features")

        if not is_pro():
            mode = "free"
        else:
            mode = "pro"

        if mode == "pro":
            prompt = f"""
Ты топ маркетолог.

ТОВАР: {product}
{features}
"""
        else:
            prompt = f"""
Базовое описание товара.

ТОВАР: {product}
{features}
"""

        result = ask_ai(prompt)
        add_use()

    return page("WB", f"""
<h2>📦 WB / Ozon генератор</h2>

<form method="POST">

<input name="product" placeholder="Название товара" required>
<textarea name="features" placeholder="Описание" required></textarea>

<button>Сгенерировать</button>

</form>

<div class="result">{result}</div>
""")


# =========================================================
# 📢 AVITO (ВКЛАДКА ВЕРНУЛАСЬ)
# =========================================================
@app.route("/avito", methods=["GET", "POST"])
def avito():

    result = ""

    if request.method == "POST":

        if not can_use():
            return page("BLOCKED", """
<h2>❌ Лимит исчерпан</h2>
<a href="/pro"><button>💎 Pro</button></a>
""")

        product = request.form.get("product")
        features = request.form.get("features")

        if not is_pro():
            prompt = f"простое объявление: {product} {features}"
        else:
            prompt = f"""
Ты эксперт Avito продаж.

Сделай сильное объявление:
ТОВАР: {product}
{features}
"""
        result = ask_ai(prompt)
        add_use()

    return page("Avito", f"""
<h2>📢 Avito генератор</h2>

<form method="POST">
<input name="product" placeholder="Товар" required>
<textarea name="features" placeholder="Описание" required></textarea>
<button>Сгенерировать</button>
</form>

<div class="result">{result}</div>
""")


# =========================================================
# 💎 PRO PAGE
# =========================================================
@app.route("/pro")
def pro():
    return page("Pro", f"""
<h2>💎 Pro подписка</h2>

<p>Все вкладки + мощные тексты</p>

<h3>{SUB_PRICE} ₽ / месяц</h3>

<a href="/fake-pay"><button>Купить</button></a>
""")


# =========================================================
# 💳 FAKE PAY (ПОТОМ YOOKASSA)
# =========================================================
@app.route("/fake-pay")
def fake_pay():

    session["sub_status"] = "active"
    session["sub_end"] = time.time() + 30 * 24 * 60 * 60
    session["used"] = 0

    return redirect("/")


# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)