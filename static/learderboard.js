// static/leaderboard.js

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".lb-unique-table");
    if (!table) return;

    // Highlight current user
    table.querySelectorAll("tr").forEach(row => {
        if (row.classList.contains("lb-unique-current")) {
            row.style.background = "#f0c040";
            row.style.fontWeight = "bold";
        }
    });
});
