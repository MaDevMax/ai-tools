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
        return clean_text(r.json()["choices"][0]["message"]["content"])
    except Exception as e:
        return str(e)


# ======================
# LIMIT
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
    width:800px;
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

button {{
    background:#2d6cdf;
    color:white;
    border:none;
    padding:10px;
    cursor:pointer;
    margin-top:10px;
}}

textarea,input {{
    width:100%;
    margin-top:10px;
    padding:10px;
}}

pre {{
    background:#eee;
    padding:15px;
    white-space:pre-wrap;
}}
</style>
</head>

<body>
<div class="container">

<nav>
<a href="/">Главная</a>
<a href="/wb">WB/Ozon</a>
<a href="/avito">Avito</a>
</nav>

<div class="hero">
<h2>AI помогает продавать товары быстрее</h2>
<p>Создавай продающие карточки товаров за 10 секунд</p>
<p>Бесплатно: {FREE_LIMIT - used} генераций</p>
</div>

{content}

</div>
</body>
</html>
"""


# ======================
# HOME (ПРОДАЮЩАЯ)
# ======================
@app.route("/")
def home():
    return page("AI Sales Tool", """
<p><b>Что это:</b> AI пишет продающие карточки товаров</p>
<p><b>Для кого:</b> WB / Ozon / Avito продавцы</p>
<p><b>Результат:</b> больше продаж без копирайтера</p>

<a href="/wb"><button>Начать бесплатно</button></a>
""")


# ======================
# WB
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        if not check_limit():
            return page("LIMIT", "<h3>Лимит исчерпан</h3><p>PRO версия скоро</p>")

        p = request.form.get("product", "")
        f = request.form.get("features", "")

        prompt = f"""
Пиши ТОЛЬКО на русском.

Сделай продающее описание для WB/Ozon:

Товар: {p}
Характеристики: {f}
"""

        result = ask_ai(prompt)
        add_usage()

    return page("WB", f"""
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

        p = request.form.get("product", "")
        f = request.form.get("features", "")

        prompt = f"""
Пиши ТОЛЬКО на русском.

Сделай объявление Авито:

Товар: {p}
Описание: {f}
"""

        result = ask_ai(prompt)
        add_usage()

    return page("Avito", f"""
<form method="POST">
<input name="product">
<textarea name="features"></textarea>
<button>Сгенерировать</button>
</form>

<pre>{result}</pre>
""")


if __name__ == "__main__":
    app.run()