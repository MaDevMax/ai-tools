from flask import Flask, request, session
import requests
import os
import re

app = Flask(__name__)
app.secret_key = "change_this_key"

FREE_LIMIT = 5

# простой PRO ключ (временно)
PRO_KEY = "1234"


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
        return f"Ошибка: {str(e)}"


# ======================
# LIMIT + PRO
# ======================
def is_pro():
    return session.get("pro", False)


def can_use():
    return is_pro() or session.get("used", 0) < FREE_LIMIT


def add_usage():
    if not is_pro():
        session["used"] = session.get("used", 0) + 1


# ======================
# UI
# ======================
def page(title, content):
    used = session.get("used", 0)
    pro = is_pro()

    left = "∞" if pro else max(FREE_LIMIT - used, 0)

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

.hero {{
    background:#111;
    color:white;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
}}

nav a {{
    margin-right:10px;
    text-decoration:none;
    font-weight:bold;
    color:#2d6cdf;
}}

.pro-box {{
    background: linear-gradient(90deg, #000, #333);
    color:white;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
}}

input, textarea {{
    width:100%;
    margin-top:10px;
    padding:10px;
}}

button {{
    background:#2d6cdf;
    color:white;
    border:none;
    padding:10px;
    margin-top:10px;
    cursor:pointer;
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
<a href="/pro">PRO</a>
</nav>

<div class="hero">
<h2>AI карточки товаров</h2>
<p>Бесплатно: {left} генераций</p>
<p>{"PRO активирован" if pro else "FREE режим"}</p>
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
    return page("AI Tool", """
<h3>Создавай продающие карточки товаров за 10 секунд</h3>
<a href="/wb"><button>Начать</button></a>
""")


# ======================
# WB
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        if not can_use():
            return page("LIMIT", "<h3>Лимит исчерпан</h3><a href='/pro'><button>Купить PRO</button></a>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"Напиши продающее описание WB/Ozon: {product} {features}"

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
        if not can_use():
            return page("LIMIT", "<a href='/pro'><button>Купить PRO</button></a>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"Сделай объявление Авито: {product} {features}"

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


# ======================
# PRO PAGE
# ======================
@app.route("/pro", methods=["GET", "POST"])
def pro():
    msg = ""

    if request.method == "POST":
        key = request.form.get("key", "")
        if key == PRO_KEY:
            session["pro"] = True
            msg = "PRO активирован!"
        else:
            msg = "Неверный ключ"

    return page("PRO", f"""
<h2>PRO доступ</h2>

<p>Введи ключ для активации PRO:</p>

<form method="POST">
<input name="key" placeholder="PRO ключ">
<button>Активировать</button>
</form>

<p>{msg}</p>
""")


if __name__ == "__main__":
    app.run(debug=True)