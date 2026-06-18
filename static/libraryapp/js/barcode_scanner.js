document.addEventListener("DOMContentLoaded", function () {

    const isbnInput = document.getElementById("id_isbn");

    if (!isbnInput) {
        return;
    }

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "📷 バーコードを読み取る";
    button.style.marginLeft = "10px";
    button.style.marginRight = "10px";
    button.style.whiteSpace = "nowrap";

    isbnInput.parentNode.appendChild(button);

    const fetchButton = document.createElement("button");
    fetchButton.type = "button";
    fetchButton.textContent = "📚 書誌情報取得";
    button.style.marginRight = "10px";
    fetchButton.style.padding = "4px 8px";
    fetchButton.style.whiteSpace = "nowrap";

    isbnInput.parentNode.appendChild(fetchButton);

    fetchButton.addEventListener("click", async function () {

        const isbn = isbnInput.value;

        if (!isbn) {
            alert("ISBNを入力してください");
            return;
        }

        const response = await fetch(
            `/library/api/book-info/?isbn=${isbn}`
        );

        console.log(response.status);

        if (!response.ok) {
            alert("書誌情報を取得できませんでした");
            return;
        }

        const data = await response.json();

        document.getElementById("id_title").value =
            data.title || "";

        document.getElementById("id_author").value =
            data.author || "";

        document.getElementById("id_publisher").value =
            data.publisher || "";

        document.getElementById("id_publication_date").value =
            data.publication_date || "";

        document.getElementById("id_cover_url").value =
            data.cover_url || "";

    });

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
