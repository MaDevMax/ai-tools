"""
🔥 AI SaaS PRODUCT BUILDER
Subscription-based version (Stripe-ready)
"""

from flask import Flask, request, session, redirect
import requests
import os
import time
import re

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SUPER_SECRET"

FREE_LIMIT = 5


# =========================================================
# 🧠 CLEAN OUTPUT (premium text)
# =========================================================
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    return text


# =========================================================
# 🤖 AI CALL
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
# 💳 SUBSCRIPTION SYSTEM (КЛЮЧЕВОЕ)
# =========================================================

def is_sub_active():
    """
    Проверка подписки:
    - есть статус active
    - не истек срок
    """

    if session.get("subscription_status") != "active":
        return False

    end_time = session.get("subscription_end", 0)

    if time.time() > end_time:
        session["subscription_status"] = "expired"
        return False

    return True


def can_use():
    """
    Можно использовать если:
    - активная подписка
    ИЛИ
    - не превышен free лимит
    """

    if is_sub_active():
        return True

    return session.get("used", 0) < FREE_LIMIT


def add_use():
    if not is_sub_active():
        session["used"] = session.get("used", 0) + 1


# =========================================================
# 🎨 UI WRAPPER
# =========================================================
def page(title, content):

    used = session.get("used", 0)
    sub = is_sub_active()

    status = "💎 ACTIVE SUBSCRIPTION" if sub else "🆓 FREE MODE"

    return f"""
<html>
<head>
<title>{title}</title>

<style>
body {{
    font-family: Arial;
    margin:0;
    background: linear-gradient(120deg, #f4f4f4, #e9eef7);
}}

.container {{
    width: 860px;
    margin: 40px auto;
    background: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

nav a {{
    margin-right: 12px;
    text-decoration: none;
    font-weight: bold;
    color: #2d6cdf;
}}

.hero {{
    background: linear-gradient(90deg, #111, #333);
    color: white;
    padding: 20px;
    border-radius: 14px;
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

<script>
function showLoading() {{
    document.getElementById("loading").style.display = "block";
}}
</script>

</head>

<body>

<div class="container">

<nav>
<a href="/">Home</a>
<a href="/wb">WB/Ozon</a>
<a href="/subscribe">Subscribe</a>
</nav>

<div class="hero">
<h2>🚀 AI SaaS Product Builder</h2>
<p>Status: <b>{status}</b></p>
<p>Free uses left: <b>{max(FREE_LIMIT - used, 0)}</b></p>
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
<h2>🔥 AI генератор карточек товаров</h2>
<p>Подписка открывает безлимит генераций</p>
<a href="/wb"><button>Start</button></a>
""")


# =========================================================
# 🛒 GENERATOR
# =========================================================
@app.route("/wb", methods=["GET", "POST"])
def wb():

    result = ""

    if request.method == "POST":

        if not can_use():
            return page("BLOCKED", """
<h2>❌ Доступ закрыт</h2>
<p>Нужна активная подписка</p>
<a href="/subscribe"><button>Подписаться</button></a>
""")

        product = request.form.get("product")
        features = request.form.get("features")
        mode = request.form.get("mode")

        if mode == "boost":
            prompt = f"""
Ты маркетолог Apple уровня.

ТОВАР: {product}
{features}

ФОРМАТ:
🔥 Заголовок
✨ Описание
💎 Преимущества
⚡ Срочность
📈 Продажи
"""

        elif mode == "pro":
            prompt = f"""
Профессиональный маркетинг.

ТОВАР: {product}
{features}
"""

        else:
            prompt = f"""
Обычное описание.

ТОВАР: {product}
{features}
"""

        result = ask_ai(prompt)
        add_use()

    return page("WB", f"""
<h2>Generator</h2>

<form method="POST" onsubmit="showLoading()">

<input name="product" placeholder="Product name" required>
<textarea name="features" placeholder="Features" required></textarea>

<select name="mode">
<option value="free">Free</option>
<option value="pro">Pro</option>
<option value="boost">Boost</option>
</select>

<button>Generate</button>

<div id="loading" style="display:none;">⏳ Generating...</div>

</form>

<div class="result">{result}</div>
""")


# =========================================================
# 💳 SUBSCRIPTION PAGE (ЗАГОТОВКА ПОД STRIPE)
# =========================================================
@app.route("/subscribe")
def subscribe():

    return page("Subscribe", """
<h2>💳 Подписка PRO</h2>

<p>Безлимит генераций + Boost режим</p>

<h3>Plan: 9.99€ / month</h3>

<!-- 🔥 СЮДА ПОДКЛЮЧАЕМ STRIPE -->
<a href="/fake-pay"><button>Subscribe now</button></a>

<hr>

<p>⚠️ В реальном проекте здесь будет Stripe Checkout</p>
""")


# =========================================================
# 💳 FAKE PAYMENT (ЗАГЛУШКА)
# =========================================================
@app.route("/fake-pay")
def fake_pay():

    # симуляция подписки на 30 дней
    session["subscription_status"] = "active"
    session["subscription_end"] = time.time() + 30 * 24 * 60 * 60
    session["used"] = 0

    return redirect("/")


# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)