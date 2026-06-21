"""
🔥 AI SaaS PRODUCT BUILDER (FINAL LOGIC FIX)
- Free = только базовый режим (без выбора)
- Pro = Pro + Boost
- Жёсткая серверная защита
- Подписка через Stripe-ready система
"""

from flask import Flask, request, session, redirect
import requests
import os
import time
import re

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET"


# =========================================================
# ⚙️ НАСТРОЙКИ
# =========================================================
FREE_LIMIT = 5


# =========================================================
# 🧠 CLEAN OUTPUT (чтобы выглядело как продукт)
# =========================================================
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    return text


# =========================================================
# 🤖 AI REQUEST
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
# 💳 SUBSCRIPTION CHECK
# =========================================================
def is_sub_active():
    if session.get("subscription_status") != "active":
        return False

    if time.time() > session.get("subscription_end", 0):
        session["subscription_status"] = "expired"
        return False

    return True


def can_use():
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
    pro = is_sub_active()

    return f"""
<html>
<head>
<title>{title}</title>

<style>
body {{
    font-family: Arial;
    margin:0;
    background: linear-gradient(120deg,#f4f4f4,#e9eef7);
}}

.container {{
    width: 860px;
    margin: 40px auto;
    background: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
}}
</style>

</head>

<body>
<div class="container">

<div class="hero">
<h2>🚀 AI SaaS Builder</h2>
<p>{"💎 PRO ACTIVE" if pro else "🆓 FREE MODE"}</p>
<p>Free uses left: {max(FREE_LIMIT - used, 0)}</p>
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
<a href="/wb"><button>Start</button></a>
<a href="/subscribe"><button>Go Pro</button></a>
""")


# =========================================================
# 🆓 FREE / 💎 PRO LOGIC SPLIT (ГЛАВНОЕ ИЗМЕНЕНИЕ)
# =========================================================
@app.route("/wb", methods=["GET", "POST"])
def wb():

    result = ""

    # ================================
    # POST обработка
    # ================================
    if request.method == "POST":

        if not can_use():
            return page("BLOCKED", """
<h2>❌ Лимит исчерпан</h2>
<a href="/subscribe"><button>💎 Получить Pro</button></a>
""")

        product = request.form.get("product", "")
        features = request.form.get("features", "")
        mode = request.form.get("mode", "free")

        # =====================================================
        # 🔒 ЖЁСТКАЯ ЗАЩИТА (ВАЖНО!)
        # =====================================================
        if not is_sub_active():
            mode = "free"

        if mode == "boost" and not is_sub_active():
            mode = "free"

        # =====================================================
        # 🧠 PROMPT LOGIC
        # =====================================================
        if mode == "boost":
            prompt = f"""
Ты маркетолог уровня Apple.

🔥 Заголовок
✨ Эмоции
💎 Преимущества
⚡ Срочность
📈 Продажи

ТОВАР: {product}
{features}
"""

        elif mode == "pro":
            prompt = f"""
Профессиональный маркетинг.

ТОВАР: {product}
{features}
"""

        else:
            prompt = f"""
Обычное описание товара.

ТОВАР: {product}
{features}
"""

        result = ask_ai(prompt)
        add_use()

    # ================================
    # UI РАЗДЕЛЕНИЕ
    # ================================

    if is_sub_active():

        # 💎 PRO UI
        return page("PRO", f"""
<h2>💎 Pro Generator</h2>

<form method="POST">

<input name="product" placeholder="Название товара" required>
<textarea name="features" placeholder="Характеристики" required></textarea>

<select name="mode">
  <option value="pro">Pro</option>
  <option value="boost">Boost 🚀</option>
</select>

<button>Generate</button>

</form>

<div class="result">{result}</div>
""")

    else:

        # 🆓 FREE UI (БЕЗ ВЫБОРА РЕЖИМА!)
        return page("FREE", f"""
<h2>🆓 Free Generator</h2>

<form method="POST">

<input name="product" placeholder="Название товара" required>
<textarea name="features" placeholder="Описание" required></textarea>

<input type="hidden" name="mode" value="free">

<button>Generate (Free)</button>

</form>

<p>💡 В Free доступен только базовый режим</p>

<a href="/subscribe"><button>💎 Upgrade to Pro</button></a>

<div class="result">{result}</div>
""")


# =========================================================
# 💳 SUBSCRIBE PAGE (Stripe-ready)
# =========================================================
@app.route("/subscribe")
def subscribe():
    return page("Subscribe", """
<h2>💎 Pro Subscription</h2>

<p>Unlimited + Boost mode</p>

<h3>9.99€/month</h3>

<a href="/fake-pay"><button>Subscribe</button></a>
""")


# =========================================================
# 💳 FAKE PAYMENT (заменим на Stripe)
# =========================================================
@app.route("/fake-pay")
def fake_pay():

    session["subscription_status"] = "active"
    session["subscription_end"] = time.time() + 30 * 24 * 60 * 60
    session["used"] = 0

    return redirect("/")


# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)