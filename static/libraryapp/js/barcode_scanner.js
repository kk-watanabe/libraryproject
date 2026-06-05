document.addEventListener("DOMContentLoaded", function () {

    const isbnInput = document.getElementById("id_isbn");

    if (!isbnInput) {
        return;
    }

    const button = document.createElement("button");

    button.type = "button";
    button.textContent = "📷 バーコードを読み取る";

    isbnInput.parentNode.appendChild(button);

    button.addEventListener("click", function () {
        alert("ボタンが押されました");
    });

});