from flask import Flask, request, session
import requests
import os
import re

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me"

# ======================
# CONFIG
# ======================
FREE_LIMIT = 5

# ======================
# CLEAN TEXT
# ======================
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    return text


# ======================
# AI REQUEST
# ======================
def ask_ai(prompt):
    try:
        response = requests.post(
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

        data = response.json()
        return clean_text(data["choices"][0]["message"]["content"])

    except Exception as e:
        return f"Ошибка: {str(e)}"


# ======================
# LIMIT SYSTEM
# ======================
def check_limit():
    used = session.get("used", 0)
    if used >= FREE_LIMIT:
        return False
    return True


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
                background: #f5f5f5;
                margin: 0;
            }}

            .box {{
                width: 800px;
                margin: 40px auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
            }}

            nav a {{
                margin-right: 15px;
                text-decoration: none;
                color: #2d6cdf;
                font-weight: bold;
            }}

            input, textarea {{
                width: 100%;
                margin-top: 10px;
                padding: 10px;
            }}

            button {{
                margin-top: 10px;
                padding: 10px;
                background: #2d6cdf;
                color: white;
                border: none;
                cursor: pointer;
            }}

            .limit {{
                background: #eee;
                padding: 10px;
                margin-bottom: 10px;
            }}

            .pro {{
                background: black;
                color: white;
                padding: 10px;
                margin-top: 10px;
                display: inline-block;
                cursor: pointer;
            }}

            pre {{
                white-space: pre-wrap;
                background: #f1f1f1;
                padding: 15px;
                margin-top: 15px;
            }}
        </style>
    </head>

    <body>
        <div class="box">

            <nav>
                <a href="/">Главная</a>
                <a href="/wb">WB/Ozon</a>
                <a href="/avito">Авито</a>
                <a href="/names">Названия</a>
            </nav>

            <div class="limit">
                Бесплатные генерации: <b>{left}/{FREE_LIMIT}</b>
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
    return page("AI Tools", "<p>Выбери инструмент 👆</p>")


# ======================
# WB
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        if not check_limit():
            return page("LIMIT", "<h3>Лимит исчерпан</h3><div class='pro'>Купить PRO (скоро)</div>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты пишешь ТОЛЬКО на русском языке.

Напиши продающее описание WB/Ozon:

Товар: {product}
Характеристики: {features}
"""
        result = ask_ai(prompt)
        add_usage()

    return page("WB/Ozon", f"""
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
            return page("LIMIT", "<h3>Лимит исчерпан</h3><div class='pro'>Купить PRO (скоро)</div>")

        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Ты пишешь ТОЛЬКО на русском языке.

Сделай объявление Авито:

Товар: {product}
Описание: {features}
"""
        result = ask_ai(prompt)
        add_usage()

    return page("Avito", f"""
        <form method="POST">
            <input name="product" placeholder="Название товара">
            <textarea name="features" placeholder="Описание"></textarea>
            <button>Сгенерировать</button>
        </form>

        <pre>{result}</pre>
    """)


# ======================
# NAMES
# ======================
@app.route("/names", methods=["GET", "POST"])
def names():
    result = ""

    if request.method == "POST":
        if not check_limit():
            return page("LIMIT", "<h3>Лимит исчерпан</h3><div class='pro'>Купить PRO (скоро)</div>")

        product = request.form.get("product", "")

        prompt = f"""
Ты пишешь ТОЛЬКО на русском языке.

Придумай 10 названий:
{product}
"""
        result = ask_ai(prompt)
        add_usage()

    return page("Names", f"""
        <form method="POST">
            <input name="product" placeholder="Товар">
            <button>Сгенерировать</button>
        </form>

        <pre>{result}</pre>
    """)


if __name__ == "__main__":
    app.run()