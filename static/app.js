function copyResult() {
    const result = document.getElementById("resultText");
    if (!result) return;

    navigator.clipboard.writeText(result.innerText);

    const btn = document.querySelector(".copy-btn");
    if (btn) {
        const old = btn.innerText;
        btn.innerText = "✔ Скопировано";

        setTimeout(() => {
            btn.innerText = old;
        }, 1500);
    }
}


document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("generateForm");
    const btn = document.getElementById("generateBtn");
    const resultBox = document.querySelector(".result");

    if (!form || !btn) return;

    form.addEventListener("submit", () => {

        // 🔒 блок кнопки
        btn.disabled = true;
        btn.innerHTML = "⏳ AI генерирует...";

        // 💎 создаём fake loading эффект
        if (resultBox) {
            resultBox.style.opacity = "0.4";
            resultBox.style.filter = "blur(2px)";
        }

        // ⏱ имитация "мышления"
        setTimeout(() => {

            if (resultBox) {
                resultBox.style.opacity = "1";
                resultBox.style.filter = "none";
            }

            btn.innerHTML = "🚀 Сгенерировать";
            btn.disabled = false;

        }, 2500);
    });
});