from flask import Flask, request, session
import requests
import os
import re

app = Flask(__name__)
app.secret_key = "change_this_key"

FREE_LIMIT = 5


# ======================
# AI
# ======================
def clean_text(text):
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text)


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

        data = r.json()
        return clean_text(data["choices"][0]["message"]["content"])

    except Exception as e:
        return f"Ошибка: {str(e)}"


# ======================
# LIMITS
# ======================
def check_limit():
    return session.get("used", 0) < FREE_LIMIT


def add_usage():
    session["used"] = session.get("used", 0) + 1


# ======================
# UI
# ======================
def page(title, content):
    used = session.get("used", 0)
    left = max(FREE_LIMIT - used, 0)

    return f"""
<html>
<head>
<title>{title}</title>
<style>
body {{
    font-family: Arial;
    background:#f4f4f4;
    margin:0;
}}

.container {{
    width:850px;
    margin:40px auto;
    background:white;
    padding:20px;
    border-radius:10px;
}}

nav a {{
    margin-right:10px;
    text-decoration:none;
    font-weight:bold;
    color:#2d6cdf;
}}

.hero {{
    padding:20px;
    background:#111;
    color:white;
    border-radius:10px;
    margin-bottom:20px;
}}

.pro {{
    background: linear-gradient(90deg, #000, #333);
    color:white;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
}}

button {{
    background:#2d6cdf;
    color:white;
    border:none;
    padding:10px;
    cursor:pointer;
    margin-top:10px;
}}

input, textarea {{
    width:100%;
    margin-top:10px;
    padding:10px;
}}

pre {{
    background:#eee;
    padding:15px;
    white-space:pre-wrap;
    margin-top:15px;
}}
</style>
</head>

<body>
<div class="container">

<nav>
<a href="/">Главная</a>
<a href="/wb">WB / Ozon</a>
<a href="/avito">Avito</a>
</nav>

<div class="hero">
<h2>AI пишет продающие карточки товаров</h2>
<p>WB / Ozon / Avito — за 10 секунд</p>
<p>Бесплатно осталось: <b>{left}</b> генераций</p>
</div>

<div class="pro">
<h3>🔥 PRO версия</h3>
<p>• Без лимитов</p>
<p>• Более сильные продающие тексты</p>
<p>• Быстрее генерация</p>
<p><b>299₽ / месяц (скоро)</b></p>
</div>

{content}

</div>
</body>
</html>
"""


# ======================
# HOME
# ======================
@app.route("/")
def home():
    return page("AI Sales Tool", """
<h3>Что это:</h3>
<p>AI создаёт продающие описания товаров</p>

<h3>Для кого:</h3>
<p>WB / Ozon / Avito продавцы</p>

<h3>Результат:</h3>
<p>Больше продаж без копирайтера</p>

<a href="/wb"><button>Начать бесплатно</button></a>
""")


# ======================
# WB / OZON
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        if not check_limit():
            return page("LIMIT", "<h3>Лимит исчерпан</h3><p>PRO версия скоро</p>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты маркетинговый копирайтер.

Напиши продающее описание для WB/Ozon.

Товар: {product}
Характеристики: {features}

Стиль: продающий, простой, без воды.
"""

        result = ask_ai(prompt)
        add_usage()

    return page("WB/Ozon", f"""
<h2>WB / Ozon генератор</h2>

<form method="POST">
<input name="product" placeholder="Название товара">
<textarea name="features" placeholder="Характеристики"></textarea>
<button>Сгенерировать</button>
</form>

<pre>{result}</pre>
""")


# ======================
# AVITO
# ======================
@app.route("/avito", methods=["GET", "POST"])
def avito():
    result = ""

    if request.method == "POST":
        if not check_limit():
            return page("LIMIT", "<h3>Лимит исчерпан</h3>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты пишешь объявления для Авито.

Товар: {product}
Описание: {features}

Сделай коротко, продающе, чтобы звонили.
"""

        result = ask_ai(prompt)
        add_usage()

    return page("Avito", f"""
<h2>Avito генератор</h2>

<form method="POST">
<input name="product" placeholder="Название товара">
<textarea name="features" placeholder="Описание"></textarea>
<button>Сгенерировать</button>
</form>

<pre>{result}</pre>
""")


if __name__ == "__main__":
    app.run(debug=True)