from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)


# =========================
# CLEAN AI TEXT
# =========================
def clean_text(text):
    # убираем **жирный markdown**
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    return text


# =========================
# AI REQUEST
# =========================
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
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()
        return clean_text(data["choices"][0]["message"]["content"])

    except Exception as e:
        return f"Ошибка API: {str(e)}"


# =========================
# UI TEMPLATE
# =========================
def render(title, body, loading=False):
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial;
                background: #f4f4f4;
                margin: 0;
                padding: 0;
            }}

            .container {{
                width: 850px;
                margin: 50px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}

            input, textarea {{
                width: 100%;
                padding: 10px;
                margin-top: 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
                font-size: 14px;
            }}

            button {{
                margin-top: 15px;
                padding: 10px 20px;
                background: #2d6cdf;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}

            button:hover {{
                background: #1f4fbf;
            }}

            nav a {{
                margin-right: 10px;
                text-decoration: none;
                color: #2d6cdf;
            }}

            pre {{
                white-space: pre-wrap;
                background: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }}

            .loading {{
                display: none;
                margin-top: 10px;
                color: #666;
            }}
        </style>

        <script>
            function showLoading() {{
                document.getElementById("loading").style.display = "block";
            }}

            function copyText() {{
                const text = document.getElementById("result").innerText;
                navigator.clipboard.writeText(text);
                alert("Скопировано!");
            }}
        </script>
    </head>

    <body>
        <div class="container">

            <nav>
                <a href="/">Главная</a>
                <a href="/wb">WB/Ozon</a>
                <a href="/avito">Авито</a>
                <a href="/names">Названия</a>
            </nav>

            <hr>

            <h2>{title}</h2>

            {body}

        </div>
    </body>
    </html>
    """


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render("AI Tools", "<p>Выбери инструмент выше</p>")


# =========================
# WB / OZON
# =========================
@app.route("/wb", methods=["GET", "POST"])
def wb():

    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Напиши продающее описание для Ozon и Wildberries.

Товар: {product}
Характеристики: {features}
"""

        result = ask_ai(prompt)

    return render("WB / Ozon генератор", f"""

    <form method="POST" onsubmit="showLoading()">
        <input name="product" placeholder="Название товара">
        <textarea name="features" rows="8" placeholder="Характеристики"></textarea>

        <button type="submit">Сгенерировать</button>

        <div id="loading" class="loading">⏳ Генерация текста...</div>
    </form>

    <button onclick="copyText()">📋 Скопировать результат</button>

    <pre id="result">{result}</pre>

    """)


# =========================
# AVITO
# =========================
@app.route("/avito", methods=["GET", "POST"])
def avito():

    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"""
Напиши объявление для Авито.

Товар: {product}
Детали: {features}
"""

        result = ask_ai(prompt)

    return render("Авито генератор", f"""

    <form method="POST" onsubmit="showLoading()">
        <input name="product" placeholder="Название товара">
        <textarea name="features" rows="8" placeholder="Детали"></textarea>

        <button type="submit">Сгенерировать</button>

        <div id="loading" class="loading">⏳ Генерация текста...</div>
    </form>

    <button onclick="copyText()">📋 Скопировать результат</button>

    <pre id="result">{result}</pre>

    """)


# =========================
# NAMES
# =========================
@app.route("/names", methods=["GET", "POST"])
def names():

    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")

        prompt = f"Придумай 10 продающих названий для товара: {product}"

        result = ask_ai(prompt)

    return render("Названия товаров", f"""

    <form method="POST" onsubmit="showLoading()">
        <input name="product" placeholder="Товар">

        <button type="submit">Сгенерировать</button>

        <div id="loading" class="loading">⏳ Генерация текста...</div>
    </form>

    <button onclick="copyText()">📋 Скопировать результат</button>

    <pre id="result">{result}</pre>

    """)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)