document.addEventListener("DOMContentLoaded", () => {
    const lookupBtn = document.getElementById("lookupBtn");
    const wordInput = document.getElementById("wordInput");
    const loader = document.getElementById("loader");
    const resultBox = document.getElementById("resultBox");

    const wordTitle = document.getElementById("wordTitle");
    const meaning = document.getElementById("meaning");
    const synonyms = document.getElementById("synonyms");
    const antonyms = document.getElementById("antonyms");

    lookupBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const word = wordInput.value.trim();
        if (!word) {
            alert("Please enter a word.");
            return;
        }

        loader.classList.remove("hidden");
        resultBox.classList.add("hidden");

        try {
            const response = await fetch("/lookup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ word })
            });

            const data = await response.json();
            loader.classList.add("hidden");

            if (data.error) {
                alert(data.error);
                return;
            }

            // Display result
            resultBox.classList.remove("hidden");
            wordTitle.textContent = data.word.toUpperCase();
            meaning.textContent = data.meaning || "No definition available.";
            synonyms.textContent = data.synonyms || "None";
            antonyms.textContent = data.antonyms || "None";

        } catch (err) {
            loader.classList.add("hidden");
            alert("⚠️ Network error. Please check your connection.");
        }
    });
});
