from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

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
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()
        return clean_text(data["choices"][0]["message"]["content"])

    except Exception as e:
        return f"Ошибка: {str(e)}"


# ======================
# UI TEMPLATE (С МЕНЮ)
# ======================
def page(title, content):
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
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
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
                border: 1px solid #ddd;
                border-radius: 5px;
            }}

            button {{
                margin-top: 10px;
                padding: 10px 15px;
                background: #2d6cdf;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}

            button:hover {{
                background: #1f4fbf;
            }}

            pre {{
                white-space: pre-wrap;
                background: #f1f1f1;
                padding: 15px;
                margin-top: 15px;
                border-radius: 5px;
            }}

            #loading {{
                display: none;
                margin-top: 10px;
                color: gray;
            }}
        </style>

        <script>
            function showLoading() {{
                document.getElementById("loading").style.display = "block";
            }}

            function copyText() {{
                let text = document.getElementById("result").innerText;
                navigator.clipboard.writeText(text);
                alert("Скопировано!");
            }}
        </script>
    </head>

    <body>
        <div class="box">

            <nav>
                <a href="/">Главная</a>
                <a href="/wb">WB/Ozon</a>
                <a href="/avito">Авито</a>
                <a href="/names">Названия</a>
            </nav>

            <hr>

            <h2>{title}</h2>

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
    return page("AI Tools", "<p>Выбери инструмент выше 👆</p>")


# ======================
# WB / OZON
# ======================
@app.route("/wb", methods=["GET", "POST"])
def wb():
    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"Напиши продающее описание для WB/Ozon: {product}. {features}"
        result = ask_ai(prompt)

    return page("WB / Ozon Generator", f"""
        <form method="POST" onsubmit="showLoading()">
            <input name="product" placeholder="Название товара">
            <textarea name="features" placeholder="Характеристики"></textarea>
            <button>Сгенерировать</button>
            <div id="loading">⏳ Генерация...</div>
        </form>

        <button onclick="copyText()">📋 Копировать</button>

        <pre id="result">{result}</pre>
    """)


# ======================
# AVITO
# ======================
@app.route("/avito", methods=["GET", "POST"])
def avito():
    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")
        features = request.form.get("features", "")

        prompt = f"Сделай объявление Авито: {product}. {features}"
        result = ask_ai(prompt)

    return page("Avito Generator", f"""
        <form method="POST" onsubmit="showLoading()">
            <input name="product" placeholder="Название товара">
            <textarea name="features" placeholder="Описание"></textarea>
            <button>Сгенерировать</button>
            <div id="loading">⏳ Генерация...</div>
        </form>

        <button onclick="copyText()">📋 Копировать</button>

        <pre id="result">{result}</pre>
    """)


# ======================
# NAMES
# ======================
@app.route("/names", methods=["GET", "POST"])
def names():
    result = ""

    if request.method == "POST":
        product = request.form.get("product", "")

        prompt = f"Придумай 10 продающих названий для: {product}"
        result = ask_ai(prompt)

    return page("Name Generator", f"""
        <form method="POST" onsubmit="showLoading()">
            <input name="product" placeholder="Товар">
            <button>Сгенерировать</button>
            <div id="loading">⏳ Генерация...</div>
        </form>

        <button onclick="copyText()">📋 Копировать</button>

        <pre id="result">{result}</pre>
    """)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run()