from flask import Flask, request, session
import requests
import os
import re

app = Flask(__name__)
app.secret_key = "change_this_key"

FREE_LIMIT = 5
PRO_KEY = "1234"


# ======================
# AI REQUEST
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
        return f"Ошибка AI: {str(e)}"


# ======================
# PRO + LIMITS
# ======================
def is_pro():
    return session.get("pro", False)


def can_use():
    return is_pro() or session.get("used", 0) < FREE_LIMIT


def add_use():
    if not is_pro():
        session["used"] = session.get("used", 0) + 1


# ======================
# UI TEMPLATE
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
    background: linear-gradient(120deg, #f4f4f4, #e9eef7);
    margin:0;
}}

.container {{
    width:850px;
    margin:40px auto;
    background:white;
    padding:25px;
    border-radius:12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

nav a {{
    margin-right:12px;
    text-decoration:none;
    font-weight:bold;
    color:#2d6cdf;
}}

.hero {{
    background: linear-gradient(90deg, #111, #333);
    color:white;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
}}

input, textarea {{
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
    font-weight:bold;
}}

button:hover {{
    background:#1f4fbf;
}}

.loading {{
    display:none;
    margin-top:10px;
    color:#666;
    font-weight:bold;
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
<a href="/">Главная</a>
<a href="/wb">WB/Ozon</a>
<a href="/avito">Avito</a>
<a href="/pro">PRO</a>
</nav>

<div class="hero">
<h2>🚀 AI Product Builder</h2>
<p>FREE осталось: <b>{left}</b></p>
<p>{"💎 PRO ACTIVE" if pro else "FREE MODE"}</p>
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
    return page("Home", """
<h2>🔥 AI генератор карточек товаров</h2>
<p>Создавай продающие тексты за 10 секунд</p>
<a href="/wb"><button>Начать</button></a>
""")


# ======================
# WB / OZON
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        if not can_use():
            return page("LIMIT", "<h2>Лимит исчерпан</h2><a href='/pro'><button>Получить PRO</button></a>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты топовый маркетолог уровня Amazon.

Сделай продающую карточку товара:

1. Заголовок
2. Описание
3. Преимущества
4. Почему купить сейчас
5. Для кого

Товар: {product}
Характеристики: {features}

Стиль: продающий, эмоциональный, без воды
"""

        result = ask_ai(prompt)
        add_use()

    return page("WB", f"""
<h2>WB / Ozon генератор</h2>

<form method="POST" onsubmit="showLoading()">
<input name="product" placeholder="Название товара" required>
<textarea name="features" placeholder="Характеристики" required></textarea>

<button type="submit">Сгенерировать</button>

<div id="loading" class="loading">
⏳ Генерация продающего текста...
</div>
</form>

<div class="result">{result}</div>
""")


# ======================
# AVITO
# ======================
@app.route("/avito", methods=["GET", "POST"])
def avito():
    result = ""

    if request.method == "POST":
        if not can_use():
            return page("LIMIT", "<a href='/pro'><button>Получить PRO</button></a>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты эксперт по продажам на Avito.

Сделай объявление которое получает звонки:

1. Заголовок
2. Описание
3. Выгоды
4. Почему купить сейчас
5. Призыв к действию

Товар: {product}
Описание: {features}
"""

        result = ask_ai(prompt)
        add_use()

    return page("Avito", f"""
<h2>Avito генератор</h2>

<form method="POST" onsubmit="showLoading()">
<input name="product" placeholder="Название товара" required>
<textarea name="features" placeholder="Описание" required></textarea>

<button type="submit">Сгенерировать</button>

<div id="loading" class="loading">
⏳ Создаю продающее объявление...
</div>
</form>

<div class="result">{result}</div>
""")


# ======================
# PRO PAGE
# ======================
@app.route("/pro", methods=["GET", "POST"])
def pro():
    msg = ""

    if request.method == "POST":
        key = request.form.get("key")

        if key == PRO_KEY:
            session["pro"] = True
            msg = "💎 PRO активирован!"
        else:
            msg = "❌ Неверный ключ"

    return page("PRO", f"""
<h2>💎 PRO доступ</h2>

<p>Введите ключ для активации PRO</p>

<form method="POST">
<input name="key" placeholder="PRO ключ">
<button>Активировать</button>
</form>

<p>{msg}</p>
""")


if __name__ == "__main__":
    app.run(debug=True)