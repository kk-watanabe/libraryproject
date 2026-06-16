document.addEventListener("DOMContentLoaded", function () {

    const isbnInput = document.getElementById("id_isbn");

    if (!isbnInput) {
        return;
    }

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "📷 バーコードを読み取る";

    isbnInput.parentNode.appendChild(button);

    // カメラ表示領域
    const reader = document.createElement("div");
    reader.id = "reader";
    reader.style.width = "400px";
    reader.style.marginTop = "10px";

    isbnInput.parentNode.appendChild(reader);

    button.addEventListener("click", function () {

        const scanner = new Html5Qrcode("reader");

        scanner.start(
            { facingMode: "environment" },
            {
                fps: 10,
                qrbox: 250,
            },
            function(decodedText) {

                isbnInput.value = decodedText;

                scanner.stop();

            }
        );

    });

});